from sqlalchemy import JSON, BigInteger, Column, ForeignKey
from sqlalchemy import Enum as SAEnum

from app.db.base import Base, enum_values
from app.resonator.models.scaling_stat import ScalingStat


class ResonatorDamageMaster(Base):
    """공명자별 에코 점수 계산 설정 (읽기 전용).

    서포터처럼 점수 계산 대상이 아닌 공명자는 행이 없다.
    relevant_damage_types는 DamageType 값의 JSON 배열(1~2개)이며, 원소 검증은 echo_score_service가 한다.
    """

    __tablename__ = "resonator_damage_master"

    id = Column(BigInteger, primary_key=True)

    relevant_damage_types = Column(JSON, nullable=False)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    scaling_stat = Column(
        SAEnum(ScalingStat, native_enum=False, length=20, values_callable=enum_values), nullable=False
    )

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False, unique=True)

    # 역참조는 미사용이라 relationship을 두지 않는다 (repository가 resonator_master_id로 직접 조회).
