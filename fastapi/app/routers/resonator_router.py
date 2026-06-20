from fastapi import APIRouter
from app.schemas.request import ResonatorImageRequest
from app.schemas.response import ResonatorImageResponse
from app.services.resonator_profile_service import extract_info
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.deps import get_db


router = APIRouter(prefix="/resonators")


@router.post("/images", response_model=ResonatorImageResponse, status_code=200)
def analyze_resonator_image(request : ResonatorImageRequest, db: Session = Depends(get_db)):
    
    data = extract_info(request.imageUrl, db)

    return ResonatorImageResponse(
        code=200,
        message="OCR 처리가 성공했습니다.",
        data=data
    )