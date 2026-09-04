# WaveSync-BE

《명조: 워더링 웨이브》 캐릭터 프로필 이미지를 분석해 스펙을 계산해주는 개인 서비스의 백엔드.

## 진행 중인 마이그레이션 (가장 중요)

**Spring Boot의 모든 로직을 FastAPI로 이전하는 작업을 진행 중이다.** 최종적으로 `spring/` 디렉토리는 제거되고 `fastapi/`만 남는다.

- 이관 대상: `spring/src/main/java/io/github/wavesync/` 하위의 `entity`, `repository`, `service`, `controller`, `dto` 전체
- 이관 순서 원칙: 도메인 하나를 통째로 옮긴다 (entity → repository → service → router 순서로, 중간에 끊지 않기)
- **Spring 코드는 이관 완료 전까지 삭제하지 말 것.** 이관한 FastAPI 로직과 동작이 동일한지 비교할 기준(reference)으로 남겨둔다
- 이관이 끝난 도메인은 이 파일의 "이관 진행 상황" 표에 체크하고, `spring/` 쪽 해당 코드에 `// MIGRATED to fastapi/app/...` 주석을 남긴다
- 작업 중 어느 쪽(Spring/FastAPI) 코드를 수정해야 하는지 애매하면 먼저 물어볼 것 — 같은 로직이 두 곳에 있는 과도기라 혼동하기 쉽다

#### MIGRATED 주석 규칙

- 도메인 엔티티/서비스/컨트롤러 파일: 이관 완료 시 `// MIGRATED to fastapi/app/...` 남김
- **공용 enum 정의 파일(`StatType.java`, `Element.java`, `BranchPosition.java`, `NodePosition.java` 등)은 표시하지 않는다.** 여러 도메인이 나눠 쓰는 값 정의라 "이관 완료" 신호로 부적절함. 추적은 그 enum을 컬럼으로 쓰는 엔티티 파일 쪽에서만 한다

## 이관 진행 상황

Spring 파일 단위로 쪼개서 추적한다. 실제 클래스가 존재하지 않는 칸은 `-`.

| 도메인         | 구성요소                                                                            | Entity/Model           | Repository                    | Service | Router/Controller |
| -------------- | ------------------------------------------------------------------------------------ | ---------------------- | ------------------------------ | ------- | ------------------ |
| Resonator      | `ResonatorMaster`                                                                    | ✅                      | ✅                               | -       | -                   |
| Resonator      | `UserResonator`                                                                      | ✅                      | ✅                               | -       | -                   |
| Resonator      | `FinalStat`                                                                          | ✅                      | ✅                               | -       | -                   |
| Resonator      | `ResonatorService`                                                                   | -                       | -                               | ✅      | -                   |
| Resonator      | `SpecCalculationService`                                                             | -                       | -                               | ✅      | -                   |
| Resonator      | `ExtractProfileValidationService`                                                    | -                       | -                               | ✅      | -                   |
| Resonator      | `ResonatorController`                                                                | -                       | -                               | -       | ✅                  |
| Echo           | `UserEcho`                                                                           | ✅                      | ✅                               | -       | -                   |
| Echo           | `UserEchoSub`                                                                        | ✅                      | ✅                               | -       | -                   |
| ResonanceNode  | `ResonanceNodeMaster`                                                                | ✅                      | - (전용 repository 없음, `ResonatorMasterRepository`로 접근) | -       | -                   |
| ResonanceNode  | `UserResonanceNode`                                                                  | ✅                      | ✅                               | -       | -                   |
| WeaponMaster   | `WeaponMaster`                                                                       | ✅                      | ✅                               | -       | -                   |
| ObjectStorage  | `ObjectStorageService` / `MinioObjectStorageService` / `SupabaseStorageService`      | -                       | -                               | ✅      | - (전용 컨트롤러 없음) |
| 이미지 분석    | OCR/Vision                                                                           | ✅ 이미 FastAPI에 있음   | -                               | -       | -                   |

체크 표시는 실제 진행에 맞게 갱신할 것. ⬜ 미착수 / 🔶 부분 완료(사유는 같은 칸에 적기) / ✅ 완료 / `-` 해당 없음(Spring에도 그 파일이 없음).

**✅는 "그 시점까지 파악된 범위에서 완료"라는 뜻이지 영구 동결이 아니다.** 다른 도메인을 이관하다가 이미 ✅된 파일에 빠진 게 드러나면 다시 수정한다 — 예: `ObjectStorage`(`storage_validator.py`)는 완료 표시된 뒤에도 `createResonator` 이관 중 Spring 서블릿 레벨 제약(`IMAGE_SIZE_EXCEEDED`, 500KB 업로드 제한)이 누락된 게 드러나 다시 수정됨.

### 도메인 표에 안 들어가는 설정/필터/클라이언트 (entity/repository/service/controller가 아님)

| Spring 파일 | 상태 |
| --- | --- |
| `config/CorsConfig.java` | ✅ `fastapi/app/main.py`의 `CORSMiddleware`로 이관 (허용 origin/method/header 동일) |
| `filter/ExecutionTimeFilter.java` | ✅ `fastapi/app/main.py`의 `execution_time_middleware`로 이관 |
| `config/WebClientConfig.java` | **이관 대상 아님** — `FastApiClient`와 함께 인프로세스 호출로 대체되어 더 이상 필요 없음 |
| `client/FastApiClient.java` | **이관 대상 아님** — `createResonator`가 `resonator_profile_service.extract_info()`를 직접 호출하면서 Spring↔FastAPI 간 HTTP 왕복 자체가 없어짐 |

새 Spring 파일을 이관 대상에 편입할 땐 표에 행을 추가한다 (예: `FinalStat`을 실제로 옮기기 시작하면 그 행만 갱신하면 되고, 다른 행에 영향 없음).

## 아키텍처

```
fastapi/app/
  routers/      # FastAPI 라우터 (Spring의 controller에 대응)
  services/     # 비즈니스 로직 (Spring의 service에 대응)
  schemas/      # Pydantic 모델 (Spring의 dto에 대응)
  clients/      # 외부 API 클라이언트 (Google Vision 등)
  exceptions/   # CustomException + ErrorCode + exception_handler 패턴
  config/       # 상수, 로거 설정
  mapper/       # 데이터 변환

spring/src/main/java/io/github/wavesync/   # 이관 대상, 이관 완료 전까지 참고용으로 유지
infra/
  docker-compose.yml   # postgres, minio, spring, fastapi 로컬 실행
  postgres/*.sql        # 마스터 테이블 초기 데이터
```

### 스토리지 추상화 패턴 (FastAPI로 이관 시 반드시 유지)

Spring에는 `ObjectStorageService` 인터페이스 + `@Profile("dev"/"prod")`로 MinIO/Supabase 구현체를 분기하는 패턴이 있다. FastAPI로 옮길 때도 이 추상화를 유지해야 한다 — 환경변수(`APP_ENV`)로 dev/prod 구현체를 선택하는 방식으로 재현할 것. 서비스 로직이 어떤 스토리지를 쓰는지 몰라도 되게 만드는 게 핵심이다.

## 개발 환경 실행

```bash
# 전체 스택 실행 (postgres, minio, spring, fastapi)
cd infra && docker-compose up

# FastAPI만 로컬로 실행 (postgres/minio는 docker-compose로 띄운 상태에서)
cd fastapi && uvicorn app.main:app --reload --port 8000

# Spring만 로컬로 실행
cd spring && ./gradlew bootRun
```

- FastAPI: `http://localhost:8000`, API prefix는 `/api`
- Spring: `http://localhost:8080`
- Postgres: `localhost:5432` (db/user/pw 전부 `wawu`)
- MinIO 콘솔: `http://localhost:9001` (admin/password123)

## 코드 스타일 (FastAPI 기준, 이관 시 이 컨벤션을 따를 것)

- 요청/응답은 `schemas/request.py`, `schemas/response.py`에 Pydantic 모델로 정의 (`Field`, `default_factory` 적극 사용)
- 예외는 `CustomException(ErrorCode.XXX)` 형태로 발생시키고, `ErrorCode`는 `exceptions/error_code.py`의 Enum에 추가. 전역 처리는 `exception_handler.py`가 담당하므로 라우터에서 try/except로 감싸지 않는다
- 라우터는 얇게 유지 — 실제 로직은 `services/`로 위임 (`resonator_router.py` → `resonator_profile_service.py` 패턴 참고)
- 도메인별로 파일을 쪼갠다 (Spring 쪽 entity/repository/service 단위와 1:1 대응시키는 걸 기본으로 함)
- **트랜잭션 커밋은 서비스 계층에서 명시적으로.** `get_db()`는 자동 commit하지 않고 미처리 예외에 rollback만 한다. `get_db()`의 `yield` 이후 코드는 FastAPI가 응답을 이미 전송한 뒤 실행돼서, 거기서 commit하면 실패해도 클라이언트는 200을 받은 상태가 된다. 쓰기(insert/update/delete)를 하는 서비스 함수는 **응답 객체를 만들기 전에** `db.commit()`을 직접 호출한다 (응답에 쓸 값은 commit이 인스턴스를 expire시키므로 commit 전에 확보). commit 실패 시 `SQLAlchemyError`가 라우터를 거쳐 `sqlalchemy_exception_handler`로 잡혀 500(`DATABASE_ERROR`)이 나간다. 여러 서비스 함수가 공유하는 내부 헬퍼(`_delete` 등)는 commit하지 않고 호출자가 트랜잭션 경계를 잡는다. repository 함수도 commit하지 않는다 (`# 커밋은 호출부 책임` 주석 유지)

## API 응답 형식

Spring은 `ApiResponseDto<T>{code, message, data}` 공용 래퍼를 쓰고, `@JsonInclude(NON_NULL)`로 `data`가 없을 때(에러 응답 등) 필드 자체를 생략한다. 에러는 `ErrorResponseDto.of(code, message)`로 `data` 없이 내려간다.

- `code` 필드는 `ErrorCode`의 `code` 문자열에서 온다 — 그래서 `error_code.py`가 `(status, code, message)` 3-튜플이다
- **성공 응답은 `schemas/api_response.py`의 제네릭 `ApiResponse[T]{code, message, data}`로 확정됐다** (ResonatorService 이관 때 결정). 라우터에서 `response_model=ApiResponse[SomeDto]` + `response_model_exclude_none=True`로 선언하면 `data`가 `None`일 때 Jackson `@JsonInclude(NON_NULL)`과 동일하게 필드 자체가 응답에서 빠진다. 새 도메인 라우터를 만들 때도 이 패턴을 그대로 쓸 것 (도메인별 개별 응답 모델 새로 정의하지 않기). 과거엔 이관 전부터 있던 `ResonatorImageResponse`(`/resonators/images` 엔드포인트)만 예외로 유지했으나, 이 엔드포인트는 프레임워크 통합으로 더 이상 쓰이지 않아 삭제됐다 — 현재는 예외 없이 전부 이 패턴을 따른다
- `exceptions/exception_handler.py`는 3단계로 처리한다: `CustomException`(도메인 예외, `{code, message}`) → `SQLAlchemyError`(Spring `DataAccessException` 대응, `DATABASE_ERROR`) → 나머지 전부(Spring `Exception` catch-all 대응, `INTERNAL_SERVER_ERROR` + `detail`). `main.py`에 `add_exception_handler`로 이 순서와 무관하게 각자 등록돼 있고, Starlette가 예외 타입의 MRO로 가장 구체적인 핸들러를 골라준다

### 의도적으로 Spring과 다르게 둔 것 (ResonatorService 이관 시 확정)

- **검증 실패 응답 코드**: Pydantic 검증 실패 시 FastAPI는 기본 422를 반환한다. Spring `GlobalExceptionHandler`엔 `MethodArgumentNotValidException` 전용 핸들러가 없어 기본값(400)이 나간다 — 프레임워크 기본 동작 차이라 의도적으로 맞추지 않았다. **프론트가 해당 엔드포인트를 FastAPI로 전환할 때 이 차이를 다시 확인할 것**
- **`getResonatorSummary`의 한글 정렬**: Spring `Collator.getInstance(Locale.KOREAN)` 대신 Python 기본 문자열 비교(`sort(key=...)`)를 쓴다. 현대 한글 음절(U+AC00~U+D7A3)은 유니코드 코드포인트 순서가 사전식 순서와 사실상 일치해 현재 데이터셋(순수 한글 공명자 이름)엔 결과가 동일하다. **숫자/영문이 섞인 이름이 마스터 데이터에 추가되면 재검토 필요** (필요 시 `PyICU` 도입 검토)

## Enum 처리 (DB 잘못된 값 방지)

Spring은 Java `enum` + `@Enumerated(EnumType.STRING)`으로 잘못된 값이 DB에 들어가는 걸 막는다. DB 컬럼 자체엔 CHECK 제약이 없다 (VARCHAR). FastAPI에서는 동일하게:

- Python `class XxxType(str, Enum)`으로 Spring enum(`StatType`, `Element`, `BranchPosition`, `NodePosition` 등)을 값 그대로 재현
- SQLAlchemy 컬럼에 `Column(SAEnum(XxxType, native_enum=False, length=N))`로 매핑 — **`native_enum=False`를 반드시 명시할 것**. 기본값(`True`)으로 두면 Postgres에 실제 `ENUM` 타입을 새로 만들게 되어 지금 DB 스키마(VARCHAR)와 어긋나고 Spring 쪽과 스키마가 갈라진다
- 요청/응답 Pydantic 스키마에도 같은 Enum을 써서 API 단에서 자동으로 422 검증되게 할 것
- 이관 완료 전까지는 스키마를 바꾸지 않는 게 원칙이므로, DB 레벨 진짜 `ENUM`/`CHECK` 제약 도입은 전체 이관이 끝난 뒤 별도로 논의

## Postgres 최적화 설정 (이관 시 성능 회귀 주의)

Spring 쪽에서 트러블슈팅으로 확보한 최적화가 있다. FastAPI + SQLAlchemy로 옮길 때 동등한 효과를 반드시 재현할 것 — 그냥 옮기면 성능이 퇴행한다.

- **N+1 방지**: Hibernate `default_batch_fetch_size: 100` → SQLAlchemy에서는 `selectinload`/`joinedload`로 연관 엔티티를 배치 조회
- **Batch insert**: ID 생성을 SEQUENCE(`INCREMENT BY 50`, `CACHE 50`) + `hibernate.jdbc.batch_size: 50` 조합으로 처리 중 (기존 IDENTITY 방식은 batch insert 불가). SQLAlchemy에서도 시퀀스 기반 batch insert를 유지할 것
- 마스터 테이블 초기화는 `infra/postgres/*.sql` (01~04번, 순서대로 실행됨)

## 제약사항 (이관 여부와 무관하게 항상 지킬 것)

- **무료 인프라만 사용.** 유료 티어로 전환되는 설정을 넣지 말 것 (Cloud Run, Vercel, Supabase 모두 무료 플랜 기준)
- **Google Vision API 호출은 최소화.** 요청 1건당 API 1회 호출로 묶여 있다 (과거 7회 → 1회로 최적화한 이력 있음). 이미지 크롭/병합 후 1번만 호출하는 구조(`preprocess_service.py`)를 건드릴 땐 호출 횟수가 늘어나지 않는지 확인할 것
- 개인 사용 목적의 소규모 서비스이므로, 과도한 확장성 설계(멀티테넌시, 대규모 트래픽 대응 등)는 지양

## 배포

- `.github/workflows/deploy-fastapi.yml`, `deploy-spring.yml`로 각각 배포됨 (Spring 이관 완료 후 `deploy-spring.yml`은 제거 예정)

## 이관 완료 후 정리 작업 (완료됨)

`spring/` 제거 후 진행하기로 했던 두 작업 모두 완료됨. 이력용으로 남긴다.

- **Enum DB 값 소문자 전환** — ✅ 완료. `Element`/`StatType`/`BranchPosition`/`NodePosition`을 소문자 code 값으로 통일하고(`models/*.py`), DB 마스터 데이터와 CHECK 제약도 소문자로 전환(`infra/postgres/01~04`). SAEnum 컬럼은 `values_callable=enum_values`로 멤버 이름이 아니라 값을 저장한다. 값과 code가 같아져 `schemas/common.py`의 커스텀 직렬화 로직은 제거됨.
- **SEQUENCE INCREMENT BY / CACHE 축소** — ✅ 완료. `infra/postgres/01_init.sql`에서 `user_node_seq`를 `INCREMENT BY 10 CACHE 10`(공명 노드 10개 고정 생성), `user_echo_sub_seq`를 `INCREMENT BY 25 CACHE 25`(게임 내 이론상 최대 5에코 × 5서브)로 낮췄다. SQLAlchemy는 행마다 `nextval()`을 호출하고 클라이언트 사이드 hi-lo가 없으므로 INCREMENT 값과 무관하게 PK 충돌은 없고 ID 조밀도만 바뀐다. (스키마 변경은 별도 마이그레이션 파일 없이 `01_init.sql`을 직접 갱신하는 게 이 프로젝트 컨벤션)
