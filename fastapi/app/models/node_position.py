from enum import Enum


class NodePosition(str, Enum):
    """Spring entity.NodePosition 대응.

    DB 저장값은 Spring @Enumerated(EnumType.STRING)과 동일하게 enum 멤버 이름
    (예: TOP)이다.

    현재는 ResonanceNodeMaster의 get_stat() 파라미터 타입으로만 쓰인다 — 이 값
    자체를 저장하는 컬럼(user_resonance_nodes.node_position)은 UserResonanceNode
    도메인 이관 시 여기 매핑된다.
    """

    TOP = "TOP"
    MIDDLE = "MIDDLE"
