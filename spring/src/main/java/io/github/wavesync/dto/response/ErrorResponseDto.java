package io.github.wavesync.dto.response;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;



@Getter
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponseDto {
    private String code;
    private String message;
    private String detail;

    public static ErrorResponseDto of(String code, String message, String detail) {
        return new ErrorResponseDto(code, message, detail);
    }

    public static ErrorResponseDto of(String code, String message) {
        return new ErrorResponseDto(code, message, null);
    }
}
