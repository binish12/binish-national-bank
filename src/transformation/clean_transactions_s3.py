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


def upload_partitioned_parquet(s3, bucket, df, prefix, batch_id):
    df = df.copy()
    df["year"] = df["transaction_timestamp"].dt.year
    df["month"] = df["transaction_timestamp"].dt.month

    for (year, month), part_df in df.groupby(["year", "month"]):
        key = f"{prefix}year={year}/month={month:02d}/part_{batch_id}.parquet"
        part_df = part_df.drop(columns=["year", "month"])
        upload_dataframe_to_s3_parquet(s3, bucket, part_df, key)
        logger.info(f"Wrote {len(part_df)} rows to s3://{bucket}/{key}")


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

    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    quarantine_key = f"{QUARANTINE_PREFIX}transactions_quarantine_{batch_id}.parquet"

    upload_partitioned_parquet(s3, bucket, clean_df, CLEAN_PREFIX, batch_id)
    upload_dataframe_to_s3_parquet(s3, bucket, quarantine_df, quarantine_key)
    logger.info(f"Original rows: {original_count}")
    logger.info(f"After removing exact duplicates: {after_dedup_count}")
    logger.info(
        f"Clean rows: {len(clean_df)} (partitioned under s3://{bucket}/{CLEAN_PREFIX})")
    logger.info(
        f"Quarantined rows: {len(quarantine_df)} -> s3://{bucket}/{quarantine_key}")


if __name__ == "__main__":
    process_transactions_s3()
