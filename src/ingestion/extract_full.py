import csv
import logging
import os
from datetime import datetime

from src.utilities.db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = "data/raw"


def extract_table_full(table_name: str) -> str:
    """Extract every row from `table_name` into a timestamped CSV. Returns the file path."""
    conn = get_connection()
    cur = conn.cursor()

    logger.info(f"Extracting full table: {table_name}")
    cur.execute(f"SELECT * FROM {table_name}")

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    table_dir = os.path.join(RAW_DATA_DIR, table_name)
    os.makedirs(table_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(table_dir, f"{table_name}_{timestamp}.csv")

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    logger.info(f"Wrote {len(rows)} rows to {file_path}")
    return file_path


def main():
    tables = ["branches", "customers", "accounts",
              "cards", "merchants", "transactions"]
    for table in tables:
        extract_table_full(table)


if __name__ == "__main__":
    main()
