from typing import Annotated, List

from pydantic import BaseModel, Field

from app.schemas.common import ResonanceNode

PositiveId = Annotated[int, Field(gt=0)]


class DeleteResonatorRequest(BaseModel):
    userResonatorIds: List[PositiveId] = Field(min_length=1)


class UpdateResonatorRequest(BaseModel):
    weaponRefineLevel: int = Field(ge=1, le=5)
    nodes: List[ResonanceNode] = Field(min_length=1)
