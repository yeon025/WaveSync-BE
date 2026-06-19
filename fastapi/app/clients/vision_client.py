from google.cloud import vision
from google.oauth2 import service_account


def create_vision_client():
  credentials = service_account.Credentials.from_service_account_file(
              "./credentials/concrete-flare-495107-c0-0ed9cd7b1ce6.json"
          )
  return vision.ImageAnnotatorClient(credentials=credentials)
  