from typing import List

import imagehash
from PIL import Image

from app.config.logger import logger


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


def calculate_chain_level(chain_images: List[Image.Image], template_path: str) -> int:
    template = Image.open(template_path).convert("RGB")

    chain_level = 0

    for chain_image in chain_images:
        is_awakened = _check_chain_level(chain_image, template)

        if is_awakened:
            chain_level += 1

    return chain_level
