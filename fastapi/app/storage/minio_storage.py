from minio import Minio
from PIL import Image
from io import BytesIO
import os


class MinioStorageService:

    def __init__(self):

        self.client = Minio(
            os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False
        )


def load_image(self, bucket: str, path: str):

    response = self.client.get_object(bucket, path)
    data = response.read()

    return Image.open(BytesIO(data)).convert("RGB")