import re

import pandas as pd

VALID_TRANSACTION_TYPES = {"purchase", "withdrawal", "deposit", "transfer"}


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


def validate_and_split(df: pd.DataFrame):
    """Dedupe, clean, validate.
    Returns (clean_df, quarantine_df, original_count, after_dedup_count)."""
    original_count = len(df)
    df = df.drop_duplicates().copy()
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
    return clean_df, quarantine_df, original_count, after_dedup_count
