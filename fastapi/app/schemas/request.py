from typing import Annotated, List

from pydantic import BaseModel, Field

from app.schemas.common import ResonanceNode

# Spring dto.request.DeleteResonatorRequest 대응
# @NotEmpty List<@NotNull @Positive Long> userResonatorIds
PositiveId = Annotated[int, Field(gt=0)]


class DeleteResonatorRequest(BaseModel):
    userResonatorIds: List[PositiveId] = Field(min_length=1)


# Spring dto.request.UpdateResonatorRequest 대응
# @Min(1) @Max(5) @NotNull weaponRefineLevel / @Valid @NotEmpty nodes
class UpdateResonatorRequest(BaseModel):
    weaponRefineLevel: int = Field(ge=1, le=5)
    nodes: List[ResonanceNode] = Field(min_length=1)
