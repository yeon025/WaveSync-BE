from pydantic import BaseModel, Field
from typing import List



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