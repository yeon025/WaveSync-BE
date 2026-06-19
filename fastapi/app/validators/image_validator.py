import cv2
from app.config.logger import logger



def validate_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        logger.warning(f"{image_path}를 불러올 수 없습니다.", stacklevel=2)