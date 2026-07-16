from PIL import Image
import imagehash
from app.config.logger import logger


def _check_chain_level(chain_path, template_path):
    threshold = 11

    chain = Image.open(chain_path).convert("RGB")
    template = Image.open(template_path).convert("RGB")

    chain_hash = imagehash.average_hash(chain)
    template_hash = imagehash.average_hash(template)

    distance = chain_hash - template_hash

    logger.debug(f"hash distance: {distance}")

    # 템플릿과 유사하면 미돌파
    if distance <= threshold:
        return False

    # 유사하지 않으면 돌파
    return True


def calculate_chain_level(chain_img_paths, template_path):

    chain_level = 0

    for chain_path in chain_img_paths:

        is_awakened = _check_chain_level(chain_path, template_path)

        if is_awakened:
            chain_level += 1

    return chain_level