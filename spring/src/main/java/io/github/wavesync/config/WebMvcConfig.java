package io.github.wavesync.config;
import io.github.wavesync.interceptor.LoggerInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;


@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final LoggerInterceptor loggerInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {

        registry.addInterceptor(loggerInterceptor)
                .addPathPatterns("/**") // 모든 API 적용
                .excludePathPatterns(
                        "/error",
                        "/favicon.ico",
                        "/swagger-ui/**",
                        "/v3/api-docs/**"
                );
    }
}