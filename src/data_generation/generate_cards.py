import random
from src.utilities.db import get_connection

CARD_TYPES = ["debit", "credit"]


def get_existing_ids(cur, table: str, id_column: str) -> list[int]:
    cur.execute(f"SELECT {id_column} FROM {table}")
    return [row[0] for row in cur.fetchall()]


def generate_card_number() -> str:
    return " ".join(str(random.randint(1000, 9999)) for _ in range(4))


def generate_cards(account_ids: list[int], count: int) -> list[tuple]:
    cards = []
    for _ in range(count):
        account_id = random.choice(account_ids)
        card_number = generate_card_number()
        card_type = random.choice(CARD_TYPES)
        expiry_year = random.randint(2026, 2031)
        expiry_month = random.randint(1, 12)
        expiry_date = f"{expiry_year}-{expiry_month:02d}-01"
        cards.append((account_id, card_number, card_type, expiry_date))
    return cards


def insert_cards(cur, cards: list[tuple]):
    cur.executemany(
        """INSERT INTO cards (account_id, card_number, card_type, expiry_date)
           VALUES (%s, %s, %s, %s)""",
        cards,
    )


def main():
    conn = get_connection()
    cur = conn.cursor()

    account_ids = get_existing_ids(cur, "accounts", "account_id")

    if not account_ids:
        print("No accounts found — generate those first.")
        cur.close()
        conn.close()
        return

    while True:
        raw = input("How many cards to generate? ")
        if raw.isdigit() and int(raw) > 0:
            count = int(raw)
            break
        print("Enter a positive whole number.")

    cards = generate_cards(account_ids, count)
    insert_cards(cur, cards)
    conn.commit()
    print(f"Inserted {count} cards.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
