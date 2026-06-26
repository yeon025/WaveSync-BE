package io.github.wavesync.exception;
import lombok.Getter;
import org.springframework.http.HttpStatus;


@Getter
public enum ErrorCode {

    IMAGE_REQUIRED(HttpStatus.BAD_REQUEST, "IMAGE_REQUIRED", "이미지를 업로드하지 않았습니다. 이미지를 선택해주세요."),
    INVALID_IMAGE_FILE(HttpStatus.BAD_REQUEST, "INVALID_IMAGE_FILE", "이미지 파일만 업로드 가능합니다."),
    RESONATOR_NOT_FOUND(HttpStatus.BAD_REQUEST, "RESONATOR_NOT_FOUND", "등록하지 않은 공명자입니다."),
    INVALID_IMAGE_RESOLUTION(HttpStatus.BAD_REQUEST, "INVALID_IMAGE_RESOLUTION", "1920×1080 해상도의 이미지만 업로드 가능합니다."),
    DATA_NOT_FOUND(HttpStatus.UNPROCESSABLE_ENTITY, "DATA_NOT_FOUND", "이미지 인식 결과를 확인할 수 없습니다. 다른 이미지를 선택해주세요."),
    DATABASE_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "DATABASE_ERROR", "데이터 처리 중 오류가 발생했습니다. 다시 시도해주세요."),
    IMAGE_PROCESSING_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "IMAGE_PROCESSING_FAILED", "이미지 처리 중 오류가 발생했습니다. 다시 시도해주세요."),
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_SERVER_ERROR", "서버 내부 오류가 발생했습니다.");

    private final HttpStatus status;
    private final String code;
    private final String message;

    ErrorCode(HttpStatus status, String code, String message) {
        this.status = status;
        this.code = code;
        this.message = message;
    }
}