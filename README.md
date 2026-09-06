# 명조: 워더링 웨이브 스펙 계산기 서비스

> 《명조: 워더링 웨이브》 캐릭터 프로필 이미지에서 텍스트를 추출해 최종 스펙을 계산해주는 개인 서비스

📅 개발 기간: 2026.05 ~ Present (배포 완료, 지속 개선 중)<br>
👤 인원: 1명 (기획 · 설계 · 개발 · 배포 전 과정 개인 진행)

<br>

## 목차

- [프로젝트 개요](#프로젝트-개요)
- [제약사항](#제약사항)
- [아키텍처](#아키텍처)
- [기술 스택](#기술-스택)
- [트러블슈팅](#트러블슈팅)
- [회고](#회고)

<br>

## 프로젝트 개요

**문제 정의**

- 캐릭터 스펙 조회가 게임 실행을 전제로 하기 때문에, 게임을 켤 수 없는 환경에서는 정보에 접근할 수 없습니다.

**해결 방안**

- 게임 데이터에 직접 접근할 수 없으므로, 공식 디스코드에 공유되는 프로필 이미지에서 캐릭터 정보를 추출해 저장함으로써 스펙을 조회할 수 있게 했습니다.

**핵심 기능**

- **캐릭터 등록** : 캐릭터 이미지를 업로드하면 이미지를 분석해 자동으로 캐릭터 정보를 등록합니다.
- **캐릭터 목록 조회** : 등록된 캐릭터를 이미지와 이름이 담긴 카드 형태로 조회합니다.
- **캐릭터 상세 스펙 조회** : 캐릭터를 선택하면 상세 스펙 정보를 확인할 수 있습니다.
- **캐릭터 삭제** : 등록된 캐릭터와 관련 정보를 삭제합니다.

<br>

## 제약사항

- 《명조: 워더링 웨이브》는 게임 IP 특성상 상업적 확장이 제한되어, 처음부터 **개인 사용 목적의 소규모 서비스**로 범위를 한정하고 **무료 인프라만으로 운영**하는 것을 전제로 설계했습니다.
- 이 제약이 이후 기술 스택 선택(무료 티어 중심의 인프라 구성)과 아키텍처 설계(무료 API 할당량 최적화) 전반에 영향을 주었습니다.

<br>

## 아키텍처

![architecture](./images/architecture.png)

<br>

## 기술 스택

| 구분       | 스택                                    |
| ---------- | --------------------------------------- |
| 프론트엔드 | Next.js                                 |
| 백엔드     | FastAPI · PostgreSQL · Supabase · MinIO |
| 인프라     | Docker · Vercel · Google Cloud Run      |
| CI/CD      | GitHub Actions                          |

<br>

## 트러블슈팅

### Google Vision API 호출 최적화 (7회 → 1회)

**[ 문제 상황 ]**

요청 1건당 Vision API를 7번 호출하는 구조였고, 이는 월 무료 할당량(1,000건)을 빠르게 소진할 위험이 있었습니다.

**[ 최종 선택 ]**

필요한 텍스트가 담긴 구역만 잘라내고, 세로로 병합해 한 장의 이미지로 만든 뒤 Vision API를 한 번만 호출하도록 개선했습니다.

**[ 결과 ]**

API 호출 횟수 7회 → 1회로 단축, 무료 할당량 내에서 안정적으로 운영 가능해졌습니다.

<table border="0">
  <tr>
    <td align="center" valign="middle" style="border: none;">
      <img src="./images/before_crop.png" width="90%" />
    </td>
    <td align="center" valign="middle" style="border: none;">
      <strong style="font-size: 30px;">➡️</strong>
    </td>
    <td align="center" valign="middle" style="border: none;">
      <img src="./images/after_crop.png" width="90%" />
    </td>
  </tr>
</table>

---

### FastAPI 컨테이너 실행 시 ModuleNotFoundError 발생

**[ 문제 상황 ]**

기존에 로컬 환경에서 직접 실행하며 개발하던 FastAPI 프로젝트를 Docker Compose 기반 개발 환경으로 전환했습니다. 기존 코드를 그대로 옮겼음에도 `docker-compose up`으로 컨테이너를 실행하자 다음과 같은 에러가 발생하며 서버가 아예 뜨지 않았습니다.

```
ModuleNotFoundError: No module named 'routers'
```

**[ 원인 분석 ]**

문제의 원인을 찾기 위해 Dockerfile과 실제 실행 구조를 하나씩 점검했습니다.

**Dockerfile 구조**
```dockerfile
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

- `WORKDIR /app`으로 컨테이너의 작업 디렉토리를 `/app`으로 지정했습니다.
- `COPY . .`으로 로컬의 `fastapi/` 폴더 전체(그 안에 다시 `app/` 폴더가 존재하는 구조)를 그대로 복사했습니다.
- 그 결과 컨테이너 내부에는 다음과 같은 **중첩 디렉토리 구조**가 생성되었습니다.
```
/app/                ← WORKDIR (sys.path 기준점)
  └── app/            ← 실제 소스 코드가 위치한 폴더
        ├── main.py
        ├── routers/
        ├── schemas/
        └── services/
```
- 실행 명령어가 `uvicorn app.main:app`이므로, Python은 `/app`을 기준으로 `app`이라는 패키지를 인식하고 그 안의 `main.py`를 로딩합니다.
- 이때 `main.py` 내부에 다음과 같이 작성되어 있던 import 구문이 문제였습니다.

```python
# main.py (수정 전)
from routers import resonator_router
```

- 이 코드는 `/app/routers`를 찾으려 하지만, 실제 경로는 `/app/app/routers`이기 때문에 모듈을 찾지 못해 `ModuleNotFoundError`가 발생한 것이었습니다.
- 반면 기존 로컬 개발 환경에서는 `fastapi/app` 폴더 내부에서 직접 실행했기 때문에 해당 폴더 자체가 최상위 기준점이 되어 `from routers import ...`가 정상적으로 동작했습니다. 즉, 코드 자체는 문제가 없었지만 실행 환경(로컬 실행 vs 컨테이너 실행)에 따라 모듈 탐색 경로(`sys.path`) 기준이 달라지면서 발생한 문제였습니다.

**[ 최종 선택 ]**

두 가지 해결 방법을 고려했습니다.

1. **Dockerfile을 수정**해서 `COPY app/ .`처럼 `app` 폴더의 내용물만 `/app`으로 복사해 중첩 구조 자체를 없애는 방법
2. **모든 import 경로를 `app.` 접두사를 포함한 절대 경로로 통일**해서 현재 디렉토리 구조에 코드를 맞추는 방법

프로젝트 구조를 그대로 유지하면서 배포 스크립트나 실행 명령어와의 일관성(`uvicorn app.main:app`)을 지키는 것이 더 안전하다고 판단해, 2번 방법(import 경로 통일)을 선택했습니다.

```python
# main.py (수정 후)
from app.routers import resonator_router
```

동일한 패턴으로 `mapper`, `services`, `validators`, `config` 등 프로젝트 내 모든 내부 모듈의 import 경로를 `app.`을 포함한 형태로 통일했습니다.

**[ 결과 ]**

- 컨테이너 실행 시 발생하던 `ModuleNotFoundError`가 해결되어 `docker-compose up`만으로 정상적으로 서버가 기동되었습니다.

<br>

## 회고

**기술 선택 재검토**

PostgreSQL은 초기에 스펙 계산용 함수 지원이 강점이라 판단해 선택했습니다. 하지만 실제 구현 과정에서는 계산 로직이 전부 FastAPI 애플리케이션 레이어로 옮겨가면서 그 장점을 살리지 못했습니다.<br>
기술 선택의 근거가 실제 구현 방향과 어긋날 수 있다는 걸 경험한 사례였습니다. 앞으로는 설계 초기에 "이 장점을 실제로 어느 레이어에서 활용할 것인지"까지 구체적으로 정하고 선택하려고 합니다.
