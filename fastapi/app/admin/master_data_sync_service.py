import hashlib
import re
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.admin import encore_client, namuwiki_client
from app.admin.schemas import SyncResult, SyncTarget
from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.profile_extraction.echo.echo_matching_service import encode_echo_object_name
from app.resonator.master import resonator_master_repository, weapon_master_repository
from app.resonator.master.resonator_master import Element, ResonatorMaster
from app.resonator.master.weapon_master import WeaponMaster
from app.resonator.resonance_node import resonance_node_master_repository
from app.resonator.resonance_node.resonance_node_master import ResonanceNodeMaster
from app.resonator.stat_type import StatType
from app.storage.object_storage_factory import get_object_storage_service

# 캐릭터 속성 한글명 → Element. echo_text_parser.py의 "OO 피해 보너스" 접두어와 동일한 표기를 쓴다.
_ELEMENT_NAME_MAP = {
    "응결": Element.GLACIO,
    "용융": Element.FUSION,
    "기류": Element.AERO,
    "전도": Element.CONDUCTO,
    "회절": Element.SPECTRA,
    "인멸": Element.HAVOC,
}

# 무기 두 번째 Property(공격력 바로 다음 항목)의 한글명 → StatType.
# 실제 Encore 응답(샘플 20종)에서 확인된 값만 포함한다 — 새 이름이 나오면 추측하지 않고 예외를 올린다.
_WEAPON_STAT_NAME_MAP = {
    "HP": StatType.HP_PERCENT,
    "공격력": StatType.ATTACK_PERCENT,
    "방어력": StatType.DEFENSE_PERCENT,
    "공명 효율": StatType.ENERGY_REGEN,
    "크리티컬": StatType.CRITICAL_RATE,
    "크리티컬 피해": StatType.CRITICAL_DAMAGE,
}

# 공명 노드(SkillTree) PropertyNodeTitle("OO 증가")의 "OO" 부분 → StatType.
# 기존 resonance_node_master 시드에서 실제로 쓰인 9개(outer) + 3개(inner) 값만 포함한다.
_NODE_STAT_NAME_MAP = {
    "HP": StatType.HP_PERCENT,
    "공격력": StatType.ATTACK_PERCENT,
    "방어력": StatType.DEFENSE_PERCENT,
    "치료 효과 보너스": StatType.HEALING_BONUS,
    "크리티컬": StatType.CRITICAL_RATE,
    "크리티컬 피해": StatType.CRITICAL_DAMAGE,
    "응결 피해 보너스": StatType.GLACIO_DAMAGE_BONUS,
    "용융 피해 보너스": StatType.FUSION_DAMAGE_BONUS,
    "전도 피해 보너스": StatType.CONDUCTO_DAMAGE_BONUS,
    "기류 피해 보너스": StatType.AERO_DAMAGE_BONUS,
    "회절 피해 보너스": StatType.SPECTRA_DAMAGE_BONUS,
    "인멸 피해 보너스": StatType.HAVOC_DAMAGE_BONUS,
}

# 긴 이름부터 접두어 매칭("크리티컬 피해"가 "크리티컬"보다 먼저 매칭되어야 한다).
_NODE_STAT_NAME_MAP_BY_LENGTH = sorted(_NODE_STAT_NAME_MAP.items(), key=lambda item: len(item[0]), reverse=True)
_PERCENT_PATTERN = re.compile(r"([\d.]+)%")

# resonance_node_master의 inner/outer 구분 규칙. SkillTree 응답에는 안쪽/바깥쪽을 나타내는 필드가 없어
# (Id, PropertyNodeTitle, PropertyNodeDescribe, PropertyNodeIcon, Consume 중 위치 필드 없음, Encore API
# 실제 응답으로 확인함), 기존 03_resonance_node_master.sql 시드 56건 전부와 Encore 실데이터(양양·설지)를
# 대조해 확인한 고정 규칙을 쓴다: inner_node_type은 항상 "기본 스탯 %" 3종류 중 하나이고, outer_node_type은
# 항상 나머지 9종류(크리티컬/치료 효과 보너스/원소 피해 보너스) 중 하나다 — 예외 없이 전부 일치했다.
_INNER_STAT_TYPES = frozenset({StatType.HP_PERCENT, StatType.ATTACK_PERCENT, StatType.DEFENSE_PERCENT})

# resonator_master/weapon_master에는 레벨별 성장치 중 90레벨(만렙) 기준 능력치만 저장한다.
_TARGET_LEVEL = 90

# 방랑자(각 원소별로 encore_id가 다른 성별 변형 2개가 존재)는 남자 쪽으로 고정한다.
# RoleBody는 캐릭터 공통 필드(모델 종류)지만, 방랑자 이름의 변형 쌍을 가를 때만 기준으로 쓴다 —
# 다른 캐릭터의 RoleBody(여성 모델 포함)에는 영향이 없다.
_ROVER_NAME_PREFIX = "방랑자"
_ROVER_MALE_ROLE_BODY = "MaleM"


def _select_target_level_row(level_rows: List[dict], label: str) -> dict:
    for row in level_rows:
        if row["level"] == _TARGET_LEVEL:
            return row
    logger.error(f"{label}: {_TARGET_LEVEL}레벨 능력치를 찾지 못했습니다.")
    raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)


def _find_property(properties: List[dict], name: str) -> dict:
    for prop in properties:
        if prop.get("Name") == name:
            return prop
    logger.error(f"Properties에서 '{name}' 항목을 찾지 못했습니다.")
    raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)


def _build_resonator_level_rows(detail: dict) -> List[dict]:
    properties = detail.get("Properties") or []
    hp_growth = {g["growthId"]: g for g in _find_property(properties, "HP").get("GrowthValues", [])}
    attack_growth = {g["growthId"]: g for g in _find_property(properties, "공격력").get("GrowthValues", [])}
    defense_growth = {g["growthId"]: g for g in _find_property(properties, "방어력").get("GrowthValues", [])}

    growth_ids = sorted(hp_growth.keys())
    if not growth_ids or growth_ids != sorted(attack_growth.keys()) or growth_ids != sorted(defense_growth.keys()):
        logger.error("HP/공격력/방어력의 growthId 구성이 서로 일치하지 않습니다.")
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    return [
        {
            "growth_id": growth_id,
            "level": hp_growth[growth_id]["level"],
            "hp": round(hp_growth[growth_id]["value"]),
            "attack": round(attack_growth[growth_id]["value"]),
            "defense": round(defense_growth[growth_id]["value"]),
        }
        for growth_id in growth_ids
    ]


def _parse_weapon_growth_value(raw: str) -> Decimal:
    text = str(raw).strip()
    if text.endswith("%"):
        text = text[:-1]
    return Decimal(text)


def _resolve_weapon_stat_type(name: str) -> StatType:
    stat_type = _WEAPON_STAT_NAME_MAP.get(name)
    if stat_type is None:
        logger.error(f"알 수 없는 무기 능력치 이름입니다: {name}")
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)
    return stat_type


def _build_weapon_level_rows(detail: dict) -> Tuple[List[dict], StatType]:
    properties = detail.get("Properties") or []
    if len(properties) < 2 or properties[0].get("Name") != "공격력":
        logger.error("무기 Properties 구성이 예상과 다릅니다 (공격력이 첫 항목이 아님).")
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    main_type = _resolve_weapon_stat_type(properties[1].get("Name"))

    attack_growth_values = properties[0].get("GrowthValues", [])
    main_growth_values = properties[1].get("GrowthValues", [])
    attack_by_level = {g["Level"]: _parse_weapon_growth_value(g["Value"]) for g in attack_growth_values}
    main_by_level = {g["Level"]: _parse_weapon_growth_value(g["Value"]) for g in main_growth_values}

    levels = sorted(attack_by_level.keys())
    if not levels or levels != sorted(main_by_level.keys()):
        logger.error("무기 공격력/보조 능력치의 level 구성이 서로 일치하지 않습니다.")
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    rows = [
        {
            "level": level,
            "attack_value": round(attack_by_level[level]),
            "main_value": main_by_level[level].quantize(Decimal("0.01")),
        }
        for level in levels
    ]
    return rows, main_type


def _apply_resonator_fields(
    existing: ResonatorMaster,
    name: str,
    element: Element,
    rarity: int,
    top_level_row: dict,
    head_icon_url: str,
) -> bool:
    changed = False
    for field, value in (
        ("name", name),
        ("element", element),
        ("rarity", rarity),
        ("hp", top_level_row["hp"]),
        ("attack", top_level_row["attack"]),
        ("defense", top_level_row["defense"]),
        ("thumbnail_image", head_icon_url),
    ):
        if getattr(existing, field) != value:
            setattr(existing, field, value)
            changed = True
    return changed


def sync_resonators(db: Session) -> SyncResult:
    # id는 Encore 캐릭터 ID 그대로다. 방랑자(이름이 같은 성별 변형 쌍)는 남자만 남기고 여자 쪽은
    # 건너뛰므로 결과적으로 원소당 행이 하나뿐이다. 그 외 캐릭터는 encore_id별로 그대로 upsert한다
    # (name이 중복되지 않으므로 병합이 필요 없다). standing_image(나무위키 전신 이미지)는 이 동기화가
    # 건드리지 않는다.
    role_list = encore_client.get_character_list()
    if not role_list:
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    encore_ids = [role["Id"] for role in role_list]
    by_id = {m.id: m for m in resonator_master_repository.find_all_by_ids(db, encore_ids)}

    result = SyncResult()

    for role in role_list:
        encore_id = role["Id"]
        name = role["Name"]
        quality_id = role.get("QualityId")
        element = _ELEMENT_NAME_MAP.get((role.get("Element") or {}).get("Name"))

        if quality_id not in (4, 5) or element is None:
            logger.warning(f"지원하지 않는 데이터라 건너뜁니다: {name} (QualityId={quality_id})")
            result.skipped += 1
            continue

        detail = encore_client.get_character_detail(encore_id)

        if name.startswith(_ROVER_NAME_PREFIX) and detail.get("RoleBody") != _ROVER_MALE_ROLE_BODY:
            logger.info(f"방랑자 성별을 남자로 고정하기 위해 건너뜁니다: {name} (Id={encore_id})")
            result.skipped += 1
            continue

        level_rows = _build_resonator_level_rows(detail)
        top_level_row = _select_target_level_row(level_rows, name)
        head_icon_url = role.get("RoleHeadIcon")

        existing = by_id.get(encore_id)

        if existing is None:
            existing = ResonatorMaster(
                id=encore_id,
                name=name,
                element=element,
                rarity=quality_id,
                hp=top_level_row["hp"],
                attack=top_level_row["attack"],
                defense=top_level_row["defense"],
                thumbnail_image=head_icon_url,
            )
            db.add(existing)
            result.created += 1
        else:
            changed = _apply_resonator_fields(existing, name, element, quality_id, top_level_row, head_icon_url)
            if changed:
                result.updated += 1
            else:
                result.unchanged += 1

    db.commit()
    return result


# 나무위키 요청 사이에 두는 간격(초). 대량 크롤링으로 나무위키 서버에 과도한 요청을 보내지 않기 위함.
_NAMUWIKI_REQUEST_INTERVAL_SECONDS = 0.5


def sync_standing_images(db: Session) -> SyncResult:
    # Encore API 동기화(sync_resonators)와 논리적으로 분리된 별도 대상이다 — 나무위키 접근 실패가
    # 캐릭터/무기 마스터 동기화 자체를 막지 않는다. 캐릭터 이름으로 나무위키 문서를 매칭하므로
    # resonator_master가 먼저 채워져 있어야 의미가 있다(동기화 순서는 호출부/관리자가 정한다).
    wiki_urls = namuwiki_client.crawl_character_urls()

    resonators = resonator_master_repository.find_all(db)
    result = SyncResult()

    for i, resonator in enumerate(resonators):
        wiki_url = wiki_urls.get(resonator.name)

        # 방랑자는 원소별로 이름이 다르지만(방랑자 · 인멸 등) 나무위키 문서는 공용(방랑자) 하나뿐이다.
        if wiki_url is None and resonator.name.startswith(_ROVER_NAME_PREFIX):
            wiki_url = wiki_urls.get(_ROVER_NAME_PREFIX)

        if wiki_url is None:
            logger.warning(f"나무위키 문서를 찾지 못해 건너뜁니다: {resonator.name}")
            result.skipped += 1
            continue

        if i > 0:
            time.sleep(_NAMUWIKI_REQUEST_INTERVAL_SECONDS)

        try:
            standing_url = namuwiki_client.find_standing_url(wiki_url, resonator.name)
        except CustomException as e:
            # 한 캐릭터의 크롤링 실패가 나머지 처리를 막지 않는다. 기존 standing_image는 그대로 둔다.
            logger.warning(f"{resonator.name} 전신 이미지 크롤링 실패, 기존 값을 유지합니다: {e.message}")
            result.skipped += 1
            continue

        if standing_url is None:
            # 유효한 이미지를 찾지 못한 경우 — 기존 값을 비우지 않는다(find_standing_url의 반환값 규약).
            result.skipped += 1
            continue

        if resonator.standing_image == standing_url:
            result.unchanged += 1
        elif resonator.standing_image is None:
            resonator.standing_image = standing_url
            result.created += 1
        else:
            resonator.standing_image = standing_url
            result.updated += 1

    db.commit()
    return result


def _apply_weapon_fields(
    existing: WeaponMaster,
    name: str,
    main_type: StatType,
    attack_value: int,
    main_value: Decimal,
    image: str,
) -> bool:
    changed = False
    for field, value in (
        ("name", name),
        ("main_type", main_type),
        ("attack_value", attack_value),
        ("main_value", main_value),
        ("image", image),
    ):
        if getattr(existing, field) != value:
            setattr(existing, field, value)
            changed = True
    return changed


def sync_weapons(db: Session) -> SyncResult:
    # id는 Encore 무기 ID 그대로다(무기 이름은 중복이 없어 캐릭터와 달리 병합 이슈가 없다).
    weapon_list = encore_client.get_weapon_list()
    if not weapon_list:
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    encore_ids = [weapon["Id"] for weapon in weapon_list]
    by_id = {m.id: m for m in weapon_master_repository.find_all_by_ids(db, encore_ids)}

    result = SyncResult()

    for weapon in weapon_list:
        encore_id = weapon["Id"]
        name = weapon["Name"]
        icon_url = weapon.get("Icon")

        detail = encore_client.get_weapon_detail(encore_id)
        level_rows, main_type = _build_weapon_level_rows(detail)
        top_level_row = _select_target_level_row(level_rows, name)
        main_value_1dp = top_level_row["main_value"].quantize(Decimal("0.1"))

        existing = by_id.get(encore_id)

        if existing is None:
            existing = WeaponMaster(
                id=encore_id,
                name=name,
                attack_value=top_level_row["attack_value"],
                main_type=main_type,
                main_value=main_value_1dp,
                image=icon_url,
            )
            db.add(existing)
            result.created += 1
        else:
            changed = _apply_weapon_fields(
                existing, name, main_type, top_level_row["attack_value"], main_value_1dp, icon_url
            )
            if changed:
                result.updated += 1
            else:
                result.unchanged += 1

    db.commit()
    return result


def sync_echoes(db: Session) -> SyncResult:
    # echo_master 테이블 없이, Encore 아이콘을 echo_bucket에 직접 올려 기존 ORB 매칭
    # (profile_extraction/echo/echo_matching_service.py)이 쓰는 이미지만 최신화한다.
    echo_list = encore_client.get_echo_list()
    if not echo_list:
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    storage = get_object_storage_service()
    # ETag는 MinIO/Supabase 모두 단일 PUT 기준으로 콘텐츠 MD5이므로, 재다운로드 없이 변경 여부를
    # 판별하는 데 쓸 수 있다 (두 스토리지 구현의 list_objects/download_object와 동일한 전제).
    existing_etags = {obj.key: obj.etag.strip('"') for obj in storage.list_objects(storage.echo_bucket)}

    result = SyncResult()

    for echo in echo_list:
        name = echo.get("Name")
        icon_url = echo.get("Icon")

        if not name or not icon_url:
            logger.warning(f"이름 또는 아이콘이 없어 건너뜁니다: Id={echo.get('Id')}")
            result.skipped += 1
            continue

        content, content_type = encore_client.download_icon(icon_url)
        object_name = encode_echo_object_name(name, icon_url)
        content_hash = hashlib.md5(content).hexdigest()
        existing_etag = existing_etags.get(object_name)

        if existing_etag == content_hash:
            result.unchanged += 1
            continue

        storage.upload_bytes(storage.echo_bucket, object_name, content, content_type)
        if existing_etag is None:
            result.created += 1
        else:
            result.updated += 1

    return result


def _group_skill_tree_values(skill_tree: List[dict]) -> Dict[StatType, List[Decimal]]:
    grouped: Dict[StatType, List[Decimal]] = {}

    for node in skill_tree:
        describe = (node.get("PropertyNodeDescribe") or "").strip()
        # PropertyNodeTitle은 "방어 증가"처럼 줄임말을 쓰기도 해 신뢰할 수 없다 — PropertyNodeDescribe가
        # "{전체 이름}이/가 X.XX% 증가한다" 형식을 항상 지키므로 여기서 긴 이름부터 접두어로 매칭한다.
        stat_type = next((v for k, v in _NODE_STAT_NAME_MAP_BY_LENGTH if describe.startswith(k)), None)
        match = _PERCENT_PATTERN.search(describe)

        if stat_type is None or match is None:
            logger.warning(f"알 수 없는 공명 노드라 건너뜁니다: {node.get('PropertyNodeTitle')!r} / {describe!r}")
            continue

        # resonance_node_master의 *_node_value 컬럼은 NUMERIC(5,1)이라 소수 1자리로 맞춰서 비교·저장한다.
        # 그대로 두면 Encore의 2자리 값(예: "2.28%")이 DB에는 2.3으로 저장된 뒤 다음 비교에서 다시
        # 다르다고 판정돼 매번 "updated"로 집계된다.
        grouped.setdefault(stat_type, []).append(Decimal(match.group(1)).quantize(Decimal("0.1")))

    return grouped


def _build_resonance_node_fields(skill_tree: List[dict]) -> Optional[dict]:
    grouped = _group_skill_tree_values(skill_tree)

    inner_groups = {t: v for t, v in grouped.items() if t in _INNER_STAT_TYPES}
    outer_groups = {t: v for t, v in grouped.items() if t not in _INNER_STAT_TYPES}

    # inner/outer 각각 정확히 1종류씩, 총 2종류만 나와야 한다 — 그 외의 조합은 _INNER_STAT_TYPES 규칙이
    # 깨진 경우이므로 임의로 배정하지 않고 호출자가 건너뛰도록 None을 반환한다.
    if len(grouped) != 2 or len(inner_groups) != 1 or len(outer_groups) != 1:
        return None

    [(inner_type, inner_values)] = inner_groups.items()
    [(outer_type, outer_values)] = outer_groups.items()

    # 각 타입은 top/middle 두 단계만 존재해야 한다. 같은 타입에서 상단(top)이 중단(middle)보다 항상 크다는
    # 것은 03_resonance_node_master.sql 시드 56건 전부와 Consume 재료 등급(상단은 더 높은 등급을 요구)으로
    # 교차 확인했다.
    if len(set(inner_values)) != 2 or len(set(outer_values)) != 2:
        return None

    inner_middle, inner_top = sorted(set(inner_values))
    outer_middle, outer_top = sorted(set(outer_values))

    return {
        "outer_node_type": outer_type,
        "outer_top_node_value": outer_top,
        "outer_middle_node_value": outer_middle,
        "inner_node_type": inner_type,
        "inner_top_node_value": inner_top,
        "inner_middle_node_value": inner_middle,
    }


def sync_resonance_nodes(db: Session) -> SyncResult:
    # resonator_master.id가 곧 encore_id이므로(find_all_with_encore_id 같은 별도 필터가 필요 없다)
    # 전체 행을 그대로 대상으로 삼는다.
    resonators = resonator_master_repository.find_all(db)
    existing_by_resonator_id = {
        node.resonator_master_id: node
        for node in resonance_node_master_repository.find_all_by_resonator_master_ids(db, [r.id for r in resonators])
    }

    result = SyncResult()

    for resonator in resonators:
        detail = encore_client.get_character_detail(resonator.id)
        skill_tree = detail.get("SkillTree") or []

        if not skill_tree:
            logger.warning(f"SkillTree가 비어 있어 건너뜁니다: {resonator.name}")
            result.skipped += 1
            continue

        fields = _build_resonance_node_fields(skill_tree)
        if fields is None:
            logger.warning(f"공명 노드 위치를 식별할 수 없어 건너뜁니다: {resonator.name}")
            result.skipped += 1
            continue

        existing = existing_by_resonator_id.get(resonator.id)

        if existing is None:
            db.add(ResonanceNodeMaster(resonator_master_id=resonator.id, **fields))
            result.created += 1
            continue

        changed = False
        for field, value in fields.items():
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                changed = True

        if changed:
            result.updated += 1
        else:
            result.unchanged += 1

    db.commit()
    return result


_SYNC_FUNCTIONS = {
    SyncTarget.RESONATORS: sync_resonators,
    SyncTarget.WEAPONS: sync_weapons,
    SyncTarget.ECHOES: sync_echoes,
    SyncTarget.RESONANCE_NODES: sync_resonance_nodes,
    SyncTarget.STANDING_IMAGES: sync_standing_images,
}


def sync(db: Session, targets: List[SyncTarget]) -> Dict[str, SyncResult]:
    # 대상별로 독립 커밋한다 — 한 대상이 실패해도 이미 커밋된 다른 대상은 영향받지 않는다.
    return {target.value: _SYNC_FUNCTIONS[target](db) for target in targets}
