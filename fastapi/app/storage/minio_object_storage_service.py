import io
import os
from typing import List
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.storage.object_storage_service import ObjectStorageService, StorageObject
from app.storage.storage_validator import raise_if_minio_bucket_not_found


class MinioObjectStorageService(ObjectStorageService):
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT")
        self.public_url = os.getenv("MINIO_PUBLIC_URL")
        self.echo_bucket = os.getenv("MINIO_BUCKET_ECHOES")

        parsed = urlparse(self.endpoint)
        self.client = Minio(
            parsed.netloc,
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=parsed.scheme == "https",
        )

    def create_url(self, path: str) -> str:
        return f"{self.public_url}/{path}"

    def _put(self, bucket: str, object_name: str, content: bytes, content_type: str) -> None:
        try:
            self.client.put_object(
                bucket,
                object_name,
                io.BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
        except Exception as e:
            if isinstance(e, S3Error):
                raise_if_minio_bucket_not_found(e, bucket)
            logger.error(f"Image upload failed: {e}")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

    def upload_bytes(self, bucket: str, object_name: str, content: bytes, content_type: str) -> str:
        self._put(bucket, object_name, content, content_type)
        return f"{self.endpoint}/{bucket}/{object_name}"

    def list_objects(self, bucket: str) -> List[StorageObject]:
        try:
            objects = self.client.list_objects(bucket)
            return [StorageObject(key=obj.object_name, etag=obj.etag) for obj in objects]

        except Exception as e:
            if isinstance(e, S3Error):
                raise_if_minio_bucket_not_found(e, bucket)
            logger.error(f"{bucket} 목록 조회 실패: {e}")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

    def download_object(self, bucket: str, key: str) -> bytes:
        try:
            response = self.client.get_object(bucket, key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        except Exception as e:
            if isinstance(e, S3Error):
                raise_if_minio_bucket_not_found(e, bucket)
            logger.error(f"{bucket} 다운로드 실패: {e} (key={key})")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)
