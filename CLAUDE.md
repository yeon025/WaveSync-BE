# WaveSync-BE

《명조: 워더링 웨이브》 프로필 이미지를 분석해 캐릭터 스펙을 계산하는 개인 서비스의 백엔드 (FastAPI).

구조와 요청 흐름은 `README.md`를 참고하고, 이 문서는 개발할 때 지킬 규칙만 둔다.

## 명령어

```bash
# 전체 스택 (postgres, minio, fastapi) — 최초 기동 시 infra/postgres/*.sql 실행
cd infra && docker compose up

# FastAPI만 로컬 실행 (postgres/minio는 compose로 띄운 상태, Python 3.13)
cd fastapi && uvicorn app.main:app --reload --port 8000

# 테스트 (외부 서비스·DB 접속 없음, conftest가 APP_ENV=test로 고정)
cd fastapi && pytest

# 검사 및 포맷
# line-length 120, 큰따옴표
cd fastapi && ruff check . && ruff format .
```

- `fastapi/tests/`는 `fastapi/.gitignore`에 들어 있어 Git에 올라가지 않는다.
  테스트를 추가해도 커밋되지 않는다는 점을 알고 있을 것.
- DB 스키마와 마스터 데이터는 `infra/postgres/01_init.sql`이 전부다.
  별도 마이그레이션 도구가 없으므로 스키마 변경은 `01_init.sql`을 직접 갱신한다.
  초기화 SQL은 볼륨이 비었을 때만 실행되므로 `docker compose down -v` 필요.

## 구조 원칙

- **도메인·기능 단위로 파일을 묶는다.**
  - `models/`·`repositories/`·`services/` 같은 계층별 폴더를 만들지 않는다.
  - 한 기능의 모델, repository, enum, 매핑은 같은 폴더에 둔다.
  - 예: `app/resonator/`, `app/profile_extraction/`, `app/auth/`

- 여러 영역을 가로지르는 업무 흐름(등록, 조회·수정·삭제, 스펙 계산)은
  `resonator/` 루트의 `*_service.py`에 둔다.
  하위 폴더(`master/`, `resonance_node/`, `user_resonator/`)는
  데이터와 해당 영역 로직을 맡는다.

- `profile_extraction/`은 DB와 `resonator/`에 의존하지 않는다.
  이미지 읽기용 `app/storage`만 사용한다.
  추출 결과의 검증은 `resonator/extract_profile_validation_service.py`가 한다.

- 한 모델·한 기능에서만 쓰는 enum은 그 파일에 같이 둔다.
  여러 영역이 공유하는 `StatType`만 `resonator/stat_type.py`에 둔다.

- 작은 설정이나 미들웨어 때문에 별도 폴더를 만들지 않는다.
  `main.py`에 둔다.

- 스토리지는 `ObjectStorageService` 인터페이스 뒤에 숨긴다.
  `APP_ENV`(dev=MinIO, prod=Supabase)에 따라 factory가 구현체를 고른다.
  서비스 로직은 어떤 스토리지인지 몰라야 한다.

## 코드 규칙

- **라우터는 얇게.**
  - 검증과 위임만 하고 로직은 서비스에 둔다.
  - 예외를 라우터에서 try/except로 감싸지 않는다.

- **예외**
  - `raise CustomException(ErrorCode.XXX)`를 사용한다.
  - 새 에러는 `exceptions/error_code.py`의 `(status, code, message)`에 추가한다.
  - 처리는 `exception_handler.py`가 담당한다.
    - `CustomException`
    - `SQLAlchemyError` → `DATABASE_ERROR`
    - 그 외 → `INTERNAL_SERVER_ERROR`

- **응답**
  - 성공 응답은 `schemas/api_response.py`의 `ApiResponse[T]{code, message, data}`로 감싼다.
  - 라우터에 `response_model=ApiResponse[Dto]`와
    `response_model_exclude_none=True`를 선언한다.
  - 도메인별 응답 래퍼를 새로 만들지 않는다.

- **스키마 위치**
  - 도메인 전용 Request/Response는 해당 도메인의 `schemas.py`
  - 공통은 `app/schemas/`

- **트랜잭션**
  - `get_db()`는 commit하지 않고 예외 시 rollback만 한다.
    (yield 이후는 응답 전송 뒤에 실행된다.)
  - 쓰기를 하는 서비스 함수는 **응답 객체를 만들기 전에** `db.commit()`을 직접 호출한다.
  - commit은 인스턴스를 expire시키므로 응답에 쓸 값은 commit 전에 확보한다.
  - 서비스 간 공유 헬퍼와 repository는 commit하지 않는다.
    (호출자가 경계를 잡는다.)

- **Repository**
  - 마스터 테이블은 테이블별 repository로 둔다.
  - 사용자 데이터는 `user_resonator_repository.py` 하나가 애그리게잇 전체를 맡는다.
  - Generic/Base Repository로 통합하지 않는다.
  - ORM 객체나 조회 결과만 반환하고 API Schema는 만들지 않는다.

- **ORM → Schema 변환**
  - 단순 변환은 Schema의 `from_*` classmethod에서 한다.
  - 새 mapper 파일을 만들지 않는다.
  - 여러 도메인 객체를 조합하는 복잡한 변환만 서비스나 기존 mapper
    (`resonance_node_mapper.py`)에서 한다.

- **Enum**
  - `class X(str, Enum)`에 소문자 값을 쓴다.
  - 컬럼은 `SAEnum(X, native_enum=False, length=N, values_callable=enum_values)`로 선언한다.
  - `native_enum=False`를 빼면 Postgres에 ENUM 타입이 생겨 VARCHAR 스키마와 어긋난다.
  - `values_callable`을 빼면 값이 아니라 멤버 이름이 저장된다.
  - 요청/응답 스키마에도 같은 Enum을 써서 입력 검증을 맡긴다.
  - DB 레벨 CHECK/ENUM 제약은 도입하지 않았다.

- 주석과 문서는 한국어로, 기존 코드의 주석 밀도와 네이밍을 따른다.

## 인증·인가

- **사용자 데이터 스코프**
  - `user_resonators` 및 하위 테이블의 조회·수정·삭제는 반드시 `current_user.id`로 스코프한다.
  - 리포지토리 함수가 `user_id`를 파라미터로 받아 WHERE/JOIN 조건에 넣는다. 서비스단에서 필터링하지 않는다.
  - `resonator_master_repository.find_resonator_summary`처럼 LEFT JOIN으로 전체 마스터 목록을 보여주는
    쿼리는 `user_id` 조건을 WHERE가 아니라 **JOIN 조건**에 둔다. WHERE에 두면 아직 등록하지 않은
    마스터 행까지 결과에서 사라진다.

- **존재 여부 숨기기**
  - 다른 사용자 리소스에 접근했을 때는 기존 `RESONATOR_NOT_FOUND`(400)를 그대로 재사용한다.
  - 이 프로젝트에 새로 진짜 HTTP 404를 도입하지 않는다.

- **CSRF**
  - 상태 변경 라우터(POST/PATCH/DELETE)는 `app/auth/csrf.py`의 `require_csrf_header`를 거친다.
  - `get_current_user`가 자동으로 체인한다.
  - 인증이 필요 없는 엔드포인트(`POST /auth/session`)는 직접 `Depends(require_csrf_header)`를 건다.

- **AuthenticatedUser**
  - 세션/유저 값은 ORM `User` 대신 `app/auth/authenticated_user.py`의 `AuthenticatedUser`(불변 값
    객체)로 서비스·라우터에 넘긴다.
  - commit 전에 값을 확보해 만든다(트랜잭션 규칙과 같은 이유).

- **관리자 권한**
  - 별도 클레임 키 없이, `ADMIN_EMAIL` 환경변수와 일치하는 검증된(`email_verified`) Google 이메일로
    로그인할 때마다 자동으로 재계산해 `users.role`에 반영한다(`google_login_service._resolve_role`).
  - 클라이언트가 보낸 값은 쓰지 않는다.
  - `ADMIN_EMAIL`이 바뀌면 그 세션의 다음 로그인 때 즉시 `user`로 내려간다. 이미 발급된 세션 자체를
    즉시 강제 로그아웃하지는 않는다(개인용 서비스 규모의 트레이드오프).
  - 관리자 전용 라우터(`app/admin/`)는 `current_user.py`의 `require_admin`을 라우터 전체에 건다.
    `role`이 `ADMIN`이 아니면 `FORBIDDEN`(403)을 던진다.
  - 사용자 소유권을 숨기는 `RESONATOR_NOT_FOUND`(400) 패턴과는 성격이 다른 경계이므로 섞어 쓰지
    않는다 — 역할 기반 차단은 403으로 명확히 드러낸다.

- **Rate limit**
  - 세션 발급의 "신규 계정 생성" 경로에만 `app/auth/rate_limiter.py`의 메모리 기반 요청 제한을 건다.
  - 인스턴스 재시작·스케일 시 카운터가 공유되지 않는 한계가 있다(외부 저장소 없이 가기 위한 의도적 선택).

## 성능·비용 제약 (퇴행 주의)

- **무료 인프라만 사용한다.**
  유료 티어로 넘어가는 설정을 넣지 않는다.
  (Cloud Run, Vercel, Supabase 무료 플랜 기준)

- **Google Vision 호출은 등록 요청 1건당 1회.**
  영역을 크롭해 세로로 병합한 이미지 한 장으로 호출하는 구조를 유지한다.
  (`ocr/text_region_builder.py`의 `crop_and_stack`
  → `ocr/ocr_service.py`의 `extract_text`)
  구조를 건드릴 때 호출 횟수가 늘지 않는지 확인한다.

- **N+1 방지**
  연관 엔티티는 `selectinload`/`joinedload`로 배치 조회한다.

- **Batch insert**
  Sequence 기반 PK + `insertmanyvalues_page_size=50`(`db/session.py`) 조합을 유지한다.
  IDENTITY로 바꾸면 batch insert가 안 된다.

  현재 시퀀스:
  - `user_node_seq`: INCREMENT 10 (노드 10개 고정)
  - `user_echo_sub_seq`: INCREMENT 25 (5에코 × 5서브)

  모델의 `Sequence(...increment=)`와 `01_init.sql`을 같이 맞춘다.

- 개인용 소규모 서비스이므로 멀티테넌시나 대규모 트래픽 대응 같은
  과도한 확장성 설계를 하지 않는다.

## 알려진 의도적 차이

- 요청 검증 실패는 FastAPI 기본값인 **422**를 반환한다.
  프론트가 400을 기대하는지 확인이 필요하다.

- 공명자 목록의 한글 정렬은 Python 기본 문자열 비교를 쓴다.
  현재는 순수 한글 이름이라 사전순과 같지만,
  숫자·영문이 섞인 이름이 마스터 데이터에 들어오면 재검토한다.

## 커밋

- 형식은 `타입: 한국어 설명`이다.
  타입은 Conventional Commits(feat, fix, refactor, docs 등)를 영어로 쓴다.
- 제목은 50자 이내로 쓰고 본문은 쓰지 않는다.
- 논리적 단위로 나누되, 의존 관계가 있으면 순서를 고려한다.
- 사용자가 요청하기 전에는 commit/push하지 않는다.
- 배포는 `main`의 `fastapi/` 변경 시 `.github/workflows/deploy-fastapi.yml`이 실행하므로,
  push 전에 영향을 의식한다.
