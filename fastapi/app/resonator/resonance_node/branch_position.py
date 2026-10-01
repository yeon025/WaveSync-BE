from enum import Enum


class BranchPosition(str, Enum):
    LEFT_OUTER = "left_outer"
    LEFT_INNER = "left_inner"
    CENTER = "center"
    RIGHT_OUTER = "right_outer"
    RIGHT_INNER = "right_inner"

    @property
    def code(self) -> str:
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "BranchPosition":
        return cls(code)
