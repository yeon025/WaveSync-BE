from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.common import ResonanceNodeDto, ResonatorStatDto, WeaponDetailDto, WeaponSettingDto



# Echo
class Stat(BaseModel):
    type: str
    value: float


class Echo(BaseModel):
    # name: str
    # imageUrl: str
    main: Stat
    secondary: Stat
    subs: List[Stat] = Field(default_factory=list)



# 공명자 정보
class ExtractData(BaseModel):
    resonatorName: str
    resonanceChainLevel: int
    weaponName: str
    echoes: List[Echo]


class ResonatorImageResponse(BaseModel):
    code: str
    message: str
    data: ExtractData



# Spring dto.response.ResonatorSummaryResponseDto 대응
class ResonatorSummaryResponseDto(BaseModel):
    userResonatorId: Optional[int] = None  # LEFT JOIN이라 매칭되는 UserResonator가 없으면 None
    resonatorName: str
    rarity: int
    releaseVersion: int
    thumbnailImageUrl: str  # 주의: Spring 원본도 실제 URL이 아니라 raw path를 그대로 담음(변환 전)



# Spring dto.response.ResonatorDetailResponseDto 대응
class ResonatorDetailResponseDto(BaseModel):
    userResonatorId: int
    resonatorName: str
    element: str  # Spring도 DTO 필드가 String이라(Element::getCode) code 문자열을 그대로 담음
    standingImageUrl: str
    resonanceChainLevel: int
    weapon: WeaponDetailDto
    stat: ResonatorStatDto


# Spring dto.response.ResonatorSettingResponseDto 대응
class ResonatorSettingResponseDto(BaseModel):
    nodes: List[ResonanceNodeDto]
    weapon: WeaponSettingDto


# Spring dto.response.CreateResonatorResponseDto 대응
class CreateResonatorResponseDto(BaseModel):
    resonatorName: str