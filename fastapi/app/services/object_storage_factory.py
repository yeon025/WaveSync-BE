import os
from functools import lru_cache

from app.services.minio_object_storage_service import MinioObjectStorageService
from app.services.object_storage_service import ObjectStorageService
from app.services.supabase_storage_service import SupabaseStorageService


@lru_cache
def get_object_storage_service() -> ObjectStorageService:
    """APP_ENV로 dev(MinIO)/prod(Supabase) 구현체를 선택한다.

    Spring의 ObjectStorageService + @Profile("dev"/"prod") 분기에 대응.
    호출부는 이 함수만 알면 되고, 어떤 스토리지를 쓰는지는 몰라도 된다.
    """
    if os.getenv("APP_ENV") == "prod":
        return SupabaseStorageService()
    return MinioObjectStorageService()
