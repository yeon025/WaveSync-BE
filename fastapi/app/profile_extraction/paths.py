import os

# 3단계 상위 = fastapi/. images/는 app 패키지 밖의 리소스 디렉터리다.
# profile_extraction/ 내 여러 모듈이 공유하는 경로라 여기에 둔다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP_DIR = os.path.join(BASE_DIR, "images/tmp")
