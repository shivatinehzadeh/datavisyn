import os
import logging
import uuid
from typing import BinaryIO
from fastapi import  HTTPException

import aioboto3
from botocore.exceptions import ClientError
from botocore.config import Config
from .base import StorageBackend

logger = logging.getLogger(__name__)


class S3Storage(StorageBackend):

    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        self.endpoint_url = os.getenv("AWS_S3_ENDPOINT_URL")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET environment variable is required")

        self.session = aioboto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

        # Common client config (retries, signature version)
        self.client_config = Config(
            signature_version='s3v4',
            retries={'max_attempts': 5, 'mode': 'standard'},
            connect_timeout=10,
            read_timeout=30,
        )

    def _get_client(self):
        """Factory for async context-managed S3 client"""
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            config=self.client_config,
        )

    async def save(
        self,
        file_id: uuid.UUID,
        file_content: BinaryIO,
        filename: str,
    ) -> str:
        """
        Save file to S3.
        Returns the S3 key that was used.
        """
        s3_key = f"uploads/{file_id}_{filename.lstrip('/')}"

        logger.info(f"Uploading to s3://{self.bucket_name}/{s3_key}")

        try:
            async with self._get_client() as s3:
                # Optional: ensure bucket exists (better done once at startup or in infra)
                try:
                    await s3.head_bucket(Bucket=self.bucket_name)
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code == "404":
                        logger.info(f"Creating bucket {self.bucket_name}")
                        await s3.create_bucket(Bucket=self.bucket_name)
                    elif error_code != "403":  # 403 might mean we have access but can't head
                        raise

                file_content.seek(0)
                await s3.upload_fileobj(
                    Fileobj=file_content,
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    ExtraArgs={
                        # Optional: useful metadata
                        "ContentDisposition": f"attachment; filename=\"{filename}\"",
                        # "ContentType": file_content.content_type,  # if available
                    }
                )

            logger.info(f"Upload successful: {s3_key}")
            return s3_key

        except ClientError as e:
            logger.error(f"S3 client error uploading {filename}: {e.response['Error']}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error uploading {filename}")
            raise

    async def read(self, stored_key: str) -> bytes:
        """
        Read file content from S3 using the stored key.
        Note: renamed parameter to stored_key for clarity (was file_name).
        """
        s3_key = stored_key if stored_key.startswith("uploads/") else f"uploads/{stored_key}"

        logger.info(f"Downloading s3://{self.bucket_name}/{s3_key}")

        try:
            async with self._get_client() as s3:
                response = await s3.get_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
                body = await response["Body"].read()
                logger.info(f"Downloaded {len(body)} bytes from {s3_key}")
                return body

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise HTTPException(status_code=404, detail="Resource not found")

            logger.error(f"S3 error downloading {s3_key}: {e.response['Error']}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error reading {s3_key}")
            raise