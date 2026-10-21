import threading
import time
from collections import defaultdict
from typing import Dict, List

# Redis 등 외부 저장소 없이 무료 인프라 제약을 지키기 위한 프로세스 메모리 기반 고정 윈도 제한기.
# 신규 게스트 계정 생성 경로에만 적용한다 (유효한 기존 세션 재사용은 제한하지 않음).
# 인스턴스 재시작/스케일 시 카운터가 공유되지 않는 한계가 있다 (개인용 소규모 서비스 범위에서 수용).

_MAX_NEW_SESSIONS = 10
_WINDOW_SECONDS = 60 * 60

_lock = threading.Lock()
_hits: Dict[str, List[float]] = defaultdict(list)


def allow_new_session(client_key: str) -> bool:
    now = time.monotonic()
    cutoff = now - _WINDOW_SECONDS

    with _lock:
        timestamps = [t for t in _hits[client_key] if t > cutoff]

        if len(timestamps) >= _MAX_NEW_SESSIONS:
            _hits[client_key] = timestamps
            return False

        timestamps.append(now)
        _hits[client_key] = timestamps
        return True


def get_client_key(forwarded_for: str, remote_addr: str) -> str:
    # Cloud Run(신뢰하는 프록시 1개) 뒤에서는 체인의 "마지막" 값이 그 프록시가 실제로 본 접속자
    # IP다. 클라이언트가 보낸 X-Forwarded-For는 앞쪽에 임의 값을 덧붙일 수 있어(스푸핑), 첫 값을
    # 쓰면 IP당 제한을 값만 바꿔가며 우회당한다.
    if forwarded_for:
        parts = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if parts:
            return parts[-1]
    return remote_addr or "unknown"
