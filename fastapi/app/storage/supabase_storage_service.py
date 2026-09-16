import os
import uuid
from typing import List

import requests
from fastapi import UploadFile

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.storage.object_storage_service import ObjectStorageService, StorageObject
from app.storage.storage_validator import get_extension, validate_image

# 고정값 (설정으로 뺄 필요 없음)
PROFILE_BUCKET = "profile-images"
ECHO_BUCKET = "echo-images"


class SupabaseStorageService(ObjectStorageService):
    def __init__(self):
        self.public_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.profile_bucket = PROFILE_BUCKET
        # TODO: echo-images 버킷 생성 필요 (Supabase 대시보드) — 생성 전까지 list_objects/download_object 미검증
        self.echo_bucket = ECHO_BUCKET

    def _auth_headers(self) -> dict:
        return {"apikey": self.service_key, "Authorization": f"Bearer {self.service_key}"}

    def create_url(self, path: str) -> str:
        return f"{self.public_url}/storage/v1/object/public/{path}"

    def upload(self, file: UploadFile) -> str:
        logger.info("SupaBase 스토리지에 접근합니다.")

        content = validate_image(file)
        logger.debug("이미지 검증을 완료했습니다.")

        object_name = f"{uuid.uuid4()}{get_extension(file)}"

        try:
            response = requests.post(
                f"{self.public_url}/storage/v1/object/{self.profile_bucket}/{object_name}",
                headers={**self._auth_headers(), "Content-Type": file.content_type, "x-upsert": "true"},
                data=content,
                timeout=10,
            )
            response.raise_for_status()
            logger.debug("프로필 이미지를 업로드했습니다.")

        except requests.RequestException as e:
            logger.error(f"Image upload failed: {e}")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

        return self.create_url(f"{self.profile_bucket}/{object_name}")

    def list_objects(self, bucket: str) -> List[StorageObject]:
        objects: List[StorageObject] = []
        offset = 0
        limit = 1000

        while True:
            try:
                response = requests.post(
                    f"{self.public_url}/storage/v1/object/list/{bucket}",
                    headers=self._auth_headers(),
                    json={"limit": limit, "offset": offset, "sortBy": {"column": "name", "order": "asc"}},
                    timeout=10,
                )
            except requests.RequestException as e:
                logger.error(f"{bucket} 목록 조회 실패: {e}")
                raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

            self._raise_if_bucket_not_found(response, bucket)

            try:
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"{bucket} 목록 조회 실패: {e}")
                raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

            page = response.json()
            objects.extend(
                StorageObject(key=item["name"], etag=(item.get("metadata") or {}).get("eTag", "")) for item in page
            )

            if len(page) < limit:
                break
            offset += limit

        return objects

    def download_object(self, bucket: str, key: str) -> bytes:
        try:
            response = requests.get(
                f"{self.public_url}/storage/v1/object/{bucket}/{key}",
                headers=self._auth_headers(),
                timeout=10,
            )
        except requests.RequestException as e:
            logger.error(f"{bucket} 다운로드 실패: {e} (key={key})")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

        self._raise_if_bucket_not_found(response, bucket)

        try:
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"{bucket} 다운로드 실패: {e} (key={key})")
            raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

        return response.content

    def _raise_if_bucket_not_found(self, response: requests.Response, bucket: str) -> None:
        """버킷 없음 응답을 STORAGE_BUCKET_NOT_FOUND로 변환한다.
        Supabase Storage 스펙상 버킷 없음은 404가 기본이지만, 버전에 따라 400 + 바디의
        error/statusCode 메시지로 오는 경우도 있어 함께 확인한다.
        (echo-images 버킷이 아직 없어 실제 응답으로는 검증 못 함 — 버킷 생성 후 재검증 필요)"""

        if response.status_code == 404:
            logger.error(f"{bucket} 버킷을 찾을 수 없습니다 (404).")
            raise CustomException(ErrorCode.STORAGE_BUCKET_NOT_FOUND)

        if response.status_code == 400:
            try:
                body = response.json()
            except ValueError:
                return
            error_message = str(body.get("error", "")) + str(body.get("message", ""))
            if "bucket not found" in error_message.lower() or str(body.get("statusCode")) == "404":
                logger.error(f"{bucket} 버킷을 찾을 수 없습니다 (400: {body}).")
                raise CustomException(ErrorCode.STORAGE_BUCKET_NOT_FOUND)
