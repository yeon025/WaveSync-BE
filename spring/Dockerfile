# Build
FROM gradle:8.8-jdk21 AS builder

WORKDIR /app

COPY . .

RUN gradle bootJar --no-daemon

# Java 21 실행 환경 사용
FROM eclipse-temurin:21-jdk

# 컨테이너 작업 디렉터리
WORKDIR /app

# 빌드된 JAR 파일 복사
COPY build/libs/wavesync-0.0.1-SNAPSHOT.jar app.jar

# Spring Boot 포트
EXPOSE 8080

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]