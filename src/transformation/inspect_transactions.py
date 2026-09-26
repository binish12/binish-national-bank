import glob
import pandas as pd

RAW_DIR = "data/raw/transactions_incremental"


def load_all_transaction_files() -> pd.DataFrame:
    """Load and combine every CSV in the incremental transactions folder."""
    files = glob.glob(f"{RAW_DIR}/*.csv")
    dataframes = [pd.read_csv(f) for f in files]
    return pd.concat(dataframes, ignore_index=True)


def main():
    df = load_all_transaction_files()
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nNull counts:\n{df.isna().sum()}")


if __name__ == "__main__":
    main()
