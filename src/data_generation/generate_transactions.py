import random
from datetime import datetime, timedelta
from src.utilities.db import get_connection

TRANSACTION_TYPES = ["purchase", "withdrawal", "deposit", "transfer"]


def get_existing_ids(cur, table: str, id_column: str) -> list[int]:
    cur.execute(f"SELECT {id_column} FROM {table}")
    return [row[0] for row in cur.fetchall()]


def random_timestamp(days_back: int = 180) -> datetime:
    seconds_back = random.randint(0, days_back * 24 * 60 * 60)
    return datetime.now() - timedelta(seconds=seconds_back)


def generate_transactions(
    account_ids: list[int],
    card_ids: list[int],
    merchant_ids: list[int],
    count: int,
) -> list[tuple]:
    transactions = []
    for _ in range(count):
        account_id = random.choice(account_ids)
        transaction_type = random.choice(TRANSACTION_TYPES)

        # Card and merchant are optional — transfers/withdrawals often have neither
        if transaction_type == "purchase":
            card_id = random.choice(card_ids)
            merchant_id = random.choice(merchant_ids)
        else:
            card_id = random.choice(
                card_ids) if random.random() < 0.3 else None
            merchant_id = None

        amount = round(random.uniform(5, 3000), 2)
        timestamp = random_timestamp()

        transactions.append((account_id, card_id, merchant_id,
                            amount, transaction_type, timestamp))
    return transactions


def insert_transactions(cur, transactions: list[tuple]):
    cur.executemany(
        """INSERT INTO transactions
           (account_id, card_id, merchant_id, amount, transaction_type, transaction_timestamp)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        transactions,
    )


def main():
    conn = get_connection()
    cur = conn.cursor()

    account_ids = get_existing_ids(cur, "accounts", "account_id")
    card_ids = get_existing_ids(cur, "cards", "card_id")
    merchant_ids = get_existing_ids(cur, "merchants", "merchant_id")

    if not account_ids or not card_ids or not merchant_ids:
        print("Missing accounts, cards, or merchants — generate those first.")
        cur.close()
        conn.close()
        return

    while True:
        raw = input("How many transactions to generate? ")
        if raw.isdigit() and int(raw) > 0:
            count = int(raw)
            break
        print("Enter a positive whole number.")

    transactions = generate_transactions(
        account_ids, card_ids, merchant_ids, count)
    insert_transactions(cur, transactions)
    conn.commit()
    print(f"Inserted {count} transactions.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
