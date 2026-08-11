from fastapi import APIRouter
from app.schemas.request import ResonatorImageRequest
from app.schemas.response import ResonatorImageResponse
from app.services.resonator_profile_service import extract_info
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