from google.cloud import vision
from google.oauth2 import service_account
from app.config.logger import logger
import os


def create_vision_client():
    try:
        if os.getenv("APP_ENV") == "dev":
            credentials = service_account.Credentials.from_service_account_file(
                "./credentials/concrete-flare-495107-c0-0ed9cd7b1ce6.json"
            )

            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            client = vision.ImageAnnotatorClient()

        logger.debug("Google Vision 클라이언트를 생성했습니다.")

        return client

    except Exception as e:
        logger.error(f"Google Vision 클라이언트 생성에 실패했습니다. {e}")
        raise