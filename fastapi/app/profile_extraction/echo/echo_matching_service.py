import base64
import binascii
import os
import pickle
import threading
import time
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.profile_extraction.paths import TMP_DIR
from app.storage.object_storage_factory import get_object_storage_service
from app.storage.object_storage_service import ObjectStorageService, StorageObject

ECHO_ORB_CACHE_PATH = os.path.join(TMP_DIR, "echo_orb_cache.pkl")

ECHO_ICON_RECTANGLES = [
    (20, 648, 214, 831),
    (398, 648, 587, 831),
    (768, 648, 963, 831),
    (1142, 648, 1335, 831),
    (1518, 648, 1708, 831),
]

# 이미지 투명 배경을 합성할 배경색 (게임 내 슬롯이 어두우므로 검은색)
IMAGE_BG_COLOR = (0, 0, 0)

ECHO_FEATURES_TTL_SECONDS = 300

ECHO_ORB_PROC_SIZE = 256  # 비교 전 통일할 이미지 크기 (정사각형, px)
ECHO_ORB_NFEATURES = 800
ECHO_ORB_SCALE_FACTOR = 1.2
ECHO_ORB_NLEVELS = 8
ECHO_ORB_FAST_THRESHOLD = 20

# 매칭 방식: "ratio" (knnMatch + Lowe ratio test) | "crosscheck" (BFMatcher crossCheck=True)
ECHO_MATCHER_MODE = "ratio"
ECHO_LOWE_RATIO = 0.75
ECHO_MIN_KEYPOINTS = 8
ECHO_MIN_MARGIN_RATIO = 0.12  # 1등이 2등보다 (1등점수 * 이 비율) 이상 높아야 채택, 아니면 모호 → None

OrbFeature = Tuple[List[cv2.KeyPoint], Optional[np.ndarray]]
EchoAsset = Tuple[OrbFeature, str]  # (ORB 특징, 스토리지 객체 키)

_ORB = cv2.ORB_create(
    nfeatures=ECHO_ORB_NFEATURES,
    scaleFactor=ECHO_ORB_SCALE_FACTOR,
    nlevels=ECHO_ORB_NLEVELS,
    fastThreshold=ECHO_ORB_FAST_THRESHOLD,
)
_BF_RATIO = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
_BF_CROSS = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


def decode_echo_name(key: str) -> str:
    """객체 키는 base64 urlsafe로 인코딩된 에코 이름이다. 디코딩할 수 없으면 stem을 그대로 반환한다."""

    stem = os.path.splitext(key)[0]
    padded = stem + "=" * (-len(stem) % 4)
    try:
        return base64.urlsafe_b64decode(padded).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return stem


def load_rgb(image_source: Union[str, bytes, os.PathLike]) -> Image.Image:
    """투명 배경은 IMAGE_BG_COLOR로 합성해 RGB로 정규화한다."""

    source = BytesIO(image_source) if isinstance(image_source, (bytes, bytearray)) else image_source
    im = Image.open(source)

    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, IMAGE_BG_COLOR + (255,))
        im = Image.alpha_composite(bg, im)

    return im.convert("RGB")


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
    """디스크 캐시 키가 `{객체 키}:{etag}`라 스토리지에서 실제로 바뀐 이미지만 다시 계산한다."""

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


# 메모리 캐시는 Cloud Run 인스턴스 간에 공유되지 않아 인스턴스마다 각자 TTL로 갱신한다.
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
    """_echo_cache_lock을 잡은 상태에서만 호출해야 한다."""

    global _echo_assets, _echo_snapshot, _echo_last_checked

    storage = get_object_storage_service()

    try:
        objects = storage.list_objects(storage.echo_bucket)
    except CustomException as exc:
        if _echo_assets is not None:
            logger.warning(f"echo-images 변경 확인 실패, 기존 캐시 유지: {exc}")
            _echo_last_checked = time.monotonic()
            return _echo_assets
        # 최초 로딩이면 돌려줄 캐시가 없으므로 그대로 전파한다.
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
    """Cloud Run은 idle 시 CPU를 스로틀하므로 백그라운드 polling 대신 요청 시점에 TTL을 확인한다."""

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
    if ECHO_MATCHER_MODE == "crosscheck":
        return len(_BF_CROSS.match(des_a, des_b))

    good = 0
    for pair in _BF_RATIO.knnMatch(des_a, des_b, k=2):
        if len(pair) == 2 and pair[0].distance < ECHO_LOWE_RATIO * pair[1].distance:
            good += 1
    return good


def _orb_similarity(feat_a: OrbFeature, feat_b: OrbFeature) -> float:
    kps_a, des_a = feat_a
    kps_b, des_b = feat_b
    if des_a is None or des_b is None:
        return 0.0
    if len(kps_a) < ECHO_MIN_KEYPOINTS or len(kps_b) < ECHO_MIN_KEYPOINTS:
        return 0.0

    denom = min(len(kps_a), len(kps_b))
    return _good_matches(des_a, des_b) / denom if denom else 0.0


def crop_echo_icons(image: Image.Image) -> List[Image.Image]:

    crops = [image.crop(rect) for rect in ECHO_ICON_RECTANGLES]

    for i, crop in enumerate(crops, start=1):
        save_path = os.path.join(TMP_DIR, f"echo_{i}.png")
        crop.save(save_path)
        logger.debug(f"{save_path}가 저장되었습니다.")

    return crops


def match_echo_icon(icon_image: Image.Image) -> Optional[Tuple[str, str]]:
    """(에코 이름, '버킷명/객체 키' 경로)를 반환한다. 1·2등 유사도 차이가 작아 모호하면 None이다."""

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
