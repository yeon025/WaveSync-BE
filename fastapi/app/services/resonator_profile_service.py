import os
import requests
from PIL import Image
from io import BytesIO
from app.services.preprocess_service import crop_circles, crop_and_stack
from app.services.resonance_chain_service import calculate_chain_level
from app.services.ocr_service import extract_text, process_ocr_result, clean_text
from app.validators.resonator_validator import validate_resonator
from app.validators.weapon_validator import validate_weapon
from app.validators.echo_sub_validator import validate_sub
from app.mapper.echo import EchoMapper
from app.config.constant import TMP_DIR, CHAIN_IMG_DIRS, TEMPLATE_IMG_DIR
from app.schemas.response import ExtractData
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger
from sqlalchemy.orm import Session



def extract_info(image_path, db: Session):
    
    echoMapper = EchoMapper()

    os.makedirs(TMP_DIR, exist_ok=True)


    # ========================================
    # 이미지 가져오기
    # ========================================
    response = requests.get(image_path, timeout=10)

    if response.status_code == 404:
        raise CustomException(ErrorCode.IMAGE_NOT_FOUND)

    if response.status_code == 403:
        raise CustomException(ErrorCode.IMAGE_ACCESS_DENIED)

    if response.status_code >= 400:
        raise CustomException(ErrorCode.IMAGE_LOAD_FAILED)

    profile = Image.open(BytesIO(response.content)).convert("RGB")
    
    

    # ========================================
    # 전처리
    # ========================================
    
    # 돌파 상태 판별을 위한 전처리
    crop_circles(profile)

    # OCR용 텍스트 인식 정확도 향상을 위한 전처리
    crop_and_stack(profile)
    
    
    

    # ========================================
    # 공명 체인 레벨 계산
    # ========================================
    chain_level = calculate_chain_level(CHAIN_IMG_DIRS, TEMPLATE_IMG_DIR)
    logger.debug(f"공명 체인 돌파 횟수는 {chain_level}입니다.")




    # ========================================
    # OCR
    # ========================================
    
    # OCR로 텍스트 추출
    full_text = extract_text(os.path.join(TMP_DIR, "merged.png"))
    logger.debug("텍스트 추출을 완료했습니다.")
    
    # 추출된 텍스트를 y좌표 기준으로 병합
    merged_texts = process_ocr_result(full_text)
    logger.debug("텍스트 병합을 완료했습니다.")
    
    # 텍스트 정제 및 필터링
    cleaned_texts = clean_text(merged_texts)
    logger.debug("텍스트 정제를 완료했습니다.")




    # ========================================
    # 에코 스탯 매핑
    # ========================================
    echo_list = echoMapper.run(cleaned_texts)
    


    # ========================================
    # 유효성 검사
    # ========================================
    
    # 공명자 이름 유효성 검사
    validate_resonator(cleaned_texts[0], db)

    # 무기 이름 유효성 검사
    cleaned_texts[1] = validate_weapon(cleaned_texts[1], db)

    # 에코 유효성 검사
    validate_sub(echo_list)

    

    return ExtractData(
        resonatorName=cleaned_texts[0], 
        resonanceChainLevel=chain_level, 
        weaponName=cleaned_texts[1], 
        echoes=echo_list
    )