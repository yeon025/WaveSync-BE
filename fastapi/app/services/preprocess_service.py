import os

from PIL import Image, ImageDraw

from app.config.constant import CIRCLES, RECTANGLES, TMP_DIR
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
