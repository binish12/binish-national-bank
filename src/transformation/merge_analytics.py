import pandas as pd
from src.utilities.db import get_connection


def load_table(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


transactions = load_table("transactions")
accounts = load_table("accounts").rename(columns={"status": "account_status"})
customers = load_table("customers")

merged = transactions.merge(accounts, on="account_id", how="left")
merged = merged.merge(customers, on="customer_id", how="left")

print(merged.shape)
print(merged.columns.tolist())


# Aggregation 1: total spend per customer
spend_per_customer = (
    merged.groupby(["customer_id", "first_name", "last_name"])["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

# Aggregation 2: count and average amount per transaction type
type_summary = (
    merged.groupby("transaction_type")["amount"]
    .agg(["count", "mean"])
    .reset_index()
)

# Aggregation 3: total transaction volume per branch
volume_per_branch = (
    merged.groupby("branch_id")["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

print("\nTop customers by spend:")
print(spend_per_customer.head())

print("\nTransaction type summary:")
print(type_summary)

print("\nVolume per branch:")
print(volume_per_branch)
