package io.github.wavesync.interceptor;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;



@Slf4j
@Component
public class LoggerInterceptor implements HandlerInterceptor {

    // 요청 시작 시간을 저장하기 위한 key
    private static final String START_TIME = "startTime";

    // 컨트롤러 실행 전에 호출됨 (요청 진입 시점)
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {

        // 요청 시작 시간 저장 (afterCompletion에서 사용)
        request.setAttribute(START_TIME, System.currentTimeMillis());

        // 요청 로그 출력
        log.info("{} [INFO] {} {} 요청을 시작합니다.",
                System.currentTimeMillis(),     // 현재 시간 (timestamp)
                request.getMethod(),           // HTTP Method (GET, POST 등)
                request.getRequestURI()        // 요청 URL
        );

        // true를 반환해야 다음 단계(컨트롤러)로 진행됨
        return true;
    }



     // 요청 처리가 끝난 후 호출됨 (응답 직전)
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {

        // preHandle에서 저장한 시작 시간 가져오기
        long startTime = (long) request.getAttribute(START_TIME);

        // 전체 처리 시간 계산
        long duration = System.currentTimeMillis() - startTime;

        // 응답 로그 출력
        log.info("{} [INFO] {} {} 응답이 완료되었습니다. | status={} | time={}ms",
                System.currentTimeMillis(),     // 현재 시간
                request.getMethod(),           // HTTP Method
                request.getRequestURI(),       // 요청 URL
                response.getStatus(),          // HTTP 상태 코드
                duration                       // 처리 시간(ms)
        );
    }
}