from enum import Enum


class ErrorCode(Enum):

    VALIDATION_FAILED = (
        422,
        "VALIDATION_FAILED",
        "이미지 인식 결과를 확인할 수 없습니다. 다른 이미지를 선택해주세요."
    )

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