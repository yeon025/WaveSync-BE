import re
from io import BytesIO
from typing import List, NamedTuple

from google.cloud import vision
from PIL import Image

from app.profile_extraction.ocr.vision_client import create_vision_client


class ProfileTextLines(NamedTuple):
    resonator_name: str
    weapon_name: str
    echo_lines: List[str]


def extract_text(image: Image.Image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    vision_image = vision.Image(content=buffer.getvalue())

    client = create_vision_client()

    return client.document_text_detection(image=vision_image)


def process_ocr_result(response):
    words_data = _extract_words(response.full_text_annotation)
    return _group_into_lines(words_data)


def _extract_words(annotation):
    words_data = []
    for page in annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    text = "".join(s.text for s in word.symbols)
                    vertices = word.bounding_box.vertices
                    words_data.append({"text": text, "x": vertices[0].x, "y": vertices[0].y})
    return words_data


def _group_into_lines(words_data):
    lines = []

    for word in sorted(words_data, key=lambda w: w["y"]):
        for line in lines:
            if abs(word["y"] - line[0]["y"]) < 20:
                line.append(word)
                break
        else:
            lines.append([word])

    result = []

    for line in lines:
        words_in_line = sorted(line, key=lambda w: w["x"])
        line_text = " ".join(word["text"] for word in words_in_line)
        result.append(line_text)

    return result


def clean_text(raw_texts):
    final_texts = []

    for text in raw_texts:
        cleaned = re.sub(r"LV[.\s]?\d+", "", text).strip()

        if cleaned:
            final_texts.append(cleaned)

    return final_texts


def split_profile_text_lines(cleaned_texts: List[str]) -> ProfileTextLines:
    # 줄 순서는 text_region_builder.RECTANGLES 순서(공명자 이름, 무기 이름, 에코 옵션)를 전제한다.
    resonator_name = cleaned_texts[0].replace(" ", "")
    weapon_name = cleaned_texts[1].replace(" ", "")
    echo_lines = cleaned_texts[2:]

    return ProfileTextLines(resonator_name=resonator_name, weapon_name=weapon_name, echo_lines=echo_lines)
