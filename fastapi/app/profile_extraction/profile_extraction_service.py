import os
from io import BytesIO

import requests
from PIL import Image

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.profile_extraction.echo.echo_matching_service import crop_echo_icons, match_echo_icon
from app.profile_extraction.echo.echo_text_parser import EchoMapper
from app.profile_extraction.ocr.ocr_service import clean_text, extract_text, process_ocr_result, split_profile_text_lines
from app.profile_extraction.ocr.text_region_builder import crop_and_stack
from app.profile_extraction.paths import TMP_DIR
from app.profile_extraction.resonance_chain_service import calculate_chain_level, crop_circles
from app.profile_extraction.schemas import ExtractData


def extract_info(image_path):

    echoMapper = EchoMapper()

    os.makedirs(TMP_DIR, exist_ok=True)

    response = requests.get(image_path, timeout=10)

    if response.status_code == 404:
        raise CustomException(ErrorCode.IMAGE_NOT_FOUND)

    if response.status_code == 403:
        raise CustomException(ErrorCode.IMAGE_ACCESS_DENIED)

    if response.status_code >= 400:
        raise CustomException(ErrorCode.IMAGE_LOAD_FAILED)

    profile = Image.open(BytesIO(response.content)).convert("RGB")

    chain_images = crop_circles(profile)
    merged_image = crop_and_stack(profile)
    echo_icons = crop_echo_icons(profile)

    # 슬롯별로 (에코 이름, 이미지 경로) 튜플, 모호하면 None
    echo_matches = [match_echo_icon(icon) for icon in echo_icons]
    logger.debug(f"에코 아이콘 판별 결과: {echo_matches}")

    chain_level = calculate_chain_level(chain_images)
    logger.debug(f"공명 체인 돌파 횟수는 {chain_level}입니다.")

    full_text = extract_text(merged_image)
    logger.debug("텍스트 추출을 완료했습니다.")

    # 추출된 텍스트를 y좌표 기준으로 병합
    merged_texts = process_ocr_result(full_text)
    logger.debug("텍스트 병합을 완료했습니다.")

    cleaned_texts = clean_text(merged_texts)
    logger.debug("텍스트 정제를 완료했습니다.")

    resonator_name, weapon_name, echo_lines = split_profile_text_lines(cleaned_texts)

    echo_list = echoMapper.run(echo_lines)

    for echo, match in zip(echo_list, echo_matches):
        if match is not None:
            echo.name, echo.imagePath = match

    return ExtractData(
        resonatorName=resonator_name,
        resonanceChainLevel=chain_level,
        weaponName=weapon_name,
        echoes=echo_list,
    )
