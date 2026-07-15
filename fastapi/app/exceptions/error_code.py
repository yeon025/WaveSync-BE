from enum import Enum


class ErrorCode(Enum):

    VALIDATION_FAILED = (
        422,
        "VALIDATION_FAILED",
        "이미지 인식 결과를 확인할 수 없습니다. 다른 이미지를 선택해주세요."
    )

    UNKNOWN_STORAGE_PROVIDER = (
        500,
        "UNKNOWN_STORAGE_PROVIDER",
        "지원하지 않는 스토리지입니다."
    )