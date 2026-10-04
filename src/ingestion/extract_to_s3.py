import csv
import io
import logging

from src.utilities.db import get_connection
from src.utilities.s3 import get_s3_client, get_bucket_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def extract_table_to_s3(table_name: str):
    conn = get_connection()
    cur = conn.cursor()

    logger.info(f"Extracting full table: {table_name}")
    cur.execute(f"SELECT * FROM {table_name}")

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Build the CSV content entirely in memory, no local file
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    writer.writerows(rows)

    s3 = get_s3_client()
    bucket = get_bucket_name()
    key = f"raw/{table_name}/{table_name}_latest.csv"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
    )

    logger.info(f"Wrote {len(rows)} rows to s3://{bucket}/{key}")


def main():
    tables = ["branches", "customers", "accounts",
              "cards", "merchants", "transactions"]
    for table in tables:
        extract_table_to_s3(table)


if __name__ == "__main__":
    main()
