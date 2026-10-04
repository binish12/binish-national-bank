import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def get_s3_client():
    """Return a boto3 S3 client configured from environment variables."""
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


def get_bucket_name() -> str:
    return os.getenv("S3_BUCKET_NAME")
