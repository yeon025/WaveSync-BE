from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class StorageObject:
    key: str
    etag: str


class ObjectStorageService(ABC):
    """버킷명은 구현체마다 정하는 방식이 다르므로 호출부는 반드시 구현체 속성(예: echo_bucket)으로 얻는다."""

    @abstractmethod
    def upload_bytes(self, bucket: str, object_name: str, content: bytes, content_type: str) -> str: ...

    @abstractmethod
    def create_url(self, path: str) -> str: ...

    @abstractmethod
    def list_objects(self, bucket: str) -> List[StorageObject]: ...

    @abstractmethod
    def download_object(self, bucket: str, key: str) -> bytes: ...
