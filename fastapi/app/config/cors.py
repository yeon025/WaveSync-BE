# CORSMiddleware와 CSRF 검증(app/auth/csrf.py)이 같은 허용 오리진 목록을 써야 하므로 한곳에 둔다.
ALLOWED_ORIGINS = ["http://localhost:3000", "https://resocollector.com"]
