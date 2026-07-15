# storage/minio_storage.py

from minio import Minio
from PIL import Image
import numpy as np
import cv2
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

        np_arr = np.frombuffer(data, np.uint8)

        return cv2.imdecode(np_arr,cv2.IMREAD_COLOR)