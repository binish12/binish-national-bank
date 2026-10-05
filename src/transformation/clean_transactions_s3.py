import io
import logging
from datetime import datetime

import pandas as pd

from src.transformation.cleaning_rules import validate_and_split
from src.utilities.s3 import get_s3_client, get_bucket_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

SOURCE_PREFIX = "raw/transactions_incremental/"
CLEAN_PREFIX = "processed/transactions_clean/"
QUARANTINE_PREFIX = "processed/transactions_quarantine/"


def load_incremental_data_from_s3(s3, bucket) -> pd.DataFrame:
    response = s3.list_objects_v2(Bucket=bucket, Prefix=SOURCE_PREFIX)
    keys = [obj["Key"] for obj in response.get("Contents", [])]

    dataframes = []
    for key in keys:
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)


def upload_dataframe_to_s3_parquet(s3, bucket, df, key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def process_transactions_s3():
    s3 = get_s3_client()
    bucket = get_bucket_name()

    df = load_incremental_data_from_s3(s3, bucket)
    clean_df, quarantine_df, original_count, after_dedup_count = validate_and_split(
        df)

    # Cleaning left timestamps as ISO strings. Convert back to real datetimes
    # so Parquet stores a true timestamp type instead of text.
    clean_df = clean_df.copy()
    clean_df["transaction_timestamp"] = pd.to_datetime(
        clean_df["transaction_timestamp"])
    quarantine_df = quarantine_df.copy()
    quarantine_df["transaction_timestamp"] = pd.to_datetime(
        quarantine_df["transaction_timestamp"], errors="coerce"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_key = f"{CLEAN_PREFIX}transactions_clean_{timestamp}.parquet"
    quarantine_key = f"{QUARANTINE_PREFIX}transactions_quarantine_{timestamp}.parquet"

    upload_dataframe_to_s3_parquet(s3, bucket, clean_df, clean_key)
    upload_dataframe_to_s3_parquet(s3, bucket, quarantine_df, quarantine_key)

    logger.info(f"Original rows: {original_count}")
    logger.info(f"After removing exact duplicates: {after_dedup_count}")
    logger.info(f"Clean rows: {len(clean_df)} -> s3://{bucket}/{clean_key}")
    logger.info(
        f"Quarantined rows: {len(quarantine_df)} -> s3://{bucket}/{quarantine_key}")


if __name__ == "__main__":
    process_transactions_s3()
