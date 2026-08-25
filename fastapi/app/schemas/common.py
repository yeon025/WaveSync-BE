from decimal import Decimal
from pydantic import BaseModel, field_serializer
from app.models.stat_type import StatType


# Spring dto.common.StatDto 대응.
# type은 Spring @JsonValue(StatType.getCode())와 동일하게 code 값으로 직렬화한다
# (DB/Python 내부값은 여전히 대문자 멤버 이름 — models/stat_type.py 참고).
class StatDto(BaseModel):
    type: StatType
    value: Decimal

    @field_serializer("type")
    def serialize_type(self, value: StatType) -> str:
        return value.value.lower()
