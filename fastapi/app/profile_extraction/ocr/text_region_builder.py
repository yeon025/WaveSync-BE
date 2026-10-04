import os

from PIL import Image

from app.config.logger import logger
from app.profile_extraction.paths import TMP_DIR

CROP_GAP = 10

RECTANGLES = [
    # 공명자 이름
    (62, 16, 750, 82),
    # 무기 이름
    (1603, 449, 1850, 484),
    # 에코 슬롯 1~5, 슬롯마다 주옵 옵션/주옵 수치/보조옵/부옵 1~5 순서
    (220, 720, 380, 750),
    (315, 750, 380, 790),
    (63, 840, 380, 875),
    (63, 875, 380, 910),
    (63, 910, 380, 945),
    (63, 945, 380, 980),
    (63, 980, 380, 1015),
    (63, 1015, 380, 1050),
    (590, 720, 760, 750),
    (685, 750, 760, 790),
    (436, 840, 760, 875),
    (436, 875, 760, 910),
    (436, 910, 760, 945),
    (436, 945, 760, 980),
    (436, 980, 760, 1015),
    (436, 1015, 760, 1050),
    (970, 720, 1135, 750),
    (1060, 750, 1135, 790),
    (811, 840, 1135, 875),
    (811, 875, 1135, 910),
    (811, 910, 1135, 945),
    (811, 945, 1135, 980),
    (811, 980, 1135, 1015),
    (811, 1015, 1135, 1050),
    (1340, 720, 1505, 750),
    (1435, 750, 1505, 790),
    (1185, 840, 1505, 875),
    (1185, 875, 1505, 910),
    (1185, 910, 1505, 945),
    (1185, 945, 1505, 980),
    (1185, 980, 1505, 1015),
    (1185, 1015, 1505, 1050),
    (1720, 720, 1880, 750),
    (1815, 750, 1880, 790),
    (1562, 840, 1880, 875),
    (1562, 875, 1880, 910),
    (1562, 910, 1880, 945),
    (1562, 945, 1880, 980),
    (1562, 980, 1880, 1015),
    (1562, 1015, 1880, 1050),
]


def crop_and_stack(image: Image.Image) -> Image.Image:
    # Vision API를 1회만 호출하려고 세로로 이어붙인다. 순서는 ocr_service.split_profile_text_lines가 전제한다.
    crops = [image.crop(rect) for rect in RECTANGLES]

    max_width = max(crop.width for crop in crops)
    total_height = sum(crop.height + CROP_GAP for crop in crops)

    merged = Image.new("RGB", (max_width, total_height), (0, 0, 0))

    y = 0
    for crop in crops:
        merged.paste(crop, (0, y))
        y += crop.height + CROP_GAP

    save_path = os.path.join(TMP_DIR, "merged.png")
    merged.save(save_path)
    logger.debug(f"{save_path}가 저장되었습니다.")

    return merged
