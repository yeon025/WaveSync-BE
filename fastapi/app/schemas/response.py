from pydantic import BaseModel, Field
from typing import List, Optional



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