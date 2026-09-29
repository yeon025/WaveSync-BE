import os
from functools import lru_cache

from app.storage.minio_object_storage_service import MinioObjectStorageService
from app.storage.object_storage_service import ObjectStorageService
from app.storage.supabase_storage_service import SupabaseStorageService


@lru_cache
def get_object_storage_service() -> ObjectStorageService:
    if os.getenv("APP_ENV") == "prod":
        return SupabaseStorageService()
    return MinioObjectStorageService()
