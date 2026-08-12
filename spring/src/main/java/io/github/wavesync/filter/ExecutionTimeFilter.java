package io.github.wavesync.filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Slf4j
@Component
@Order(Integer.MIN_VALUE)
public class ExecutionTimeFilter extends OncePerRequestFilter {

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return request.getRequestURI().equals("/actuator/health");
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain filterChain
    ) throws ServletException, IOException {

        // 요청 시작 시간 저장
        long start = System.currentTimeMillis();

        // 요청 로그 출력
        log.info("{} {} 요청을 시작합니다.", request.getMethod(), request.getRequestURI());

        try {
            filterChain.doFilter(request, response); // 이 안에서 다른 Filter들 + DispatcherServlet(Interceptor+Controller) 실행됨
        } finally {
            // 전체 처리 시간 계산
            long duration = System.currentTimeMillis() - start;

            // 응답 로그 출력
            log.info("{} {} 응답이 완료되었습니다. | status={} | time={}ms", request.getMethod(), request.getRequestURI(), response.getStatus(), duration);
        }
    }
}
