from minio import Minio
from PIL import Image
import numpy as np
import cv2
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
    
    np_arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return img