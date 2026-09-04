from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import ResonanceNode, ResonatorStat, WeaponDetail, WeaponSetting


class ResonatorSummaryResponse(BaseModel):
    userResonatorId: Optional[int] = None  # LEFT JOIN이라 매칭되는 UserResonator가 없으면 None
    resonatorName: str
    rarity: int
    releaseVersion: int
    thumbnailImageUrl: str  # URL이 아니라 raw path (변환 전)


class ResonatorDetailResponse(BaseModel):
    userResonatorId: int
    resonatorName: str
    element: str  # code 문자열
    standingImageUrl: str
    resonanceChainLevel: int
    weapon: WeaponDetail
    stat: ResonatorStat


class ResonatorSettingResponse(BaseModel):
    nodes: List[ResonanceNode]
    weapon: WeaponSetting


class CreateResonatorResponse(BaseModel):
    resonatorName: str
