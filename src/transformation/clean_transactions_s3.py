import io
import logging
import re
from datetime import datetime

import pandas as pd

from src.utilities.s3 import get_s3_client, get_bucket_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

SOURCE_PREFIX = "raw/transactions_incremental/"
CLEAN_PREFIX = "processed/transactions_clean/"
QUARANTINE_PREFIX = "processed/transactions_quarantine/"

VALID_TRANSACTION_TYPES = {"purchase", "withdrawal", "deposit", "transfer"}


def load_incremental_data_from_s3(s3, bucket) -> pd.DataFrame:
    response = s3.list_objects_v2(Bucket=bucket, Prefix=SOURCE_PREFIX)
    keys = [obj["Key"] for obj in response.get("Contents", [])]

    dataframes = []
    for key in keys:
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)


def clean_amount(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d.\-]", "", value)
        if cleaned == "":
            return None
        return float(cleaned)
    return float(value)


def clean_transaction_type(value):
    if pd.isna(value):
        return None
    normalized = str(value).strip().lower()
    if normalized in VALID_TRANSACTION_TYPES:
        return normalized
    return None


def clean_timestamp(value):
    try:
        return pd.to_datetime(value).isoformat()
    except Exception:
        return None


def upload_dataframe_to_s3(s3, bucket, df, key):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def process_transactions_s3():
    s3 = get_s3_client()
    bucket = get_bucket_name()

    df = load_incremental_data_from_s3(s3, bucket)
    original_count = len(df)

    df = df.drop_duplicates()
    after_dedup_count = len(df)

    df["amount"] = df["amount"].apply(clean_amount)
    df["transaction_type"] = df["transaction_type"].apply(
        clean_transaction_type)
    df["transaction_timestamp"] = df["transaction_timestamp"].apply(
        clean_timestamp)

    reasons = []
    for _, row in df.iterrows():
        row_reasons = []
        if pd.isna(row["amount"]):
            row_reasons.append("missing_or_invalid_amount")
        elif row["amount"] < 0:
            row_reasons.append("negative_amount")
        if pd.isna(row["transaction_type"]):
            row_reasons.append("invalid_transaction_type")
        if pd.isna(row["transaction_timestamp"]):
            row_reasons.append("invalid_timestamp")
        reasons.append(", ".join(row_reasons) if row_reasons else None)

    df["rejection_reason"] = reasons

    clean_df = df[df["rejection_reason"].isna()].drop(
        columns=["rejection_reason"])
    quarantine_df = df[df["rejection_reason"].notna()]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_key = f"{CLEAN_PREFIX}transactions_clean_{timestamp}.csv"
    quarantine_key = f"{QUARANTINE_PREFIX}transactions_quarantine_{timestamp}.csv"

    upload_dataframe_to_s3(s3, bucket, clean_df, clean_key)
    upload_dataframe_to_s3(s3, bucket, quarantine_df, quarantine_key)

    logger.info(f"Original rows: {original_count}")
    logger.info(f"After removing exact duplicates: {after_dedup_count}")
    logger.info(f"Clean rows: {len(clean_df)} -> s3://{bucket}/{clean_key}")
    logger.info(
        f"Quarantined rows: {len(quarantine_df)} -> s3://{bucket}/{quarantine_key}")


if __name__ == "__main__":
    process_transactions_s3()
