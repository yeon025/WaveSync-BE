from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# 성공 응답 공용 래퍼 {code, message, data}. data가 None이면 라우터의
# response_model_exclude_none=True로 필드 자체를 생략한다.
class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: Optional[T] = None
