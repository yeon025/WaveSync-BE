from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# Spring dto.response.ApiResponseDto<T> 대응.
#
# CLAUDE.md "API 응답 형식"에서 미정으로 남겨뒀던 성공 응답 공용 래퍼를 여기서 도입한다.
# ResonatorController의 6개 엔드포인트가 전부 이 모양(code/message/data)을 공유해서,
# 도메인별 개별 정의보다 Spring 구조에 더 1:1로 대응된다고 판단했다.
#
# Jackson @JsonInclude(NON_NULL)(data가 null이면 필드 자체를 생략)은 라우터에서
# response_model_exclude_none=True를 지정해 재현한다.
class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: Optional[T] = None
