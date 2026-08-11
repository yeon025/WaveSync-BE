from enum import Enum


class ErrorCode(Enum):

    IMAGE_LOAD_FAILED = (
        400,
        "이미지를 불러올 수 없습니다."
    )

    IMAGE_NOT_FOUND = (
        404,
        "이미지를 찾을 수 없습니다."
    )

    IMAGE_ACCESS_DENIED = (
        403,
        "이미지 접근 권한이 없습니다."
    )