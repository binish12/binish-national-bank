# Binish National Bank — Data Engineering Platform

A fictional bank's end-to-end data engineering platform, built as a learning
project covering ingestion, transformation, storage, and analytics using a
modern data stack.

## Architecture

PostgreSQL (source) → Python ingestion → Data cleaning/validation (Pandas)
→ Local ETL pipeline → (planned: S3 data lake → PySpark → Redshift →
Kafka → Airflow → CI/CD)

## Setup

1. Clone the repo and create a virtual environment:
   \`\`\`bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   \`\`\`

2. Copy `.env.example` to `.env` and fill in your PostgreSQL credentials.

3. Ensure PostgreSQL is running locally with the `binish_national_bank_local`
   database created and schema applied (see `sql/` — coming soon).

## Running the pipeline

\`\`\`bash
python -m src.pipeline.run_local_etl
\`\`\`

This runs, in order:
1. Full extraction of all 6 tables from PostgreSQL to `data/raw/`
2. Incremental extraction of new transactions (watermark-based)
3. Cleaning and quarantine of transaction data

## Project structure

\`\`\`
src/
├── ingestion/       # Extraction from PostgreSQL
├── transformation/  # Cleaning, merging, aggregation
├── data_generation/ # Synthetic data + dirty-data injection
├── pipeline/        # Orchestration of the full ETL flow
└── utilities/       # Shared DB connection logic
\`\`\`

## Status

Milestones 0–4 complete (environment, database + synthetic data,
ingestion, Pandas cleaning, local ETL pipeline). Currently working toward
S3, PySpark, Redshift, Kafka, Airflow, and CI/CD.
Current focus: Milestone 5 (main version)