import glob
import os
import re
from datetime import datetime

import pandas as pd

DIRTY_DIR = "data/raw/transactions_incremental"
CLEAN_DIR = "data/processed/transactions_clean"
QUARANTINE_DIR = "data/processed/transactions_quarantine"

VALID_TRANSACTION_TYPES = {"purchase", "withdrawal", "deposit", "transfer"}


def load_dirty_data() -> pd.DataFrame:
    files = glob.glob(f"{DIRTY_DIR}/*.csv")
    dataframes = [pd.read_csv(f) for f in files]
    return pd.concat(dataframes, ignore_index=True)


def clean_amount(value):
    """Strip $ and commas from a currency string, return a float, or None if unusable."""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d.\-]", "", value)
        if cleaned == "":
            return None
        return float(cleaned)
    return float(value)


def clean_transaction_type(value):
    """Normalize casing/whitespace; return None if it's not a recognized type."""
    if pd.isna(value):
        return None
    normalized = str(value).strip().lower()
    if normalized in VALID_TRANSACTION_TYPES:
        return normalized
    return None


def clean_timestamp(value):
    """Parse any reasonable date format into a standard ISO string, or None if unparseable."""
    try:
        return pd.to_datetime(value).isoformat()
    except Exception:
        return None


def process_transactions():
    df = load_dirty_data()
    original_count = len(df)

    # Step 1: remove exact duplicates
    df = df.drop_duplicates()
    after_dedup_count = len(df)

    # Step 2: apply cleaning functions
    df["amount"] = df["amount"].apply(clean_amount)
    df["transaction_type"] = df["transaction_type"].apply(
        clean_transaction_type)
    df["transaction_timestamp"] = df["transaction_timestamp"].apply(
        clean_timestamp)

    # Step 3: build rejection reasons per row
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

    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    clean_path = os.path.join(CLEAN_DIR, f"transactions_clean_{timestamp}.csv")
    quarantine_path = os.path.join(
        QUARANTINE_DIR, f"transactions_quarantine_{timestamp}.csv")

    clean_df.to_csv(clean_path, index=False)
    quarantine_df.to_csv(quarantine_path, index=False)

    print(f"Original rows: {original_count}")
    print(f"After removing exact duplicates: {after_dedup_count}")
    print(f"Clean rows: {len(clean_df)}")
    print(f"Quarantined rows: {len(quarantine_df)}")
    print(f"\nQuarantine reasons breakdown:")
    print(quarantine_df["rejection_reason"].value_counts())


if __name__ == "__main__":
    process_transactions()
