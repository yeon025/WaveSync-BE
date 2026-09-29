import base64
import threading
import time

import cv2
import numpy as np
import pytest

import app.profile_extraction.echo.echo_matching_service as em
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.storage.object_storage_service import StorageObject


def _key(name: str) -> str:
    """decode_echo_name()으로 되돌릴 수 있는 base64 urlsafe 객체 키를 만든다."""
    return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=") + ".png"


class FakeStorage:
    """ObjectStorageService를 흉내내는 테스트용 더블. echo_bucket/list_objects/download_object만 있으면 된다."""

    def __init__(self):
        self.echo_bucket = "echo-images"
        self.objects: list[StorageObject] = []
        self.contents: dict[str, bytes] = {}
        self.list_calls = 0
        self.download_calls: list[str] = []
        self.raise_on_list: Exception | None = None
        self.slow = False

    def list_objects(self, bucket):
        self.list_calls += 1
        if self.slow:
            time.sleep(0.02)
        if self.raise_on_list is not None:
            raise self.raise_on_list
        return list(self.objects)

    def download_object(self, bucket, key):
        self.download_calls.append(key)
        return self.contents[key]


@pytest.fixture(autouse=True)
def reset_cache(monkeypatch, tmp_path):
    """모듈 전역 메모리 캐시를 매 테스트마다 초기화하고, 디스크 캐시를 임시 경로로 격리한다.
    ORB 계산(_compute_orb)과 이미지 디코딩(load_rgb)은 실제 이미지 없이 결정적으로 동작하도록 가짜로 대체한다."""

    em._echo_assets = None
    em._echo_snapshot = {}
    em._echo_last_checked = 0.0

    monkeypatch.setattr(em, "ECHO_ORB_CACHE_PATH", str(tmp_path / "echo_orb_cache.pkl"))
    monkeypatch.setattr(em, "load_rgb", lambda content: content)

    orb_calls = {"count": 0}

    def fake_compute_orb(_image):
        orb_calls["count"] += 1
        kps = [
            cv2.KeyPoint(x=0.0, y=0.0, size=1.0, angle=-1.0, response=0.0, octave=0, class_id=-1)
            for _ in range(em.ECHO_MIN_KEYPOINTS)
        ]
        des = np.zeros((em.ECHO_MIN_KEYPOINTS, 32), dtype=np.uint8)
        return kps, des

    monkeypatch.setattr(em, "_compute_orb", fake_compute_orb)

    yield orb_calls


def _use_storage(monkeypatch, storage: FakeStorage):
    monkeypatch.setattr(em, "get_object_storage_service", lambda: storage)


def _expire_ttl():
    """다음 _get_echo_features() 호출이 TTL 이내 fast-path를 타지 않고
    실제로 echo-images 변경 여부를 확인하도록 강제한다."""
    em._echo_last_checked = 0.0


# 테스트 1. 최초 로딩: A/B 존재 → 둘 다 ORB 계산 → 메모리 캐시 생성
def test_initial_load_builds_all_assets(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key, b_key = _key("A"), _key("B")
    storage.objects = [StorageObject(key=a_key, etag="etag1"), StorageObject(key=b_key, etag="etag2")]
    storage.contents = {a_key: b"content-a", b_key: b"content-b"}
    _use_storage(monkeypatch, storage)

    assets = em._get_echo_features()

    assert set(assets.keys()) == {"A", "B"}
    assert reset_cache["count"] == 2
    assert storage.list_calls == 1


# 테스트 2. 변경 없음: 다시 확인해도 변경이 없으면 ORB를 재계산하지 않는다
def test_no_change_skips_recompute(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key, b_key = _key("A"), _key("B")
    storage.objects = [StorageObject(key=a_key, etag="etag1"), StorageObject(key=b_key, etag="etag2")]
    storage.contents = {a_key: b"content-a", b_key: b"content-b"}
    _use_storage(monkeypatch, storage)

    em._get_echo_features()
    assert reset_cache["count"] == 2

    _expire_ttl()
    assets = em._get_echo_features()

    assert reset_cache["count"] == 2  # 재계산 없음
    assert storage.list_calls == 2  # 변경 여부 확인을 위한 목록 조회는 일어남
    assert set(assets.keys()) == {"A", "B"}


# 테스트 3. 새 이미지 추가: C만 ORB 계산되고 메모리 캐시에 추가된다
def test_new_image_only_computes_new_one(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key, b_key, c_key = _key("A"), _key("B"), _key("C")
    storage.objects = [StorageObject(key=a_key, etag="etag1"), StorageObject(key=b_key, etag="etag2")]
    storage.contents = {a_key: b"content-a", b_key: b"content-b", c_key: b"content-c"}
    _use_storage(monkeypatch, storage)

    em._get_echo_features()
    assert reset_cache["count"] == 2
    storage.download_calls.clear()

    storage.objects.append(StorageObject(key=c_key, etag="etag3"))
    _expire_ttl()
    assets = em._get_echo_features()

    assert reset_cache["count"] == 3  # C만 추가로 계산됨
    assert set(assets.keys()) == {"A", "B", "C"}
    assert c_key in storage.download_calls
    assert a_key not in storage.download_calls  # A는 디스크 캐시 재사용, 재다운로드 없음


# 테스트 4. 이미지 수정: A만 재계산되고 B는 기존 디스크 캐시를 재사용한다
def test_modified_image_recomputes_only_that_one(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key, b_key = _key("A"), _key("B")
    storage.objects = [StorageObject(key=a_key, etag="etag1"), StorageObject(key=b_key, etag="etag2")]
    storage.contents = {a_key: b"content-a", b_key: b"content-b"}
    _use_storage(monkeypatch, storage)

    em._get_echo_features()
    assert reset_cache["count"] == 2
    storage.download_calls.clear()

    storage.objects = [StorageObject(key=a_key, etag="etag999"), StorageObject(key=b_key, etag="etag2")]
    storage.contents[a_key] = b"content-a-v2"
    _expire_ttl()
    assets = em._get_echo_features()

    assert reset_cache["count"] == 3  # A만 재계산
    assert storage.download_calls == [a_key]  # B는 재다운로드하지 않음
    assert set(assets.keys()) == {"A", "B"}


# 테스트 5. 이미지 삭제: B가 목록에서 사라지면 메모리 캐시에서도 제거된다
def test_deleted_image_removed_from_cache(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key, b_key = _key("A"), _key("B")
    storage.objects = [StorageObject(key=a_key, etag="etag1"), StorageObject(key=b_key, etag="etag2")]
    storage.contents = {a_key: b"content-a", b_key: b"content-b"}
    _use_storage(monkeypatch, storage)

    em._get_echo_features()

    storage.objects = [StorageObject(key=a_key, etag="etag1")]
    _expire_ttl()
    assets = em._get_echo_features()

    assert set(assets.keys()) == {"A"}
    assert reset_cache["count"] == 2  # 삭제만 있었으므로 추가 계산 없음


# 테스트 6. Supabase 조회 실패: 기존 정상 캐시를 그대로 유지한다
def test_list_failure_keeps_existing_cache(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key = _key("A")
    storage.objects = [StorageObject(key=a_key, etag="etag1")]
    storage.contents = {a_key: b"content-a"}
    _use_storage(monkeypatch, storage)

    first = em._get_echo_features()
    assert set(first.keys()) == {"A"}

    storage.raise_on_list = CustomException(ErrorCode.IMAGE_PROCESSING_FAILED)
    _expire_ttl()
    second = em._get_echo_features()

    assert second == first
    assert reset_cache["count"] == 1  # 재계산 없음


# 테스트 7. 동시 요청: TTL이 만료된 상태에서 여러 스레드가 동시에 호출해도 재빌드는 한 번만 일어난다
def test_concurrent_requests_rebuild_once(monkeypatch, reset_cache):
    storage = FakeStorage()
    a_key = _key("A")
    storage.objects = [StorageObject(key=a_key, etag="etag1")]
    storage.contents = {a_key: b"content-a"}
    _use_storage(monkeypatch, storage)

    em._get_echo_features()
    assert storage.list_calls == 1

    storage.slow = True  # list_objects를 살짝 느리게 만들어 여러 스레드가 겹치게 유도
    _expire_ttl()

    results = []
    errors = []

    def worker():
        try:
            results.append(em._get_echo_features())
        except Exception as exc:  # pragma: no cover - 실패 시 즉시 드러나도록
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    assert not errors
    assert len(results) == 5
    assert storage.list_calls == 2  # 최초 1회 + 만료 후 재빌드 1회 (동시 요청이어도 중복 실행 없음)
    assert all(set(r.keys()) == {"A"} for r in results)
