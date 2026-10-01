import os
from typing import List

import imagehash
from PIL import Image, ImageDraw

from app.config.logger import logger
from app.profile_extraction.paths import BASE_DIR, TMP_DIR

TEMPLATE_IMG_DIR = os.path.join(BASE_DIR, "images/template", "locked_resonance_chain.png")


CIRCLES = [
    # 돌파
    (189, 575, 15),
    (263, 575, 15),
    (343, 575, 15),
    (423, 575, 15),
    (503, 575, 15),
    (583, 575, 15),
]


def crop_circles(image: Image.Image) -> List[Image.Image]:

    crops = []

    for cx, cy, r in CIRCLES:
        x1, y1, x2, y2 = (cx - r, cy - r, cx + r, cy + r)

        crop = image.crop((x1, y1, x2, y2))

        mask = Image.new("L", (2 * r, 2 * r), 0)

        draw = ImageDraw.Draw(mask)

        draw.ellipse((0, 0, 2 * r, 2 * r), fill=255)

        circle_crop = Image.new("RGB", crop.size)

        circle_crop.paste(crop, mask=mask)

        crops.append(circle_crop)

    for i, crop in enumerate(crops, start=1):
        save_path = os.path.join(TMP_DIR, f"resonance_chain_{i}.png")
        crop.save(save_path)
        logger.debug(f"{save_path}가 저장되었습니다.")

    return crops


def _check_chain_level(chain_image: Image.Image, template: Image.Image) -> bool:
    threshold = 11

    chain = chain_image.convert("RGB")

    chain_hash = imagehash.average_hash(chain)
    template_hash = imagehash.average_hash(template)

    distance = chain_hash - template_hash

    logger.debug(f"hash distance: {distance}")

    # 템플릿은 미돌파 상태 이미지다.
    if distance <= threshold:
        return False

    return True


def calculate_chain_level(chain_images: List[Image.Image]) -> int:
    template = Image.open(TEMPLATE_IMG_DIR).convert("RGB")

    chain_level = 0

    for chain_image in chain_images:
        is_awakened = _check_chain_level(chain_image, template)

        if is_awakened:
            chain_level += 1

    return chain_level
