from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition
from app.models.stat_type import StatType


# Spring dto.common.Stat 대응.
# type은 Spring @JsonValue(StatType.getCode())와 동일하게 code 값으로 직렬화한다
# (DB/Python 내부값은 여전히 대문자 멤버 이름 — models/stat_type.py 참고).
#
# 입력측(예: updateResonator 요청 바디)도 이 클래스를 쓰므로, 클라이언트가 code
# 문자열(예: "attack_percent")을 그대로 돌려보내는 경우를 from_code()로 흡수한다.
# 서비스 코드에서 이미 StatType 인스턴스로 생성하는 기존 호출부(예: WeaponDetail)는
# 영향 없다 — isinstance 체크로 그대로 통과시킨다.
class Stat(BaseModel):
    type: StatType
    value: Decimal

    @field_validator("type", mode="before")
    @classmethod
    def _coerce_type(cls, v):
        if isinstance(v, str):
            try:
                return StatType.from_code(v)
            except KeyError:
                pass  # from_code 실패 시 그대로 두고 Pydantic 표준 422로 처리
        return v

    @field_serializer("type")
    def serialize_type(self, value: StatType) -> str:
        return value.code


# Spring dto.common.ResonanceNode 대응.
# branchPosition/nodePosition은 Spring 필드 타입 자체가 enum이라(String으로 미리
# 변환하지 않음) Jackson @JsonValue처럼 code로 직렬화한다.
# Stat과 동일한 이유로 입력측 from_code() 변환도 같이 둔다.
class ResonanceNode(BaseModel):
    branchPosition: BranchPosition
    nodePosition: NodePosition
    active: bool
    stat: Optional[Stat] = None

    @field_validator("branchPosition", mode="before")
    @classmethod
    def _coerce_branch_position(cls, v):
        if isinstance(v, str):
            try:
                return BranchPosition.from_code(v)
            except KeyError:
                pass
        return v

    @field_validator("nodePosition", mode="before")
    @classmethod
    def _coerce_node_position(cls, v):
        if isinstance(v, str):
            try:
                return NodePosition.from_code(v)
            except KeyError:
                pass
        return v

    @field_serializer("branchPosition")
    def serialize_branch_position(self, value: BranchPosition) -> str:
        return value.code

    @field_serializer("nodePosition")
    def serialize_node_position(self, value: NodePosition) -> str:
        return value.code


# Spring dto.common.ResonatorStat 대응.
class ResonatorStat(BaseModel):
    hp: int
    attack: int
    defense: int

    energyRegen: Decimal
    criticalRate: Decimal
    criticalDamage: Decimal

    resonanceSkillDamageBonus: Decimal
    basicAttackDamageBonus: Decimal
    heavyAttackDamageBonus: Decimal
    resonanceLiberationDamageBonus: Decimal

    glacioDamageBonus: Decimal
    fusionDamageBonus: Decimal
    conductoDamageBonus: Decimal
    aeroDamageBonus: Decimal
    spectraDamageBonus: Decimal
    havocDamageBonus: Decimal
    healingBonus: Decimal

    @classmethod
    def from_final_stat(cls, final_stat) -> "ResonatorStat":
        return cls(
            hp=final_stat.hp,
            attack=final_stat.attack,
            defense=final_stat.defense,
            energyRegen=final_stat.energy_regen,
            criticalRate=final_stat.critical_rate,
            criticalDamage=final_stat.critical_damage,
            resonanceSkillDamageBonus=final_stat.resonance_skill_damage_bonus,
            basicAttackDamageBonus=final_stat.basic_attack_damage_bonus,
            heavyAttackDamageBonus=final_stat.heavy_attack_damage_bonus,
            resonanceLiberationDamageBonus=final_stat.resonance_liberation_damage_bonus,
            glacioDamageBonus=final_stat.glacio_damage_bonus,
            fusionDamageBonus=final_stat.fusion_damage_bonus,
            conductoDamageBonus=final_stat.conducto_damage_bonus,
            aeroDamageBonus=final_stat.aero_damage_bonus,
            spectraDamageBonus=final_stat.spectra_damage_bonus,
            havocDamageBonus=final_stat.havoc_damage_bonus,
            healingBonus=final_stat.healing_bonus,
        )


# Spring dto.common.WeaponDetail 대응.
class WeaponDetail(BaseModel):
    name: str
    attackValue: int
    main: Stat
    refineLevel: int
    imageUrl: str

    @classmethod
    def from_user_resonator(cls, user_resonator, weapon_image_url: str) -> "WeaponDetail":
        weapon = user_resonator.weapon_master
        return cls(
            name=weapon.name,
            attackValue=weapon.attack_value,
            main=Stat(type=weapon.main_type, value=weapon.main_value),
            refineLevel=user_resonator.refine_level,
            imageUrl=weapon_image_url,
        )


# Spring dto.common.WeaponSetting 대응.
# refineType은 Spring도 DTO 필드 자체가 String이라(Optional.map(StatType::getCode))
# 여기서도 그대로 code 문자열로 담는다 — 별도 field_serializer 불필요.
class WeaponSetting(BaseModel):
    refineLevel: int
    refineType: Optional[str] = None
    refine1Value: Optional[Decimal] = None
    refine2Value: Optional[Decimal] = None
    refine3Value: Optional[Decimal] = None
    refine4Value: Optional[Decimal] = None
    refine5Value: Optional[Decimal] = None
    imageUrl: str

    @classmethod
    def from_user_resonator(cls, user_resonator, weapon_image_url: str) -> "WeaponSetting":
        weapon = user_resonator.weapon_master
        return cls(
            refineLevel=user_resonator.refine_level,
            refineType=weapon.refine_type.code if weapon.refine_type else None,
            refine1Value=weapon.refine_1_value,
            refine2Value=weapon.refine_2_value,
            refine3Value=weapon.refine_3_value,
            refine4Value=weapon.refine_4_value,
            refine5Value=weapon.refine_5_value,
            imageUrl=weapon_image_url,
        )


# Echo — OCR 추출 결과 스키마 (Request/Response 접미사가 없는 하위 DTO라 common으로 이동).
class ExtractedStat(BaseModel):
    type: str
    value: float


class Echo(BaseModel):
    # name: str
    # imageUrl: str
    main: ExtractedStat
    secondary: ExtractedStat
    subs: List[ExtractedStat] = Field(default_factory=list)


# 공명자 정보
class ExtractData(BaseModel):
    resonatorName: str
    resonanceChainLevel: int
    weaponName: str
    echoes: List[Echo]
