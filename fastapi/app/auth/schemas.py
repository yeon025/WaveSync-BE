from pydantic import BaseModel

from app.auth.authenticated_user import AuthenticatedUser


class SessionResponse(BaseModel):
    userId: int
    role: str
    isGuest: bool

    @classmethod
    def from_authenticated_user(cls, user: AuthenticatedUser, is_guest: bool) -> "SessionResponse":
        return cls(userId=user.id, role=user.role.value, isGuest=is_guest)
