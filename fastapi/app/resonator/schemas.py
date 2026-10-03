from decimal import Decimal
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from app.resonator.echo_score.echo_grade import EchoGrade
from app.resonator.resonance_node.branch_position import BranchPosition
from app.resonator.resonance_node.node_position import NodePosition
from app.resonator.stat_type import StatType

PositiveId = Annotated[int, Field(gt=0)]


class Stat(BaseModel):
    type: StatType
    value: Decimal


class ResonanceNode(BaseModel):
    branchPosition: BranchPosition
    nodePosition: NodePosition
    active: bool
    stat: Optional[Stat] = None


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


# per_stat(점수 산출 내역)은 내부 계산용이라 응답에 포함하지 않는다.
class EchoDetail(BaseModel):
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    main: Stat
    secondary: Stat
    subs: List[Stat] = Field(default_factory=list)
    scorePercent: Optional[float] = None
    grade: Optional[EchoGrade] = None

    @classmethod
    def from_user_echo(cls, echo, image_url: Optional[str]) -> "EchoDetail":
        return cls(
            name=echo.name,
            imageUrl=image_url,
            main=Stat(type=echo.main_type, value=echo.main_value),
            secondary=Stat(type=echo.secondary_type, value=echo.secondary_value),
            subs=[Stat(type=sub.type, value=sub.value) for sub in echo.user_echo_subs],
            scorePercent=echo.score_percent,
            grade=echo.grade,
        )


class EchoListResponse(BaseModel):
    echoes: List[EchoDetail] = Field(default_factory=list)
    # 공명자 단위 에코 종합 분석(DB에 저장된 값). 없으면 None이라 응답에서 빠진다.
    echoAnalysis: Optional[str] = None


class DeleteResonatorRequest(BaseModel):
    userResonatorIds: List[PositiveId] = Field(min_length=1)


class UpdateResonatorRequest(BaseModel):
    weaponRefineLevel: int = Field(ge=1, le=5)
    nodes: List[ResonanceNode] = Field(min_length=1)


class ResonatorSummaryResponse(BaseModel):
    userResonatorId: Optional[int] = None  # LEFT JOIN이라 매칭되는 UserResonator가 없으면 None
    resonatorName: str
    rarity: int
    releaseVersion: int
    thumbnailImageUrl: str  # URL이 아니라 raw path (변환 전)


class ResonatorDetailResponse(BaseModel):
    userResonatorId: int
    resonatorName: str
    element: str
    standingImageUrl: str
    resonanceChainLevel: int
    weapon: WeaponDetail
    stat: ResonatorStat


class ResonatorSettingResponse(BaseModel):
    nodes: List[ResonanceNode]
    weapon: WeaponSetting


class CreateResonatorResponse(BaseModel):
    resonatorName: str
