import re
from io import BytesIO

from google.cloud import vision
from PIL import Image

from app.profile_extraction.ocr.vision_client import create_vision_client


def extract_text(image: Image.Image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    vision_image = vision.Image(content=buffer.getvalue())

    client = create_vision_client()

    return client.document_text_detection(image=vision_image)


def process_ocr_result(response):
    annotation = response.full_text_annotation

    words_data = _extract_words(annotation)
    lines = _group_into_lines(words_data)
    return lines


def _extract_words(annotation):
    words_data = []
    for page in annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    text = "".join([s.text for s in word.symbols])
                    vertices = word.bounding_box.vertices
                    words_data.append({"text": text, "x": vertices[0].x, "y": vertices[0].y})
    return words_data


def _group_into_lines(words_data):
    lines = []
    sorted_words = sorted(words_data, key=lambda w: w["y"])

    for word in sorted_words:
        placed = False
        for line in lines:
            if abs(word["y"] - line[0]["y"]) < 20:
                line.append(word)
                placed = True
                break
        if not placed:
            lines.append([word])

    result = []
    for line in lines:
        line.sort(key=lambda w: w["x"])
        result.append(" ".join([w["text"] for w in line]))
    return result


def clean_text(raw_texts):
    final_texts = []

    for text in raw_texts:
        cleaned = re.sub(r"LV[.\s]?\d+", "", text).strip()
        if cleaned:
            final_texts.append(cleaned)

    return final_texts
