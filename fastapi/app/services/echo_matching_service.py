import base64
import binascii
import os
import pickle
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.config.constant import (
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
from app.config.logger import logger
from app.services.object_storage_factory import get_object_storage_service
from app.services.preprocess_service import load_rgb

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


def _build_echo_features() -> Dict[str, EchoAsset]:
    """echo-images 버킷의 모든 이미지에 대해 ORB 특징을 { 에코 이름: ((keypoints, descriptors), 객체 키) }로 계산한다.
    로컬 디스크 캐시 키는 `{원본 base64 키}:{etag}` — 스토리지에서 실제로 바뀐 이미지만 재계산한다."""

    storage = get_object_storage_service()
    objects = storage.list_objects(storage.echo_bucket)

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
            except (OSError, ValueError, cv2.error) as exc:
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


@lru_cache
def _get_echo_features() -> Dict[str, EchoAsset]:
    """echo-images 특징을 프로세스 생애주기 동안 재사용한다 (object_storage_factory와 동일한 캐싱 패턴).
    스토리지에 에코 이미지가 추가/변경돼도 프로세스를 재시작하기 전까지는 반영되지 않는다."""

    return _build_echo_features()


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
