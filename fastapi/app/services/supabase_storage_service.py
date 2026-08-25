import os
import uuid
import requests
from fastapi import UploadFile
from app.services.object_storage_service import ObjectStorageService
from app.validators.storage_validator import validate_image, get_extension
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


# Spring application-prod.yml의 supabase.bucket.profiles 값과 동일 (설정으로 뺄 필요 없는 고정값)
PROFILE_BUCKET = "profile-images"


class SupabaseStorageService(ObjectStorageService):

    def __init__(self):
        self.public_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.profile_bucket = PROFILE_BUCKET

    def create_url(self, path: str) -> str:
        return f"{self.public_url}/storage/v1/object/public/{path}"

    def upload_profile_image(self, file: UploadFile) -> str:
        logger.info("SupaBase 스토리지에 접근합니다.")

        content = validate_image(file)
        logger.debug("이미지 검증을 완료했습니다.")

        object_name = f"{uuid.uuid4()}{get_extension(file)}"

        try:
            response = requests.post(
                f"{self.public_url}/storage/v1/object/{self.profile_bucket}/{object_name}",
                headers={
                    "apikey": self.service_key,
                    "Authorization": f"Bearer {self.service_key}",
                    "Content-Type": file.content_type,
                    "x-upsert": "true",
                },
                data=content,
                timeout=10,
            )
            response.raise_for_status()
            logger.debug("프로필 이미지를 업로드했습니다.")

        except requests.RequestException as e:
            logger.error(f"Image upload failed: {e}")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

        return self.create_url(f"{self.profile_bucket}/{object_name}")
