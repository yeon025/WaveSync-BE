from validators.image_validator import validate_image
from services.preprocess_service import crop_circles, crop_and_stack
from services.resonance_chain_service import calculate_chain_level
from services.ocr_service import extract_text, process_ocr_result, clean_text
from mapper.echo import EchoMapper
from config.constant import TMP_DIR, CHAIN_IMG_DIRS, TEMPLATE_IMG_DIR
from schemas.response import ExtractData
import os




def extract_info(image_path):
    
    echoMapper = EchoMapper()

    os.makedirs(TMP_DIR, exist_ok=True)
    
    # 이미지 유효성 검사
    validate_image(image_path)
    
    
    
    # ========================================
    # 전처리
    # ========================================
    
    # 돌파 상태 판별을 위한 전처리
    crop_circles(image_path)

    # OCR용 텍스트 인식 정확도 향상을 위한 전처리
    crop_and_stack(image_path)
    
    
    

    # ========================================
    # 공명 체인 레벨 계산
    # ========================================
    chain_level = calculate_chain_level(CHAIN_IMG_DIRS, TEMPLATE_IMG_DIR)




    # ========================================
    # OCR
    # ========================================
    
    # OCR로 텍스트 추출
    full_text = extract_text(os.path.join(TMP_DIR, "merged.png"))
    
    # 추출된 텍스트를 y좌표 기준으로 병합
    merged_texts = process_ocr_result(full_text)
    
    # 텍스트 정제 및 필터링
    cleaned_texts = clean_text(merged_texts)



    # ========================================
    # 에코 스탯 매핑
    # ========================================
    echo_list = echoMapper.run(cleaned_texts)
    
    
    

    return ExtractData(
        resonatorName=merged_texts[0], 
        resonanceChainLevel=chain_level, 
        weaponName=merged_texts[1], 
        echo=echo_list
    )