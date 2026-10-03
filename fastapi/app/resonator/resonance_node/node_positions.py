from enum import Enum


class BranchPosition(str, Enum):
    LEFT_OUTER = "left_outer"
    LEFT_INNER = "left_inner"
    CENTER = "center"
    RIGHT_OUTER = "right_outer"
    RIGHT_INNER = "right_inner"


class NodePosition(str, Enum):
    TOP = "top"
    MIDDLE = "middle"
