from abc import ABC, abstractmethod

from fastapi import UploadFile


class ObjectStorageService(ABC):
    @abstractmethod
    def upload(self, file: UploadFile) -> str: ...

    @abstractmethod
    def create_url(self, path: str) -> str: ...
