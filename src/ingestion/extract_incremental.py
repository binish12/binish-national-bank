import csv
import json
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
STATE_DIR = "data/state"
STATE_FILE = os.path.join(STATE_DIR, "transactions_watermark.json")


def load_watermark() -> str:
    """Return the last saved watermark, or a very old default if this is the first run."""
    if not os.path.exists(STATE_FILE):
        return "1970-01-01 00:00:00"

    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    return state["last_watermark"]


def save_watermark(new_watermark) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_watermark": str(new_watermark)}, f)


def extract_transactions_incremental():
    watermark = load_watermark()
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

    table_dir = os.path.join(RAW_DATA_DIR, "transactions_incremental")
    os.makedirs(table_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(table_dir, f"transactions_{timestamp}.csv")

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    logger.info(f"Wrote {len(rows)} new rows to {file_path}")

    ts_index = columns.index("transaction_timestamp")
    new_watermark = max(row[ts_index] for row in rows)
    save_watermark(new_watermark)
    logger.info(f"Updated watermark to: {new_watermark}")


if __name__ == "__main__":
    extract_transactions_incremental()
