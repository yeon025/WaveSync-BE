import io
from PIL import Image
from fastapi import UploadFile
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


def validate_image(file: UploadFile) -> bytes:
    content = file.file.read()
    file.file.seek(0)

    # 빈 이미지인지 확인
    if not content:
        raise CustomException(ErrorCode.IMAGE_REQUIRED)

    content_type = file.content_type

    # 이미지 파일인지 확인
    if content_type is None or not content_type.startswith("image/"):
        raise CustomException(ErrorCode.INVALID_IMAGE_FILE)

    # 1920×1080인지 해상도 검증
    try:
        image = Image.open(io.BytesIO(content))
        width, height = image.size
    except Exception as e:
        logger.error(str(e))
        raise CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)

    if width != 1920 or height != 1080:
        raise CustomException(ErrorCode.INVALID_IMAGE_RESOLUTION)

    return content


def get_extension(file: UploadFile) -> str:
    filename = file.filename

    if not filename or "." not in filename:
        return ""

    return filename[filename.rfind("."):]
