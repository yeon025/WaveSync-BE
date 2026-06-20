from enum import Enum


class ErrorCode(Enum):

    IMAGE_REQUIRED = (
        400,
        "IMAGE_REQUIRED",
        "이미지를 업로드하지 않았습니다. 이미지를 선택해주세요."
    )

    INVALID_IMAGE_SIZE = (
        400,
        "INVALID_IMAGE_SIZE",
        "1920×1080 크기의 이미지만 업로드 가능합니다."
    )

    VALIDATION_FAILED = (
        422,
        "VALIDATION_FAILED",
        "이미지 인식 결과를 확인할 수 없습니다. 다른 이미지를 선택해주세요."
    )

    IMAGE_SAVE_FAILED = (
        500,
        "IMAGE_SAVE_FAILED",
        "이미지 저장에 실패했습니다. 다시 시도해주세요."
    )

    RESONATOR_SAVE_FAILED = (
        500,
        "RESONATOR_SAVE_FAILED",
        "공명자 저장에 실패했습니다. 다시 시도해주세요."
    )