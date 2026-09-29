from enum import Enum


class NodePosition(str, Enum):
    TOP = "top"
    MIDDLE = "middle"

    @property
    def code(self) -> str:
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "NodePosition":
        return cls(code)
