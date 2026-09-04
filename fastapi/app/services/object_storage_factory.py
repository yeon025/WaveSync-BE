import os
from functools import lru_cache

from app.services.minio_object_storage_service import MinioObjectStorageService
from app.services.object_storage_service import ObjectStorageService
from app.services.supabase_storage_service import SupabaseStorageService


@lru_cache
def get_object_storage_service() -> ObjectStorageService:
    """APP_ENV로 dev(MinIO)/prod(Supabase) 스토리지 구현체를 선택한다."""
    if os.getenv("APP_ENV") == "prod":
        return SupabaseStorageService()
    return MinioObjectStorageService()
