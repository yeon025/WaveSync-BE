import os
from io import BytesIO
from typing import List, Union

from PIL import Image, ImageDraw

from app.config.constant import CIRCLES, ECHO_ICON_RECTANGLES, IMAGE_BG_COLOR, RECTANGLES, TMP_DIR
from app.config.logger import logger

os.makedirs(TMP_DIR, exist_ok=True)


def crop_circles(image):

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


def crop_and_stack(image):

    crops = [image.crop((x1, y1, x2, y2)) for (x1, y1, x2, y2) in RECTANGLES]

    if not crops:
        return None

    max_width = max(crop.width for crop in crops)

    aligned = []

    for crop in crops:
        padded = Image.new("RGB", (max_width, crop.height + 10), (0, 0, 0))

        padded.paste(crop, (0, 0))

        aligned.append(padded)

    total_height = sum(img.height for img in aligned)

    merged = Image.new("RGB", (max_width, total_height))

    y = 0

    for img in aligned:
        merged.paste(img, (0, y))
        y += img.height

    save_path = os.path.join(TMP_DIR, "merged.png")

    merged.save(save_path)
    logger.debug(f"{save_path}가 저장되었습니다.")


def load_rgb(image_source: Union[str, bytes, os.PathLike]) -> Image.Image:
    """경로 또는 바이트(스토리지에서 다운로드한 이미지 등)를 불러와 RGB로 정규화한다.
    투명 배경(RGBA 등)은 IMAGE_BG_COLOR로 합성한다 (webp/png 등 포맷 차이 무관)."""

    source = BytesIO(image_source) if isinstance(image_source, (bytes, bytearray)) else image_source
    im = Image.open(source)

    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, IMAGE_BG_COLOR + (255,))
        im = Image.alpha_composite(bg, im)

    return im.convert("RGB")


def crop_echo_icons(image: Image.Image) -> List[Image.Image]:
    """공명자 프로필 스크린샷에서 에코 슬롯 1~5의 아이콘 영역만 크롭한다 (ORB 매칭 입력용)."""

    crops = [image.crop(rect) for rect in ECHO_ICON_RECTANGLES]

    for i, crop in enumerate(crops, start=1):
        save_path = os.path.join(TMP_DIR, f"echo_{i}.png")
        crop.save(save_path)
        logger.debug(f"{save_path}가 저장되었습니다.")

    return crops
