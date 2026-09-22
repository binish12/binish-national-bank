from faker import Faker
from src.utilities.db import get_connection

fake = Faker()


def generate_customers(count: int) -> list[tuple]:
    customers = []
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        phone = fake.numerify("(###) ###-####")
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
        customers.append((first_name, last_name, email, phone, dob))
    return customers


def insert_customers(cur, customers: list[tuple]):
    cur.executemany(
        """INSERT INTO customers (first_name, last_name, email, phone, date_of_birth)
           VALUES (%s, %s, %s, %s, %s)""",
        customers,
    )


def main():
    while True:
        raw = input("How many customers to generate? ")
        if raw.isdigit() and int(raw) > 0:
            count = int(raw)
            break
        print("Enter a positive whole number.")

    customers = generate_customers(count)

    conn = get_connection()
    cur = conn.cursor()
    insert_customers(cur, customers)
    conn.commit()
    print(f"Inserted {count} customers.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
