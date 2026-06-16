# Python 3.13 실행 환경 사용
FROM python:3.13-slim

# 컨테이너 작업 디렉터리
WORKDIR /app

# 의존성 목록 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# FastAPI 포트
EXPOSE 8000