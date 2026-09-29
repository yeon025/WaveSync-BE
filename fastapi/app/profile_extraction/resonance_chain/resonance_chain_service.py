import imagehash
from PIL import Image

from app.config.logger import logger


def _check_chain_level(chain_path, template_path):
    threshold = 11

    chain = Image.open(chain_path).convert("RGB")
    template = Image.open(template_path).convert("RGB")

    chain_hash = imagehash.average_hash(chain)
    template_hash = imagehash.average_hash(template)

    distance = chain_hash - template_hash

    logger.debug(f"hash distance: {distance}")

    # 템플릿은 미돌파 상태 이미지다.
    if distance <= threshold:
        return False

    return True


def calculate_chain_level(chain_img_paths, template_path):

    chain_level = 0

    for chain_path in chain_img_paths:
        is_awakened = _check_chain_level(chain_path, template_path)

        if is_awakened:
            chain_level += 1

    return chain_level
