import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open and return a new connection to the banking database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
