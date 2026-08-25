from enum import Enum


class ErrorCode(Enum):

    IMAGE_REQUIRED = (
        400,
        "IMAGE_REQUIRED",
        "이미지를 업로드하지 않았습니다. 이미지를 선택해주세요."
    )

    INVALID_IMAGE_FILE = (
        400,
        "INVALID_IMAGE_FILE",
        "이미지 파일만 업로드할 수 있습니다."
    )

    INVALID_IMAGE_RESOLUTION = (
        400,
        "INVALID_IMAGE_RESOLUTION",
        "1920×1080 해상도의 이미지만 업로드 가능합니다. 다른 이미지를 선택해주세요."
    )

    IMAGE_LOAD_FAILED = (
        400,
        "IMAGE_LOAD_FAILED",
        "이미지를 불러올 수 없습니다."
    )

    IMAGE_NOT_FOUND = (
        404,
        "IMAGE_NOT_FOUND",
        "이미지를 찾을 수 없습니다."
    )

    IMAGE_ACCESS_DENIED = (
        403,
        "IMAGE_ACCESS_DENIED",
        "이미지 접근 권한이 없습니다."
    )

    IMAGE_PROCESSING_FAILED = (
        500,
        "IMAGE_PROCESSING_FAILED",
        "이미지 처리 중 오류가 발생했습니다. 다시 시도해주세요."
    )

    RESONATOR_NOT_FOUND = (
        400,
        "RESONATOR_NOT_FOUND",
        "등록하지 않은 공명자입니다."
    )

    DATABASE_ERROR = (
        500,
        "DATABASE_ERROR",
        "데이터 처리 중 오류가 발생했습니다. 다시 시도해주세요."
    )

    INTERNAL_SERVER_ERROR = (
        500,
        "INTERNAL_SERVER_ERROR",
        "서버 내부 오류가 발생했습니다."
    )

    VALIDATION_FAILED = (
        422,
        "VALIDATION_FAILED",
        "추출된 데이터가 유효하지 않습니다."
    )

    IMAGE_SIZE_EXCEEDED = (
        413,
        "IMAGE_SIZE_EXCEEDED",
        "이미지 크기는 500KB 이하만 업로드할 수 있습니다. 다른 이미지를 선택해주세요."
    )
