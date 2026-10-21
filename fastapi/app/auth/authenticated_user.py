from dataclasses import dataclass

from app.auth.user_role import UserRole


# ORM User를 라우터/서비스까지 들고 다니면 commit 이후 expire된 속성을 다시 읽어야 하는 문제가 생긴다.
# session_service가 commit 전에 값을 확보해 이 불변 값 객체로 넘겨준다.
@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    role: UserRole
