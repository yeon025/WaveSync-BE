from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.request import ResonatorImageRequest, DeleteResonatorRequestDto, UpdateResonatorRequestDto
from app.schemas.response import (
    ResonatorImageResponse,
    ResonatorSummaryResponseDto,
    ResonatorDetailResponseDto,
    ResonatorSettingResponseDto,
    CreateResonatorResponseDto,
)
from app.schemas.api_response import ApiResponse
from app.services.resonator_profile_service import extract_info
from app.services import resonator_service
from app.config.logger import logger


router = APIRouter(prefix="/resonators")


@router.post("/images", response_model=ResonatorImageResponse, status_code=200)
def analyze_resonator_image(request : ResonatorImageRequest):
    logger.debug(f"request.imageUrl: {request.imageUrl}")

    data = extract_info(request.imageUrl)

    return ResonatorImageResponse(
        code="OK",
        message="이미지 추출이 성공했습니다.",
        data=data
    )


# 아래 6개는 Spring ResonatorController 대응.


@router.post("", response_model=ApiResponse[CreateResonatorResponseDto], response_model_exclude_none=True, status_code=200)
def create_resonator(resonatorProfile: UploadFile = File(...), db: Session = Depends(get_db)):
    data = resonator_service.create_resonator(db, resonatorProfile)

    return ApiResponse(code="OK", message="공명자가 등록되었습니다.", data=data)


@router.get("", response_model=ApiResponse[List[ResonatorSummaryResponseDto]], response_model_exclude_none=True, status_code=200)
def get_resonator_summary(db: Session = Depends(get_db)):
    data = resonator_service.get_resonator_summary(db)

    return ApiResponse(code="OK", message="전체 공명자 목록을 조회했습니다.", data=data)


@router.get("/{user_resonator_id}", response_model=ApiResponse[ResonatorDetailResponseDto], response_model_exclude_none=True, status_code=200)
def get_resonator_detail(user_resonator_id: int, db: Session = Depends(get_db)):
    data = resonator_service.get_resonator_detail(db, user_resonator_id)

    return ApiResponse(code="OK", message="공명자를 조회했습니다.", data=data)


@router.get("/{user_resonator_id}/setting", response_model=ApiResponse[ResonatorSettingResponseDto], response_model_exclude_none=True, status_code=200)
def get_resonator_setting(user_resonator_id: int, db: Session = Depends(get_db)):
    data = resonator_service.get_resonator_setting(db, user_resonator_id)

    return ApiResponse(code="OK", message="설정 정보를 조회했습니다.", data=data)


@router.patch("/{user_resonator_id}/setting", response_model=ApiResponse, response_model_exclude_none=True, status_code=200)
def update_resonator(user_resonator_id: int, data: UpdateResonatorRequestDto, db: Session = Depends(get_db)):
    resonator_service.update_resonator(db, user_resonator_id, data)

    return ApiResponse(code="OK", message="공명자 정보가 수정되었습니다.")


@router.delete("", response_model=ApiResponse, response_model_exclude_none=True, status_code=200)
def delete_resonator(data: DeleteResonatorRequestDto, db: Session = Depends(get_db)):
    resonator_service.delete_resonator(db, data.userResonatorIds)

    return ApiResponse(code="OK", message="공명자 정보가 삭제되었습니다.")
