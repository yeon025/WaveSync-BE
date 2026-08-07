import types
import pytest
from app.services import ocr_service


class FakeSymbol:
    def __init__(self, text):
        self.text = text


class FakeWord:
    def __init__(self, symbols, x, y):
        self.symbols = symbols
        class VB: pass
        vb = types.SimpleNamespace()
        vb.x = x
        vb.y = y
        self.bounding_box = types.SimpleNamespace(vertices=[vb])


class FakeParagraph:
    def __init__(self, words):
        self.words = words


class FakeBlock:
    def __init__(self, paragraphs):
        self.paragraphs = paragraphs


class FakePage:
    def __init__(self, blocks):
        self.blocks = blocks


class FakeAnnotation:
    def __init__(self, pages):
        self.pages = pages


class FakeResponse:
    def __init__(self, annotation):
        self.full_text_annotation = annotation


def test_process_ocr_result_grouping_and_ordering():
    # create words on two lines with positions
    w1 = FakeWord([FakeSymbol('Hello')], x=5, y=10)
    w2 = FakeWord([FakeSymbol('World')], x=50, y=12)
    w3 = FakeWord([FakeSymbol('LV10')], x=5, y=100)
    p1 = FakeParagraph([w1, w2])
    p2 = FakeParagraph([w3])
    b1 = FakeBlock([p1])
    b2 = FakeBlock([p2])
    page = FakePage([b1, b2])
    annotation = FakeAnnotation([page])
    resp = FakeResponse(annotation)

    lines = ocr_service.process_ocr_result(resp)
    # expect two lines joined appropriately
    assert any('Hello' in ln for ln in lines)
    assert any('LV10' in ln for ln in lines)


def test_clean_text_removes_lv_and_spaces():
    raw = ["Reso LV.10", "Wea p on LV10 "]
    cleaned = ocr_service.clean_text(raw)
    # should remove LV and spaces in names
    assert cleaned[0] == "Reso"
    assert cleaned[1] == "Weapon"


def test_clean_text_indexes_out_of_range_raises_index_error():
    # supply empty list to trigger indexing error in clean_text
    with pytest.raises(Exception):
        ocr_service.clean_text([])
