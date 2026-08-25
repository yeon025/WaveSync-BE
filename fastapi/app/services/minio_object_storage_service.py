import io
import os
import uuid
from urllib.parse import urlparse
from minio import Minio
from fastapi import UploadFile
from app.services.object_storage_service import ObjectStorageService
from app.validators.storage_validator import validate_image, get_extension
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


class MinioObjectStorageService(ObjectStorageService):

    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT")
        self.public_url = os.getenv("MINIO_PUBLIC_URL")
        self.profile_bucket = os.getenv("MINIO_BUCKET_PROFILES")

        parsed = urlparse(self.endpoint)
        self.client = Minio(
            parsed.netloc,
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=parsed.scheme == "https",
        )

    def create_url(self, path: str) -> str:
        return f"{self.public_url}/{path}"

    def upload_profile_image(self, file: UploadFile) -> str:
        logger.info("MinIO 스토리지에 접근합니다.")

        content = validate_image(file)
        logger.debug("이미지 검증을 완료했습니다.")

        object_name = f"{uuid.uuid4()}{get_extension(file)}"

        try:
            self.client.put_object(
                self.profile_bucket,
                object_name,
                io.BytesIO(content),
                length=len(content),
                content_type=file.content_type,
            )
            logger.debug("프로필 이미지를 업로드했습니다.")

        except Exception as e:
            logger.error(f"Image upload failed: {e}")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

        return f"{self.endpoint}/{self.profile_bucket}/{object_name}"
