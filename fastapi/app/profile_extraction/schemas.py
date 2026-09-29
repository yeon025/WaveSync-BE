from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractedStat(BaseModel):
    type: str
    value: float


class Echo(BaseModel):
    name: Optional[str] = None
    imagePath: Optional[str] = None  # '버킷명/이미지명' 형태의 상대 경로 (예: echo-images/mumangja.png)
    main: ExtractedStat
    secondary: ExtractedStat
    subs: List[ExtractedStat] = Field(default_factory=list)


class ExtractData(BaseModel):
    resonatorName: str
    resonanceChainLevel: int
    weaponName: str
    echoes: List[Echo]
