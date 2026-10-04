import csv
import io
import json
import logging
from datetime import datetime

from src.utilities.db import get_connection
from src.utilities.s3 import get_s3_client, get_bucket_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

WATERMARK_KEY = "state/transactions_watermark.json"


def load_watermark(s3, bucket) -> str:
    try:
        response = s3.get_object(Bucket=bucket, Key=WATERMARK_KEY)
        state = json.loads(response["Body"].read())
        return state["last_watermark"]
    except s3.exceptions.NoSuchKey:
        return "1970-01-01 00:00:00"


def save_watermark(s3, bucket, new_watermark):
    body = json.dumps({"last_watermark": str(new_watermark)})
    s3.put_object(Bucket=bucket, Key=WATERMARK_KEY, Body=body)


def extract_transactions_incremental_s3():
    s3 = get_s3_client()
    bucket = get_bucket_name()

    watermark = load_watermark(s3, bucket)
    logger.info(f"Current watermark: {watermark}")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM transactions
        WHERE transaction_timestamp > %s
        ORDER BY transaction_timestamp
        """,
        (watermark,),
    )

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        logger.info(
            "No new transactions since last watermark. Nothing to extract.")
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    writer.writerows(rows)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key = f"raw/transactions_incremental/transactions_{timestamp}.csv"

    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    logger.info(f"Wrote {len(rows)} new rows to s3://{bucket}/{key}")

    ts_index = columns.index("transaction_timestamp")
    new_watermark = max(row[ts_index] for row in rows)
    save_watermark(s3, bucket, new_watermark)
    logger.info(f"Updated watermark to: {new_watermark}")


if __name__ == "__main__":
    extract_transactions_incremental_s3()
