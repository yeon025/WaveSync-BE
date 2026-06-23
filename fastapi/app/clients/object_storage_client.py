from minio import Minio
from io import BytesIO
from PIL import Image
import os



MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)


def load_image(bucket: str, path: str) -> Image.Image:
    response = minio_client.get_object(bucket, path)
    data = response.read()
    return Image.open(BytesIO(data)).convert("RGB")