import glob
import os
from datetime import datetime

import pandas as pd

from src.transformation.cleaning_rules import validate_and_split

SOURCE_DIR = "data/raw/transactions_incremental"
CLEAN_DIR = "data/processed/transactions_clean"
QUARANTINE_DIR = "data/processed/transactions_quarantine"


def load_local_data() -> pd.DataFrame:
    files = glob.glob(f"{SOURCE_DIR}/*.csv")
    dataframes = [pd.read_csv(f) for f in files]
    return pd.concat(dataframes, ignore_index=True)


def process_transactions():
    df = load_local_data()
    clean_df, quarantine_df, original_count, after_dedup_count = validate_and_split(
        df)

    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    clean_df.to_csv(os.path.join(
        CLEAN_DIR, f"transactions_clean_{timestamp}.csv"), index=False)
    quarantine_df.to_csv(
        os.path.join(QUARANTINE_DIR, f"transactions_quarantine_{timestamp}.csv"), index=False
    )

    print(f"Original rows: {original_count}")
    print(f"After removing exact duplicates: {after_dedup_count}")
    print(f"Clean rows: {len(clean_df)}")
    print(f"Quarantined rows: {len(quarantine_df)}")
    print("\nQuarantine reasons breakdown:")
    print(quarantine_df["rejection_reason"].value_counts())


if __name__ == "__main__":
    process_transactions()
