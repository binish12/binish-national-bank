import time
import numpy as np
import pandas as pd

ROW_COUNT = 500_000

# Generate random amounts directly with NumPy — no database needed for this test
amounts = np.random.uniform(5, 3000, size=ROW_COUNT)
df = pd.DataFrame({"amount": amounts})


def calculate_fee_slow(amount):
    return amount * 0.05


# Approach 1: row-by-row loop via .apply()
start = time.time()
df["fee_slow"] = df["amount"].apply(calculate_fee_slow)
slow_duration = time.time() - start

# Approach 2: vectorized — the whole column multiplied at once
start = time.time()
df["fee_fast"] = df["amount"] * 0.05
fast_duration = time.time() - start

print(f"Row count: {ROW_COUNT:,}")
print(f".apply() (row-by-row) took: {slow_duration:.4f} seconds")
print(f"Vectorized (whole column at once) took: {fast_duration:.4f} seconds")
print(f"Vectorized was {slow_duration / fast_duration:.0f}x faster")
