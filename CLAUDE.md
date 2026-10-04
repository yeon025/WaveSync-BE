# WaveSync-BE

《명조: 워더링 웨이브》 캐릭터 프로필 이미지를 분석해 스펙을 계산해주는 개인 서비스의 백엔드.

## Spring Boot → FastAPI 마이그레이션 (완료)

**Spring Boot에 있던 모든 로직을 FastAPI로 이전하는 마이그레이션이 완료되었다.** `spring/` 디렉토리는 이미 삭제되었고, 현재 저장소에는 `fastapi/`만 남아 있다. CRUD를 포함한 모든 기능은 현재 FastAPI가 전담하며, 코드 구조도 Spring 파일과의 1:1 대응이 아니라 `profile_extraction/`·`resonator/` 중심의 FastAPI 도메인 구조로 정리되어 있다 (아래 "아키텍처" 참고).

아래 "이관 진행 상황" 표와 "MIGRATED 주석 규칙"은 **이관 작업 당시의 이력 기록**이다. `spring/`이 삭제된 지금은 실제로 참고할 Spring 코드가 없으므로, 새 작업을 이 표 기준으로 진행하거나 갱신할 필요는 없다.

- 이관 대상이었던 범위: `spring/src/main/java/io/github/wavesync/` 하위의 `entity`, `repository`, `service`, `controller`, `dto` 전체
- 이관 순서 원칙(당시): 도메인 하나를 통째로 옮긴다 (entity → repository → service → router 순서로, 중간에 끊지 않기)
- 이관이 끝나기 전까지는 비교 기준(reference)으로 Spring 코드를 남겨뒀으나, 이관 완료 후 `spring/` 자체를 삭제했다

#### MIGRATED 주석 규칙 (과거 이력 — spring/ 삭제로 더 이상 유효하지 않음)

- 도메인 엔티티/서비스/컨트롤러 파일: 이관 완료 시 `// MIGRATED to fastapi/app/...` 주석을 남겼다
- **공용 enum 정의 파일(`StatType.java`, `Element.java`, `BranchPosition.java`, `NodePosition.java` 등)은 표시하지 않았다.** 여러 도메인이 나눠 쓰는 값 정의라 "이관 완료" 신호로 부적절했기 때문 — 추적은 그 enum을 컬럼으로 쓰는 엔티티 파일 쪽에서만 했다

## 이관 진행 상황 (완료된 이력)

Spring 파일 단위로 쪼개서 추적했던 기록이다. 모든 행이 완료되었고 더 갱신할 필요는 없다. 실제 클래스가 존재하지 않았던 칸은 `-`.

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
| 이미지 분석    | OCR/Vision                                                                           | ✅ 이미 FastAPI에 있었음  | -                               | -       | -                   |

범례: ✅ 완료 / `-` 해당 없음(Spring에도 그 파일이 없었음).

**✅는 "당시 파악된 범위에서 완료"라는 뜻이었다.** 실제로 다른 도메인을 이관하던 중 이미 ✅ 표시된 파일에서 누락이 발견되어 다시 수정된 사례가 있었다 — 예: `ObjectStorage`(`storage_validator.py`)는 완료 표시된 뒤에도 `createResonator` 이관 중 Spring 서블릿 레벨 제약(`IMAGE_SIZE_EXCEEDED`, 500KB 업로드 제한)이 누락된 게 드러나 다시 수정됐다.

### 도메인 표에 안 들어갔던 설정/필터/클라이언트 (entity/repository/service/controller가 아님)

| Spring 파일 | 상태 |
| --- | --- |
| `config/CorsConfig.java` | ✅ `fastapi/app/main.py`의 `CORSMiddleware`로 이관 완료 (허용 origin/method/header 동일) |
| `filter/ExecutionTimeFilter.java` | ✅ `fastapi/app/main.py`의 `execution_time_middleware`로 이관 완료 |
| `config/WebClientConfig.java` | 이관 대상 아니었음 — `FastApiClient`와 함께 인프로세스 호출로 대체되어 더 이상 필요 없어짐 |
| `client/FastApiClient.java` | 이관 대상 아니었음 — `createResonator`가 `profile_extraction_service.extract_info()`(현재 `app/profile_extraction/profile_extraction_service.py`)를 직접 호출하면서 Spring↔FastAPI 간 HTTP 왕복 자체가 없어짐 |

이관이 완료되어 이 표에 새 Spring 파일이 추가될 일은 더 이상 없다.

## 아키텍처

```
fastapi/
  app/                  # FastAPI 애플리케이션 코드의 루트
    main.py
    config/
    db/
    exceptions/
    schemas/
    storage/
    profile_extraction/
    resonator/
  images/                # app 패키지와 분리된 이미지 리소스 (템플릿 이미지 + 런타임 임시 파일)
  credentials/           # 로컬 개발용 Google Vision 서비스 계정 키 등 (git 추적 안 함)
infra/
  docker-compose.yml     # postgres, minio, fastapi 로컬 실행
  postgres/*.sql          # 마스터 테이블 초기 데이터
```

### app/main.py

애플리케이션 생성과 조립을 담당한다.

- FastAPI app 생성
- CORS 설정 (`CORSMiddleware`)
- 요청/응답 실행시간 로깅 미들웨어 등록
- `/health` 헬스체크
- 도메인 라우터(`resonator/router.py`) 등록
- 전역 예외 핸들러(`exceptions/exception_handler.py`) 등록

작은 앱 설정이나 미들웨어 로직을 위해 불필요하게 별도 폴더(`middleware/` 등)로 분리하지 않는다.

### app/config/

애플리케이션 전역 설정 관련 코드. 현재 `logger.py`를 포함한다.

### app/db/

SQLAlchemy 기반 DB 설정과 세션 관리를 담당한다 (`base.py`의 선언적 Base, `session.py`의 엔진/세션 라이프사이클).

### app/exceptions/

애플리케이션 예외(`custom_exception.py`)와 에러 코드(`error_code.py`), 전역 예외 핸들러(`exception_handler.py`)를 관리한다.

### app/schemas/

여러 도메인에서 공통으로 사용하는 API Schema를 관리한다. 현재 `api_response.py`(제네릭 `ApiResponse[T]` 래퍼)를 포함한다.

도메인 전용 Schema는 각 도메인 내부에 둔다.

- `app/profile_extraction/schemas.py`
- `app/resonator/schemas.py`

### app/storage/

객체 저장소 관련 기능을 관리한다. `object_storage_service.py`(추상 인터페이스), `minio_object_storage_service.py`/`supabase_storage_service.py`(구현체), `object_storage_factory.py`(환경변수 `APP_ENV` 기준 구현체 선택), `storage_validator.py`(업로드 이미지 검증)를 포함한다. 이 dev/prod 구현체 분기 패턴은 Spring 시절 `ObjectStorageService` 인터페이스 + `@Profile("dev"/"prod")` 설계를 FastAPI 이관 때 그대로 재현한 것이며, 이관이 끝난 지금도 유지한다 — 서비스 로직이 어떤 스토리지를 쓰는지 몰라도 되게 만드는 게 핵심이다.

### app/profile_extraction/

게임 내 공명자 프로필 화면 스크린샷 이미지에서 데이터를 추출하는 기능을 담당한다. 이미지 크롭/병합, OCR(Google Vision API 호출 포함), Echo 이미지 매칭, Echo 텍스트 파싱, Resonance Chain(돌파 여부) 판별까지 포함한다. 처리 단계(OCR, 에코) 기준으로 하위 폴더를 나눈다. 추출 결과를 마스터 데이터로 검증하는 일은 resonator 도메인(`resonator/extract_profile_validation_service.py`)이 맡으므로, profile_extraction은 DB와 resonator에 의존하지 않는다 (Echo 아이콘 매칭용 이미지를 읽기 위해 `app/storage`만 사용한다).

```
profile_extraction/
├── profile_extraction_service.py   # extract_info: 이미지 다운로드 후 아래 단계 전체를 조합하는 오케스트레이터
├── resonance_chain_service.py      # 돌파 원 영역 크롭 + 템플릿 이미지 해시 비교로 돌파 횟수 판별
├── paths.py                        # 여러 모듈이 공유하는 경로 (BASE_DIR, 런타임 임시 파일용 TMP_DIR)
├── schemas.py                      # 추출 결과 DTO (ExtractedStat/Echo/ExtractData)
├── ocr/
│   ├── text_region_builder.py      # 텍스트 영역 크롭 후 세로로 이어붙여 Vision 호출을 1회로 만든다
│   ├── ocr_service.py              # Vision 호출, 응답 단어를 줄로 병합, 텍스트 정제, 공명자/무기/에코 줄 분리
│   └── vision_client.py            # Google Vision 클라이언트 생성 (dev는 서비스 계정 키 파일 사용)
└── echo/
    ├── echo_matching_service.py    # 에코 아이콘 크롭, ORB 특징점 매칭, echo-images 특징점 캐시(메모리 + 디스크)
    └── echo_text_parser.py         # OCR 줄을 Echo(메인/보조/서브 옵션)로 파싱
```

### app/resonator/

명조 캐릭터(공명자)와 관련된 핵심 도메인을 담당한다. Resonator, Weapon, Echo, Resonance Node, Final Stat 엔티티와 스탯 계산, 에코 점수, DB 접근, API Router까지 이 폴더 하나에 모여 있다 (Echo/Resonance Node/Weapon은 독립된 라우터·서비스가 없는 Resonator의 하위 개념이라 별도 최상위 도메인으로 분리하지 않았다).

**`resonator/`는 `models/`, `repositories/`, `services/`처럼 계층별로 분리하지 않는다.** 하나의 도메인이나 기능을 구성하는 관련 코드(모델, repository, enum, 매핑 등)를 함께 배치해, 해당 영역의 코드를 찾고 수정하기 쉽게 유지한다. 그래서 하위 폴더마다 들어 있는 파일의 종류가 다르며(`master/`에는 service가 없고 `echo_score/`에는 계산·서비스가 있다), 이는 의도한 구조다. 여러 영역을 가로지르는 업무 흐름(CRUD, 등록, 스펙 계산)은 특정 하위 폴더에 넣지 않고 루트에 둔다.

```
resonator/
├── router.py                              # API 엔드포인트 (얇게 유지, 실제 로직은 service로 위임)
├── resonator_service.py                   # 조회/수정/삭제 CRUD, 여러 Repository 조합과 트랜잭션, 응답 조립
├── resonator_registration_service.py      # create_resonator: 업로드 → 추출 → 검증 → 조립 → 스펙/점수 계산 → 커밋 → LLM 설명 저장
├── extract_profile_validation_service.py  # 프로필 추출 결과를 마스터 데이터/게임 수치로 검증
├── user_resonator_factory.py              # 추출 결과 + 마스터 데이터로 저장 전 UserResonator 애그리게잇 조립 (DB 접근 없음)
├── spec_calculation_service.py            # 최종 스탯 계산 (등록과 수정에서 공유하는 순수 계산 로직)
├── schemas.py                             # Resonator 도메인 request/response 스키마
├── stat_type.py                           # 여러 영역이 공유하는 StatType enum
├── echo_sub_stat_values.py                # 에코 서브옵션 유효 수치 (검증과 점수 계산이 공유)
├── master/                                # 게임 마스터 데이터
├── resonance_node/                        # 공명 노드
├── user_resonator/                        # 사용자 공명자 애그리게잇
└── echo_score/                            # 에코 점수 계산과 설명
```

- **`master/`**: 공명자(`resonator_master.py`, `Element` enum 포함)와 무기(`weapon_master.py`) 마스터 모델, 그리고 테이블별 repository(`resonator_master_repository.py`, `weapon_master_repository.py`)를 둔다. 별도 service는 없고 `extract_profile_validation_service`, `resonator_service` 등이 repository를 직접 사용한다.
- **`resonance_node/`**: 노드 마스터 모델(`resonance_node_master.py`), 사용자 노드 모델(`user_resonance_node.py`), 노드 위치 enum(`node_positions.py`의 `BranchPosition`/`NodePosition`), 노드 위치를 스탯 값으로 바꾸는 `resonance_node_mapper.py`(`get_stat`)를 둔다. 전용 repository는 없다. 마스터 노드는 `ResonatorMaster.resonance_node_master` 관계로, 사용자 노드는 `user_resonator_repository`가 함께 다룬다.
- **`user_resonator/`**: 사용자가 등록한 공명자 애그리게잇(`UserResonator`/`FinalStat`/`UserEcho`/`UserEchoSub` 모델)과 `user_resonator_repository.py`를 둔다. 하위 테이블(노드/에코/에코 서브/최종 스탯)은 `UserResonator` 없이 단독으로 조회·저장·삭제되는 경로가 없어서, repository 하나가 애그리게잇 전체를 담당한다. 별도 service는 없고 루트의 service들이 repository를 조합한다.
- **`echo_score/`**: 에코 서브속성 점수 계산과 LLM 설명을 하나의 기능 단위로 묶는다. `echo_score_calculator.py`(가중치/점수/등급 순수 계산), `echo_grade.py`(`EchoGrade` enum), `resonator_damage_master.py`(점수 계산 설정 마스터 모델, `DamageType`/`ScalingStat` enum 포함)와 `resonator_damage_master_repository.py`, `echo_score_service.py`(점수 계산 후 에코에 반영), `echo_explanation_service.py`(LLM 입력 payload 조립과 설명 생성), `gemini_client.py`(Gemini SDK 호출)로 구성된다.
- **enum 위치**: 한 모델이나 한 기능에서만 쓰는 enum은 파일을 따로 만들지 않고 그 모델/모듈 파일에 함께 둔다 (`Element` → `master/resonator_master.py`, `BranchPosition`/`NodePosition` → `resonance_node/node_positions.py`, `DamageType`/`ScalingStat` → `echo_score/resonator_damage_master.py`). 여러 영역이 공유하는 `StatType`만 루트의 `stat_type.py`에 둔다.
- **Repository 규칙**: 마스터 테이블(`resonator_master`/`weapon_master`/`resonator_damage_master`)은 테이블별로 repository를 두고, 사용자 데이터는 `user_resonator_repository.py` 하나가 담당한다. **Generic Repository나 BaseRepository로 통합하지 않는다.** Repository는 API Response Schema를 생성하지 않고 ORM 객체 또는 DB 조회 결과만 반환한다 (상세 규칙은 아래 "ORM → Schema 변환 규칙" 참고).
- **`resonator/schemas.py`**: Resonator 도메인의 Request/Response Schema를 관리한다. 단순한 ORM → Schema 변환은 Schema의 `from_*` classmethod로 처리한다.
- **`resonator/resonator_service.py`**: Resonator 관련 비즈니스 로직과 여러 Repository의 조합, 트랜잭션 경계를 담당한다. 필요한 경우 Repository 조회 결과를 API Schema로 조립한다.
- **`resonator/spec_calculation_service.py`**: 명조 캐릭터의 스탯 계산과 관련된 핵심 도메인 로직을 담당한다. 등록(`resonator_registration_service`)과 수정(`resonator_service.update_resonator`)이 함께 사용한다.

## 개발 환경 실행

```bash
# 전체 스택 실행 (postgres, minio, fastapi)
cd infra && docker-compose up

# FastAPI만 로컬로 실행 (postgres/minio는 docker-compose로 띄운 상태에서)
cd fastapi && uvicorn app.main:app --reload --port 8000
```

- FastAPI: `http://localhost:8000`, API prefix는 `/api`
- Postgres: `localhost:5432` (db/user/pw 전부 `wawu`)
- MinIO 콘솔: `http://localhost:9001` (admin/password123)

## 코드 스타일 (FastAPI 컨벤션)

- 요청/응답 Pydantic 모델은 도메인별 `schemas.py`에 정의한다 (`Field`, `default_factory` 적극 사용) — 공통 API 응답 래퍼는 `app/schemas/api_response.py`, 프로필 추출 DTO는 `app/profile_extraction/schemas.py`, Resonator 도메인 request/response는 `app/resonator/schemas.py`에 둔다
- 예외는 `CustomException(ErrorCode.XXX)` 형태로 발생시키고, `ErrorCode`는 `exceptions/error_code.py`의 Enum에 추가. 전역 처리는 `exception_handler.py`가 담당하므로 라우터에서 try/except로 감싸지 않는다
- 라우터는 얇게 유지 — 실제 로직은 도메인 서비스로 위임한다 (`resonator/router.py` → `resonator/resonator_service.py` 패턴 참고)
- 도메인/기능 단위로 파일을 묶는다 (`profile_extraction/`, `resonator/`처럼 하나의 책임 영역을 하나의 폴더에 모은다). `models/`/`repositories/`처럼 계층별 폴더로 나누지 않고, 한 도메인·기능의 모델·repository·enum·매핑을 같은 폴더에 둔다
- **트랜잭션 커밋은 서비스 계층에서 명시적으로.** `get_db()`는 자동 commit하지 않고 미처리 예외에 rollback만 한다. `get_db()`의 `yield` 이후 코드는 FastAPI가 응답을 이미 전송한 뒤 실행돼서, 거기서 commit하면 실패해도 클라이언트는 200을 받은 상태가 된다. 쓰기(insert/update/delete)를 하는 서비스 함수는 **응답 객체를 만들기 전에** `db.commit()`을 직접 호출한다 (응답에 쓸 값은 commit이 인스턴스를 expire시키므로 commit 전에 확보). commit 실패 시 `SQLAlchemyError`가 라우터를 거쳐 `sqlalchemy_exception_handler`로 잡혀 500(`DATABASE_ERROR`)이 나간다. 여러 서비스 함수가 공유하는 내부 헬퍼는 commit하지 않고 호출자가 트랜잭션 경계를 잡는다. repository 함수도 commit하지 않는다 (`# 커밋은 호출부 책임` 주석 유지)

### ORM → Schema 변환 규칙

- 단순한 ORM 모델 → API Schema 변환은 해당 Schema의 `from_*` classmethod에서 처리한다 (예: `resonator/schemas.py`의 `ResonatorStat.from_final_stat`, `WeaponDetail.from_user_resonator`, `WeaponSetting.from_user_resonator`, `EchoDetail.from_user_echo`).
- 별도의 mapper 파일을 새로 만들지 않는다.
- 여러 도메인 객체를 조합하거나 복잡한 변환 로직이 필요한 경우에만 기존 mapper(`resonator/resonance_node/resonance_node_mapper.py` 등) 또는 Service에서 처리한다.
- Repository에서는 API Schema를 생성하지 않는다.
- Repository는 ORM 객체 또는 DB 조회 결과만 반환한다.
- Service는 Repository의 결과를 조합하여 API Schema를 반환할 수 있다.

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
- 이관 당시엔 스키마를 바꾸지 않는 게 원칙이라 DB 레벨 진짜 `ENUM`/`CHECK` 제약 도입을 보류했다. 이관이 완료된 지금도 아직 도입하지 않았으며, 필요해지면 별도로 논의한다

## Postgres 최적화 설정 (성능 회귀 주의)

Spring 쪽에서 트러블슈팅으로 확보했던 최적화를 FastAPI + SQLAlchemy로 이관하면서 동등하게 재현했다. 이 부분을 다시 건드릴 땐 아래 효과가 퇴행하지 않는지 확인할 것.

- **N+1 방지**: Hibernate `default_batch_fetch_size: 100` → SQLAlchemy에서는 `selectinload`/`joinedload`로 연관 엔티티를 배치 조회
- **Batch insert**: ID 생성을 SEQUENCE(`INCREMENT BY 50`, `CACHE 50`) + `hibernate.jdbc.batch_size: 50` 조합으로 처리 중 (기존 IDENTITY 방식은 batch insert 불가). SQLAlchemy에서도 시퀀스 기반 batch insert를 유지할 것
- 마스터 테이블 초기화는 `infra/postgres/*.sql` (01~05번, 순서대로 실행됨)

## 제약사항 (이관 여부와 무관하게 항상 지킬 것)

- **무료 인프라만 사용.** 유료 티어로 전환되는 설정을 넣지 말 것 (Cloud Run, Vercel, Supabase 모두 무료 플랜 기준)
- **Google Vision API 호출은 최소화.** 요청 1건당 API 1회 호출로 묶여 있다 (과거 7회 → 1회로 최적화한 이력 있음). 이미지 크롭/병합 후 1번만 호출하는 구조(`app/profile_extraction/ocr/text_region_builder.py`의 `crop_and_stack` → `ocr/ocr_service.py`의 `extract_text`)를 건드릴 땐 호출 횟수가 늘어나지 않는지 확인할 것
- 개인 사용 목적의 소규모 서비스이므로, 과도한 확장성 설계(멀티테넌시, 대규모 트래픽 대응 등)는 지양

## 배포

- `.github/workflows/deploy-fastapi.yml`로 배포됨 (`deploy-spring.yml`은 Spring 이관 완료로 제거됨)

## 이관 완료 후 정리 작업 (완료됨)

`spring/` 제거 후 진행하기로 했던 두 작업 모두 완료됨. 이력용으로 남긴다.

- **Enum DB 값 소문자 전환** — ✅ 완료. `Element`/`StatType`/`BranchPosition`/`NodePosition`을 소문자 code 값으로 통일하고(현재 `resonator/stat_type.py`, `resonator/master/resonator_master.py`, `resonator/resonance_node/node_positions.py`), DB 마스터 데이터와 CHECK 제약도 소문자로 전환(`infra/postgres/01~04`). SAEnum 컬럼은 `values_callable=enum_values`로 멤버 이름이 아니라 값을 저장한다. 값과 code가 같아져 당시 `schemas/common.py`(현재는 `resonator/schemas.py`로 통합됨)에 있던 커스텀 직렬화 로직은 제거됨.
- **SEQUENCE INCREMENT BY / CACHE 축소** — ✅ 완료. `infra/postgres/01_init.sql`에서 `user_node_seq`를 `INCREMENT BY 10 CACHE 10`(공명 노드 10개 고정 생성), `user_echo_sub_seq`를 `INCREMENT BY 25 CACHE 25`(게임 내 이론상 최대 5에코 × 5서브)로 낮췄다. SQLAlchemy는 행마다 `nextval()`을 호출하고 클라이언트 사이드 hi-lo가 없으므로 INCREMENT 값과 무관하게 PK 충돌은 없고 ID 조밀도만 바뀐다. (스키마 변경은 별도 마이그레이션 파일 없이 `01_init.sql`을 직접 갱신하는 게 이 프로젝트 컨벤션)
