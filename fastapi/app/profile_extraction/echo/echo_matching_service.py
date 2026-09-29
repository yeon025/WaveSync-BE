import base64
import binascii
import os
import pickle
import threading
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.profile_extraction.constants import (
    ECHO_FEATURES_TTL_SECONDS,
    ECHO_LOWE_RATIO,
    ECHO_MATCHER_MODE,
    ECHO_MIN_KEYPOINTS,
    ECHO_MIN_MARGIN_RATIO,
    ECHO_ORB_CACHE_PATH,
    ECHO_ORB_FAST_THRESHOLD,
    ECHO_ORB_NFEATURES,
    ECHO_ORB_NLEVELS,
    ECHO_ORB_PROC_SIZE,
    ECHO_ORB_SCALE_FACTOR,
)
from app.profile_extraction.preprocessing.preprocess_service import load_rgb
from app.storage.object_storage_factory import get_object_storage_service
from app.storage.object_storage_service import ObjectStorageService, StorageObject

OrbFeature = Tuple[List[cv2.KeyPoint], Optional[np.ndarray]]
EchoAsset = Tuple[OrbFeature, str]  # (ORB 특징, 스토리지 객체 키)

# ORB 디텍터 / 매처 (모듈 전역 — 매 호출마다 새로 만들 필요 없음)
_ORB = cv2.ORB_create(
    nfeatures=ECHO_ORB_NFEATURES,
    scaleFactor=ECHO_ORB_SCALE_FACTOR,
    nlevels=ECHO_ORB_NLEVELS,
    fastThreshold=ECHO_ORB_FAST_THRESHOLD,
)
_BF_RATIO = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
_BF_CROSS = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


def decode_echo_name(key: str) -> str:
    """echo-images 버킷의 객체 키(base64 urlsafe 인코딩된 파일명)를 사람이 읽는 에코 이름으로 변환한다.
    디코딩할 수 없는 키는 원본 stem을 그대로 반환한다."""

    stem = os.path.splitext(key)[0]
    padded = stem + "=" * (-len(stem) % 4)
    try:
        return base64.urlsafe_b64decode(padded).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return stem


def _to_gray_array(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.resize((ECHO_ORB_PROC_SIZE, ECHO_ORB_PROC_SIZE), Image.LANCZOS).convert("L"))
    return np.ascontiguousarray(arr, dtype=np.uint8)


def _compute_orb(image: Image.Image) -> OrbFeature:
    gray = _to_gray_array(image)
    keypoints, descriptors = _ORB.detectAndCompute(gray, None)
    return list(keypoints), descriptors


def _kps_to_tuples(keypoints: List[cv2.KeyPoint]) -> list:
    return [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]


def _tuples_to_kps(tuples: list) -> List[cv2.KeyPoint]:
    return [
        cv2.KeyPoint(x=t[0], y=t[1], size=t[2], angle=t[3], response=t[4], octave=int(t[5]), class_id=int(t[6]))
        for t in tuples
    ]


def _load_disk_cache() -> Dict[str, dict]:
    if not os.path.exists(ECHO_ORB_CACHE_PATH):
        return {}
    try:
        with open(ECHO_ORB_CACHE_PATH, "rb") as f:
            return pickle.load(f)
    except (pickle.PickleError, EOFError, OSError) as exc:
        logger.warning(f"에코 ORB 캐시 로드 실패, 새로 계산합니다: {exc}")
        return {}


def _save_disk_cache(cache: Dict[str, dict]) -> None:
    try:
        with open(ECHO_ORB_CACHE_PATH, "wb") as f:
            pickle.dump(cache, f)
    except OSError as exc:
        logger.warning(f"에코 ORB 캐시 저장 실패: {exc}")


def _build_echo_features(storage: ObjectStorageService, objects: List[StorageObject]) -> Dict[str, EchoAsset]:
    """이미 조회된 echo-images 객체 목록(objects)에 대해 ORB 특징을
    { 에코 이름: ((keypoints, descriptors), 객체 키) }로 계산한다.
    로컬 디스크 캐시 키는 `{원본 base64 키}:{etag}` — 스토리지에서 실제로 바뀐 이미지만 재계산한다.
    변경 여부 확인(목록 조회)은 호출자(_refresh_echo_features)가 이미 끝낸 상태로 넘어온다."""

    disk_cache = _load_disk_cache()
    new_disk_cache: Dict[str, dict] = {}
    assets: Dict[str, EchoAsset] = {}
    recomputed = 0
    skipped = 0

    for obj in objects:
        cache_key = f"{obj.key}:{obj.etag}"
        name = decode_echo_name(obj.key)

        cached = disk_cache.get(cache_key)
        if cached is not None:
            kps = _tuples_to_kps(cached["kps"])
            des = cached["des"]
        else:
            try:
                content = storage.download_object(storage.echo_bucket, obj.key)
                kps, des = _compute_orb(load_rgb(content))
            except (OSError, ValueError, cv2.error, CustomException) as exc:
                logger.warning(f"에코 이미지 ORB 계산 실패, 건너뜁니다: {obj.key} ({exc})")
                continue
            recomputed += 1

        if des is None or len(kps) < ECHO_MIN_KEYPOINTS:
            # 특징점을 거의 못 찾은 이미지는 매칭 대상에서 제외 (크래시 방지)
            skipped += 1
            new_disk_cache[cache_key] = {"kps": _kps_to_tuples(kps), "des": des}
            continue

        new_disk_cache[cache_key] = {"kps": _kps_to_tuples(kps), "des": des}
        assets[name] = ((kps, des), obj.key)

    if recomputed or set(new_disk_cache) != set(disk_cache):
        _save_disk_cache(new_disk_cache)

    logger.debug(
        f"echo-images {len(assets)}개 로드 "
        f"(신규 계산 {recomputed}, 캐시 재사용 {len(assets) - recomputed}, 특징점 부족 제외 {skipped})"
    )
    return assets


# echo-images 메모리 캐시 상태 (모듈 전역). Cloud Run 인스턴스마다 독립적으로 유지되며
# 인스턴스 간 공유되지 않는다 — 인스턴스별로 각자 TTL마다 변경 여부를 확인한다.
_echo_assets: Optional[Dict[str, EchoAsset]] = None
_echo_snapshot: Dict[str, str] = {}  # 마지막으로 반영한 { 객체 키: etag }
_echo_last_checked = 0.0
_echo_cache_lock = threading.Lock()


def _diff_echo_snapshot(old: Dict[str, str], new: Dict[str, str]) -> Tuple[int, int, int]:
    added = len(new.keys() - old.keys())
    removed = len(old.keys() - new.keys())
    modified = sum(1 for key in new.keys() & old.keys() if new[key] != old[key])
    return added, modified, removed


def _refresh_echo_features() -> Dict[str, EchoAsset]:
    """echo-images 변경 여부를 확인하고, 변경이 있을 때만 ORB 캐시를 재빌드한다.
    호출자(_get_echo_features)가 _echo_cache_lock을 잡은 상태에서만 호출해야 한다."""

    global _echo_assets, _echo_snapshot, _echo_last_checked

    storage = get_object_storage_service()

    try:
        objects = storage.list_objects(storage.echo_bucket)
    except CustomException as exc:
        if _echo_assets is not None:
            logger.warning(f"echo-images 변경 확인 실패, 기존 캐시 유지: {exc}")
            _echo_last_checked = time.monotonic()
            return _echo_assets
        # 최초 로딩인데 목록 조회 자체가 실패하면 반환할 캐시가 없으므로 그대로 전파한다
        # (기존 동작과 동일 — 첫 호출 실패 시 에러 응답).
        raise

    new_snapshot = {obj.key: obj.etag for obj in objects}

    if _echo_assets is not None and new_snapshot == _echo_snapshot:
        logger.debug("echo-images 변경 없음, 기존 캐시 사용")
        _echo_last_checked = time.monotonic()
        return _echo_assets

    if _echo_assets is not None:
        added, modified, removed = _diff_echo_snapshot(_echo_snapshot, new_snapshot)
        logger.info(f"echo-images 변경 감지: 추가 {added}개, 수정 {modified}개, 삭제 {removed}개")

    try:
        new_assets = _build_echo_features(storage, objects)
    except Exception as exc:  # noqa: BLE001 - 재빌드 실패로 기존 정상 캐시를 잃지 않기 위한 안전망
        if _echo_assets is not None:
            logger.warning(f"echo-images ORB 캐시 재빌드 실패, 기존 캐시 유지: {exc}")
            _echo_last_checked = time.monotonic()
            return _echo_assets
        raise

    _echo_assets = new_assets
    _echo_snapshot = new_snapshot
    _echo_last_checked = time.monotonic()
    logger.debug("echo-images ORB 캐시 재빌드 완료")
    return new_assets


def _get_echo_features() -> Dict[str, EchoAsset]:
    """echo-images 특징을 메모리에 캐시하고, TTL(ECHO_FEATURES_TTL_SECONDS)이 지나면
    변경 여부를 확인해 필요할 때만 재빌드한다.

    Cloud Run은 요청 처리 중에만 CPU를 할당하고(idle 시 스로틀), 트래픽에 따라
    여러 인스턴스로 스케일되며 언제든 종료될 수 있어 별도 백그라운드 polling 루프는
    신뢰할 수 없다. 대신 실제 요청이 들어올 때(=CPU가 할당된 시점) TTL을 확인하는
    방식을 쓴다. 동시에 여러 요청 스레드가 TTL 만료를 감지해도 재빌드는 한 번만
    일어나도록 lock으로 감싼다."""

    assets = _echo_assets
    if assets is not None and (time.monotonic() - _echo_last_checked) < ECHO_FEATURES_TTL_SECONDS:
        return assets

    with _echo_cache_lock:
        # 락을 기다리는 동안 다른 스레드가 이미 갱신을 마쳤을 수 있으므로 다시 확인한다.
        assets = _echo_assets
        if assets is not None and (time.monotonic() - _echo_last_checked) < ECHO_FEATURES_TTL_SECONDS:
            return assets
        return _refresh_echo_features()


def _good_matches(des_a: np.ndarray, des_b: np.ndarray) -> int:
    """ECHO_MATCHER_MODE에 따라 좋은 매칭 개수를 센다."""

    if ECHO_MATCHER_MODE == "crosscheck":
        return len(_BF_CROSS.match(des_a, des_b))

    good = 0
    for pair in _BF_RATIO.knnMatch(des_a, des_b, k=2):
        if len(pair) == 2 and pair[0].distance < ECHO_LOWE_RATIO * pair[1].distance:
            good += 1
    return good


def _orb_similarity(feat_a: OrbFeature, feat_b: OrbFeature) -> float:
    """두 ORB 특징 간 유사도(0.0~1.0) = 좋은 매칭 수 / min(특징점 수 a, 특징점 수 b)."""

    kps_a, des_a = feat_a
    kps_b, des_b = feat_b
    if des_a is None or des_b is None:
        return 0.0
    if len(kps_a) < ECHO_MIN_KEYPOINTS or len(kps_b) < ECHO_MIN_KEYPOINTS:
        return 0.0

    denom = min(len(kps_a), len(kps_b))
    return _good_matches(des_a, des_b) / denom if denom else 0.0


def match_echo_icon(icon_image: Image.Image) -> Optional[Tuple[str, str]]:
    """에코 슬롯 아이콘 크롭 이미지와 가장 유사한 echo-images 이미지의 (이름, 이미지 경로)를 반환한다.
    이미지 경로는 '버킷명/객체 키' 형태의 상대 경로다 (예: echo-images/mumangja.png).
    1등과 2등의 유사도 차이가 충분치 않으면(모호하면) None을 반환한다."""

    try:
        slot_feat = _compute_orb(icon_image)
    except cv2.error as exc:
        logger.warning(f"에코 아이콘 ORB 계산 실패: {exc}")
        return None

    if slot_feat[1] is None or len(slot_feat[0]) < ECHO_MIN_KEYPOINTS:
        logger.debug(f"에코 아이콘 특징점 부족 (검출 {len(slot_feat[0])}개) → 매칭 없음")
        return None

    echo_assets = _get_echo_features()
    ranked = sorted(
        ((_orb_similarity(slot_feat, feat), name, key) for name, (feat, key) in echo_assets.items()),
        reverse=True,
    )
    if not ranked:
        return None

    best_score, best_name, best_key = ranked[0]
    second_score, second_name, _ = ranked[1] if len(ranked) > 1 else (0.0, None, None)

    if (best_score - second_score) < best_score * ECHO_MIN_MARGIN_RATIO:
        logger.debug(f"에코 매칭 모호 (1등 {best_score:.3f} {best_name!r}, 2등 {second_score:.3f} {second_name!r})")
        return None

    logger.debug(f"에코 매칭: {best_name} (유사도 {best_score:.3f}, 2등 {second_score:.3f} {second_name!r})")

    storage = get_object_storage_service()
    image_path = f"{storage.echo_bucket}/{best_key}"
    return best_name, image_path
