from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition
from app.models.resonance_node_master import ResonanceNodeMaster
from app.schemas.common import Stat


# 이미 로드된 ResonanceNodeMaster에서 위치에 맞는 필드를 골라 Stat으로 포장하는 순수 selector.
def get_stat(
    node_master: ResonanceNodeMaster, branch_position: BranchPosition, node_position: NodePosition
) -> Stat | None:

    if branch_position in (BranchPosition.LEFT_OUTER, BranchPosition.RIGHT_OUTER):
        value = (
            node_master.outer_top_node_value
            if node_position == NodePosition.TOP
            else node_master.outer_middle_node_value
        )
        return Stat(type=node_master.outer_node_type, value=value)

    if branch_position in (BranchPosition.LEFT_INNER, BranchPosition.RIGHT_INNER):
        value = (
            node_master.inner_top_node_value
            if node_position == NodePosition.TOP
            else node_master.inner_middle_node_value
        )
        return Stat(type=node_master.inner_node_type, value=value)

    return None  # CENTER
