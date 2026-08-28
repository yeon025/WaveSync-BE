from typing import List

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.user_echo import UserEcho
from app.models.user_echo_sub import UserEchoSub


def save_all(db: Session, echo_subs: List[UserEchoSub]) -> None:
    # Spring JpaRepository.saveAll() 대응. 커밋은 호출부 책임
    db.add_all(echo_subs)


def soft_delete_by_user_resonator_ids(db: Session, ids: List[int]) -> None:
    # ues.userEcho.userResonator.id in :ids — Postgres UPDATE ... FROM으로 2단계 JOIN 재현
    stmt = (
        update(UserEchoSub)
        .where(
            UserEchoSub.user_echo_id == UserEcho.id,
            UserEcho.user_resonator_id.in_(ids),
            UserEchoSub.is_deleted.is_(False),
        )
        .values(is_deleted=True)
    )
    db.execute(stmt)
    # 커밋은 호출부(서비스 계층) 책임
