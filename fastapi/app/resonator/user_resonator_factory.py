from decimal import Decimal
from typing import List, Tuple

from app.profile_extraction.schemas import ExtractData
from app.resonator.master.resonator_master import ResonatorMaster
from app.resonator.master.weapon_master import WeaponMaster
from app.resonator.resonance_node.node_positions import BranchPosition, NodePosition
from app.resonator.resonance_node.resonance_node_mapper import get_stat
from app.resonator.resonance_node.user_resonance_node import UserResonanceNode
from app.resonator.schemas import ResonanceNode
from app.resonator.stat_type import StatType
from app.resonator.user_resonator.user_echo import UserEcho
from app.resonator.user_resonator.user_echo_sub import UserEchoSub
from app.resonator.user_resonator.user_resonator import UserResonator

# ExtractData + 마스터 데이터로 저장 전 UserResonator 애그리게잇을 조립한다 (DB 접근 없음).


def build_user_resonator(
    resonator_master: ResonatorMaster,
    weapon_master: WeaponMaster,
    extracted: ExtractData,
) -> Tuple[UserResonator, List[ResonanceNode]]:
    user_resonator = UserResonator(
        resonance_chain_level=extracted.resonanceChainLevel,
        refine_level=1,
        resonator_master=resonator_master,
        weapon_master=weapon_master,
    )

    # Column default는 flush 때 적용되는데 flush 전에 dto를 만들므로 is_active를 명시한다.
    nodes = []
    for branch_position in BranchPosition:
        for node_position in NodePosition:
            UserResonanceNode(
                branch_position=branch_position,
                node_position=node_position,
                is_active=True,
                user_resonator=user_resonator,
            )
            nodes.append(
                ResonanceNode(
                    branchPosition=branch_position,
                    nodePosition=node_position,
                    active=True,
                    stat=get_stat(resonator_master.resonance_node_master, branch_position, node_position),
                )
            )

    for echo_dto in extracted.echoes:
        echo = UserEcho(
            name=echo_dto.name,
            image=echo_dto.imagePath,
            main_type=StatType.from_code(echo_dto.main.type),
            main_value=Decimal(str(echo_dto.main.value)),
            secondary_type=StatType.from_code(echo_dto.secondary.type),
            secondary_value=int(echo_dto.secondary.value),
            user_resonator=user_resonator,
        )

        for sub_dto in echo_dto.subs:
            UserEchoSub(
                type=StatType.from_code(sub_dto.type),
                value=Decimal(str(sub_dto.value)),
                user_echo=echo,
            )

    return user_resonator, nodes
