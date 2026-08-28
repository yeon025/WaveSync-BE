from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import ResonanceNode, ResonatorStat, WeaponDetail, WeaponSetting


# Spring dto.response.ResonatorSummaryResponse 대응
class ResonatorSummaryResponse(BaseModel):
    userResonatorId: Optional[int] = None  # LEFT JOIN이라 매칭되는 UserResonator가 없으면 None
    resonatorName: str
    rarity: int
    releaseVersion: int
    thumbnailImageUrl: str  # 주의: Spring 원본도 실제 URL이 아니라 raw path를 그대로 담음(변환 전)


# Spring dto.response.ResonatorDetailResponse 대응
class ResonatorDetailResponse(BaseModel):
    userResonatorId: int
    resonatorName: str
    element: str  # Spring도 DTO 필드가 String이라(Element::getCode) code 문자열을 그대로 담음
    standingImageUrl: str
    resonanceChainLevel: int
    weapon: WeaponDetail
    stat: ResonatorStat


# Spring dto.response.ResonatorSettingResponse 대응
class ResonatorSettingResponse(BaseModel):
    nodes: List[ResonanceNode]
    weapon: WeaponSetting


# Spring dto.response.CreateResonatorResponse 대응
class CreateResonatorResponse(BaseModel):
    resonatorName: str
