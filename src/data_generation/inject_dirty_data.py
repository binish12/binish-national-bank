import glob
import os
import random
from datetime import datetime

import pandas as pd

RAW_DIR = "data/raw/transactions_incremental"
DIRTY_DIR = "data/raw/transactions_dirty"


def load_all_transaction_files() -> pd.DataFrame:
    files = glob.glob(f"{RAW_DIR}/*.csv")
    dataframes = [pd.read_csv(f) for f in files]
    return pd.concat(dataframes, ignore_index=True)


def inject_dirty_data(df: pd.DataFrame, n: int) -> pd.DataFrame:
    df = df.copy()
    n = min(n, len(df))

    # 1. Duplicate rows — simulates a resend/replay
    duplicates = df.sample(n=n).copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # 2. Missing required field
    missing_idx = df.sample(n=n).index
    df.loc[missing_idx, "amount"] = None

    # 3. Inconsistent format — currency string instead of a number
    bad_format_idx = df.sample(n=n).index
    df.loc[bad_format_idx, "amount"] = df.loc[bad_format_idx, "amount"].apply(
        lambda x: f"${x:.2f}" if pd.notna(x) else x
    )

    # 4. Inconsistent date format
    bad_date_idx = df.sample(n=n).index

    def reformat_date(ts):
        try:
            return pd.to_datetime(ts).strftime("%m/%d/%Y")
        except Exception:
            return ts
    df.loc[bad_date_idx, "transaction_timestamp"] = df.loc[bad_date_idx,
                                                           "transaction_timestamp"].apply(reformat_date)

    # 5. Inconsistent categorical values
    bad_type_idx = df.sample(n=n).index
    messy_types = ["PURCHASE", "Purchase ", "withdrawl", "unknown"]
    df.loc[bad_type_idx, "transaction_type"] = [
        random.choice(messy_types) for _ in bad_type_idx]

    # 6. Invalid values — negative amounts
    negative_idx = df.sample(n=n).index
    df.loc[negative_idx, "amount"] = df.loc[negative_idx, "amount"].apply(
        lambda x: -
        abs(float(x)) if pd.notna(x) and not isinstance(x, str) else x
    )

    # shuffle, like a real incoming file
    return df.sample(frac=1).reset_index(drop=True)


def main():
    df = load_all_transaction_files()

    while True:
        raw = input("How many records to corrupt per issue type? ")
        if raw.isdigit() and int(raw) > 0:
            n = int(raw)
            break
        print("Enter a positive whole number.")

    dirty_df = inject_dirty_data(df, n)

    os.makedirs(DIRTY_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(DIRTY_DIR, f"transactions_dirty_{timestamp}.csv")
    dirty_df.to_csv(file_path, index=False)
    print(f"Wrote {len(dirty_df)} rows to {file_path}")


if __name__ == "__main__":
    main()
