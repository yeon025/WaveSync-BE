from typing import Annotated, List
from pydantic import BaseModel, Field
from app.schemas.common import ResonanceNodeDto


class ResonatorImageRequest(BaseModel):
    imageUrl: str


# Spring dto.request.DeleteResonatorRequestDto 대응
# @NotEmpty List<@NotNull @Positive Long> userResonatorIds
PositiveId = Annotated[int, Field(gt=0)]


class DeleteResonatorRequestDto(BaseModel):
    userResonatorIds: List[PositiveId] = Field(min_length=1)


# Spring dto.request.UpdateResonatorRequestDto 대응
# @Min(1) @Max(5) @NotNull weaponRefineLevel / @Valid @NotEmpty nodes
class UpdateResonatorRequestDto(BaseModel):
    weaponRefineLevel: int = Field(ge=1, le=5)
    nodes: List[ResonanceNodeDto] = Field(min_length=1)
