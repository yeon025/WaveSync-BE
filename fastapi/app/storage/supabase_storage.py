import os
import requests
from PIL import Image
from io import BytesIO


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

        return Image.open(BytesIO(response.content)).convert("RGB")