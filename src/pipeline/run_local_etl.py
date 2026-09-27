import logging

from src.ingestion.extract_full import extract_table_full
from src.ingestion.extract_incremental import extract_transactions_incremental
from src.transformation.clean_transactions import process_transactions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

TABLES = ["branches", "customers", "accounts",
          "cards", "merchants", "transactions"]


def run_pipeline():
    logger.info("=== Starting ETL pipeline run ===")

    # Stage 1: Full extraction for all tables
    try:
        logger.info("Stage 1: Full extraction")
        for table in TABLES:
            extract_table_full(table)
        logger.info("Stage 1 complete.")
    except Exception as e:
        logger.error(f"Stage 1 (full extraction) failed: {e}")
        return  # stop here — no point continuing if extraction itself is broken

    # Stage 2: Incremental extraction for transactions
    try:
        logger.info("Stage 2: Incremental extraction (transactions)")
        extract_transactions_incremental()
        logger.info("Stage 2 complete.")
    except Exception as e:
        logger.error(f"Stage 2 (incremental extraction) failed: {e}")
        return

    # Stage 3: Cleaning
    try:
        logger.info("Stage 3: Cleaning transactions")
        process_transactions()
        logger.info("Stage 3 complete.")
    except Exception as e:
        logger.error(f"Stage 3 (cleaning) failed: {e}")
        return

    logger.info("=== ETL pipeline run finished successfully ===")


if __name__ == "__main__":
    run_pipeline()
