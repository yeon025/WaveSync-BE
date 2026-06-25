package io.github.wavesync.dto.response;
import lombok.*;
import org.springframework.http.HttpStatus;


@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponseDto<T> {
    private String code;
    private String message;
    private T data;

    public static <T> ApiResponseDto<T> of(String code, String message, T data) {
        return new ApiResponseDto<>(code, message, data);
    }

    public static ApiResponseDto<Void> of(String code, String message) {
        return new ApiResponseDto<>(code, message, null);
    }
}
