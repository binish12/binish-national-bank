import random
from src.utilities.db import get_connection

ACCOUNT_TYPES = ["checking", "savings", "business"]


def get_existing_ids(cur, table: str, id_column: str) -> list[int]:
    cur.execute(f"SELECT {id_column} FROM {table}")
    return [row[0] for row in cur.fetchall()]


def generate_accounts(customer_ids: list[int], branch_ids: list[int], count: int) -> list[tuple]:
    accounts = []
    for _ in range(count):
        customer_id = random.choice(customer_ids)
        branch_id = random.choice(branch_ids)
        account_type = random.choice(ACCOUNT_TYPES)
        balance = round(random.uniform(0, 50000), 2)
        accounts.append((customer_id, branch_id, account_type, balance))
    return accounts


def insert_accounts(cur, accounts: list[tuple]):
    cur.executemany(
        """INSERT INTO accounts (customer_id, branch_id, account_type, balance)
           VALUES (%s, %s, %s, %s)""",
        accounts,
    )


def main():
    conn = get_connection()
    cur = conn.cursor()

    customer_ids = get_existing_ids(cur, "customers", "customer_id")
    branch_ids = get_existing_ids(cur, "branches", "branch_id")

    if not customer_ids or not branch_ids:
        print("No customers or branches found — generate those first.")
        cur.close()
        conn.close()
        return

    while True:
        raw = input("How many accounts to generate? ")
        if raw.isdigit() and int(raw) > 0:
            count = int(raw)
            break
        print("Enter a positive whole number.")

    accounts = generate_accounts(customer_ids, branch_ids, count)
    insert_accounts(cur, accounts)
    conn.commit()
    print(f"Inserted {count} accounts.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
