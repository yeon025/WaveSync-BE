from typing import Optional
from app.models.resonance_node_master import ResonanceNodeMaster
from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition
from app.schemas.common import Stat


# Spring entity.ResonanceNodeMaster.getStat() 대응.
# DB I/O 없이 이미 로드된 ResonanceNodeMaster의 필드 중 하나를 골라 Stat으로
# 포장하는 순수 selector라서 모델 메서드가 아니라 mapper 함수로 분리했다.
def get_stat(
    node_master: ResonanceNodeMaster,
    branch_position: BranchPosition,
    node_position: NodePosition,
) -> Optional[Stat]:

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
