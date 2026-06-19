from pydantic import BaseModel, Field
from typing import List



# Echo
class Stat(BaseModel):
    type: str
    value: str

class Echo(BaseModel):
    # name: str
    # imageUrl: str
    main: Stat
    secondary: Stat
    sub: List[Stat] = Field(default_factory=list)



# 공명자 정보
class ExtractData(BaseModel):
    resonatorName: str
    resonanceChainLevel: int
    weaponName: str
    echo: List[Echo]


class ResonatorImageResponse(BaseModel):
    code: int
    message: str
    data: ExtractData