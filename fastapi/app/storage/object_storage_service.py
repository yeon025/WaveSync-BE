from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from fastapi import UploadFile


@dataclass(frozen=True)
class StorageObject:
    """스토리지 버킷 안의 객체 하나."""

    key: str
    etag: str


class ObjectStorageService(ABC):
    """버킷명은 인터페이스가 강제하지 않고 각 구현체가 __init__에서 스스로 정한다
    (예: self.echo_bucket) — 소스(env var/고정 상수)는 구현체마다 달라도 되지만,
    호출부는 반드시 그 구현체의 속성을 통해 버킷명을 얻어야 한다 (echo_matching_service.py 참고)."""

    @abstractmethod
    def upload(self, file: UploadFile) -> str: ...

    @abstractmethod
    def create_url(self, path: str) -> str: ...

    @abstractmethod
    def list_objects(self, bucket: str) -> List[StorageObject]: ...

    @abstractmethod
    def download_object(self, bucket: str, key: str) -> bytes: ...
