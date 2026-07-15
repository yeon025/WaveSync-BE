import os
import requests
import numpy as np
import cv2


class SupabaseStorageService:

    def __init__(self):

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY")


    def load_image(self, bucket: str, path: str):

        response = requests.get(
            f"{self.url}/storage/v1/object/{bucket}/{path}",
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}"
            }
        )

        response.raise_for_status()

        np_arr = np.frombuffer(response.content, np.uint8)

        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)