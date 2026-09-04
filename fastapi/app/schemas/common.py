from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition
from app.models.stat_type import StatType


# 스탯 (type + value). Pydantic이 StatType 문자열 <-> 멤버 변환을 네이티브 처리한다.
class Stat(BaseModel):
    type: StatType
    value: Decimal


# 공명 노드 (위치 + 활성 여부 + 스탯).
class ResonanceNode(BaseModel):
    branchPosition: BranchPosition
    nodePosition: NodePosition
    active: bool
    stat: Optional[Stat] = None


# 공명자 최종 스탯.
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


# 무기 상세.
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


# 무기 설정 (재련). refineType은 code 문자열로 담는다.
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
            refineType=weapon.refine_type.value if weapon.refine_type else None,
            refine1Value=weapon.refine_1_value,
            refine2Value=weapon.refine_2_value,
            refine3Value=weapon.refine_3_value,
            refine4Value=weapon.refine_4_value,
            refine5Value=weapon.refine_5_value,
            imageUrl=weapon_image_url,
        )


# OCR 추출 결과 스키마.
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
