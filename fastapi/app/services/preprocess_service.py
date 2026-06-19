import cv2
import numpy as np
import os
from app.config.constant import TMP_DIR, CIRCLES, RECTANGLES
from app.config.logger import logger


os.makedirs(TMP_DIR, exist_ok=True)


def crop_circles(image_path):
    image = cv2.imread(image_path)

    crops = []
    for cx, cy, r in CIRCLES:
        x1, y1, x2, y2 = cx - r, cy - r, cx + r, cy + r
        crop = image[y1:y2, x1:x2].copy()

        mask = np.zeros((2 * r, 2 * r), dtype=np.uint8)
        cv2.circle(mask, (r, r), r, 255, -1)

        circle_crop = cv2.bitwise_and(crop, crop, mask=mask)
        crops.append(circle_crop)

    for i, crop in enumerate(crops, start=1):
        save_path = os.path.join(TMP_DIR, f"resonance_chain_{i}.png")
        cv2.imwrite(save_path, crop)
        logger.debug(f"{save_path}가 저장되었습니다.")



def crop_and_stack(image_path):
    image = cv2.imread(image_path)

    crops = [image[y1:y2, x1:x2] for (x1, y1, x2, y2) in RECTANGLES]

    if not crops:
        return None

    max_width = max(crop.shape[1] for crop in crops)

    aligned = []
    for crop in crops:
        h, w = crop.shape[:2]
        pad_right = max_width - w

        padded = cv2.copyMakeBorder(
            crop,
            top=0,
            bottom=10,
            left=0,
            right=pad_right,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )

        aligned.append(padded)

    save_path = os.path.join(TMP_DIR, f"merged.png")
    cv2.imwrite(save_path, cv2.vconcat(aligned))
    logger.debug(f"{save_path}가 저장되었습니다.")
