package io.github.wavesync.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.wavesync.dto.request.ExtractProfileRequestDto;
import io.github.wavesync.dto.response.ApiResponseDto;
import io.github.wavesync.dto.response.ErrorResponseDto;
import io.github.wavesync.dto.response.ExtractProfileResponseDto;
import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Slf4j
@Component
@RequiredArgsConstructor
public class FastApiClient {

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    public ApiResponseDto<ExtractProfileResponseDto> extractImage(ExtractProfileRequestDto request) {

        try {
            log.info(objectMapper.writeValueAsString(request));
        } catch (Exception e) {
            log.error("JSON serialize failed", e);
        }

        return webClient.post()
                .uri("/api/resonators/images")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .onStatus(
                        status -> status.value() == 422,
                        response -> response.bodyToMono(ErrorResponseDto.class)
                                .flatMap(error -> Mono.error(new CustomException(ErrorCode.DATA_NOT_FOUND)))
                )
                .onStatus(
                        HttpStatusCode::is5xxServerError,
                        response -> Mono.error(new CustomException(ErrorCode.INTERNAL_SERVER_ERROR))
                )
                .bodyToMono(new ParameterizedTypeReference<ApiResponseDto<ExtractProfileResponseDto>>() {})
                .block();
    }
}