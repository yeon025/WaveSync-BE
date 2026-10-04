import os
from typing import List

import imagehash
from PIL import Image, ImageDraw

from app.config.logger import logger
from app.profile_extraction.paths import BASE_DIR, TMP_DIR

TEMPLATE_IMG_PATH = os.path.join(BASE_DIR, "images/template", "locked_resonance_chain.png")

# 템플릿(미돌파 이미지)과의 해시 거리가 이 값 이하면 미돌파다.
HASH_DISTANCE_THRESHOLD = 11

CIRCLES = [
    (189, 575, 15),
    (263, 575, 15),
    (343, 575, 15),
    (423, 575, 15),
    (503, 575, 15),
    (583, 575, 15),
]


def crop_circles(image: Image.Image) -> List[Image.Image]:
    crops = []

    for i, (cx, cy, r) in enumerate(CIRCLES, start=1):
        crop = image.crop((cx - r, cy - r, cx + r, cy + r))

        mask = Image.new("L", (2 * r, 2 * r), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 2 * r, 2 * r), fill=255)

        circle_crop = Image.new("RGB", crop.size)
        circle_crop.paste(crop, mask=mask)
        crops.append(circle_crop)

        save_path = os.path.join(TMP_DIR, f"resonance_chain_{i}.png")
        circle_crop.save(save_path)
        logger.debug(f"{save_path}가 저장되었습니다.")

    return crops


def calculate_chain_level(chain_images: List[Image.Image]) -> int:
    template = Image.open(TEMPLATE_IMG_PATH).convert("RGB")
    template_hash = imagehash.average_hash(template)

    chain_level = 0

    for chain_image in chain_images:
        chain_hash = imagehash.average_hash(chain_image.convert("RGB"))
        distance = chain_hash - template_hash
        logger.debug(f"hash distance: {distance}")

        if distance > HASH_DISTANCE_THRESHOLD:
            chain_level += 1

    return chain_level
