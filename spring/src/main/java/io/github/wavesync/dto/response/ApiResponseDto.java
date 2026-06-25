package io.github.wavesync.dto.response;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;



@Getter
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
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
