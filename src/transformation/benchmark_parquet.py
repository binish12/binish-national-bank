import os
import time

import numpy as np
import pandas as pd

ROW_COUNT = 500_000
EXTRA_COLUMNS = 15
RUNS = 5
BENCH_DIR = "data/benchmark"
CSV_PATH = os.path.join(BENCH_DIR, "transactions.csv")
PARQUET_PATH = os.path.join(BENCH_DIR, "transactions.parquet")

os.makedirs(BENCH_DIR, exist_ok=True)

seconds_in_180_days = 180 * 24 * 3600
df = pd.DataFrame({
    "transaction_id": np.arange(ROW_COUNT),
    "account_id": np.random.randint(1, 1000, size=ROW_COUNT),
    "amount": np.round(np.random.uniform(5, 3000, size=ROW_COUNT), 2),
    "transaction_type": np.random.choice(
        ["purchase", "withdrawal", "deposit", "transfer"], size=ROW_COUNT
    ),
    "transaction_timestamp": pd.Timestamp("2026-01-01")
    + pd.to_timedelta(np.random.randint(0, seconds_in_180_days,
                      size=ROW_COUNT), unit="s"),
})

# Real tables are wide, so add extra numeric columns to be more realistic
for i in range(EXTRA_COLUMNS):
    df[f"extra_{i}"] = np.round(np.random.uniform(0, 1000, size=ROW_COUNT), 2)

df.to_csv(CSV_PATH, index=False)
df.to_parquet(PARQUET_PATH, index=False)


def best_time(fn, runs=RUNS):
    """Run fn several times and return the fastest run, so one-time startup cost is ignored."""
    times = []
    for _ in range(runs):
        start = time.time()
        fn()
        times.append(time.time() - start)
    return min(times)


csv_read = best_time(lambda: pd.read_csv(CSV_PATH, usecols=["amount"]))
parquet_read = best_time(lambda: pd.read_parquet(
    PARQUET_PATH, columns=["amount"]))

csv_size = os.path.getsize(CSV_PATH)
parquet_size = os.path.getsize(PARQUET_PATH)

print(f"Columns: {len(df.columns)}")
print(f"CSV size:     {csv_size / 1_000_000:.1f} MB")
print(f"Parquet size: {parquet_size / 1_000_000:.1f} MB")
print(f"Parquet is {csv_size / parquet_size:.1f}x smaller")
print()
print(f"Read ONE column from CSV (best of {RUNS}):     {csv_read:.4f} s")
print(f"Read ONE column from Parquet (best of {RUNS}): {parquet_read:.4f} s")
print(f"Parquet was {csv_read / parquet_read:.1f}x faster")
