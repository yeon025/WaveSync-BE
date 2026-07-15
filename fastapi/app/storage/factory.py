import os
from .minio_storage import MinioStorageService
from .supabase_storage import SupabaseStorageService
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


def get_storage():

    provider = os.getenv("STORAGE_PROVIDER")

    if provider == "minio":
        logger.info("MinIO 스토리지에 접근합니다.")
        return MinioStorageService()

    if provider == "supabase":
        logger.info("Supabase 스토리지에 접근합니다.")
        return SupabaseStorageService()

    raise CustomException(ErrorCode.UNKNOWN_STORAGE_PROVIDER)
