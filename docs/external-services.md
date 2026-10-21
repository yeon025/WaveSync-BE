# 외부 서비스 — OCR

Google Cloud Vision API로 프로필 이미지에서 텍스트를 추출합니다. 이미지 전처리와 결과 파싱은 `profile_extraction/`이 담당합니다.

- Vision API는 등록 요청 1건당 1회만 호출합니다.
- 프로필 이미지에서 캐릭터 이름, 무기 이름, 에코 옵션 영역을 분리한 뒤 세로로 병합해 하나의 이미지로 요청합니다.
  (`ocr/text_region_builder.py`의 `crop_and_stack`)
- Vision 응답의 단어를 줄 단위로 병합하고 정제한 뒤, 병합 순서에 따라 캐릭터 이름, 무기 이름, 에코 옵션 줄로 나눕니다.
  (`ocr/ocr_service.py`의 `extract_text`)

구조를 건드릴 때는 호출 횟수가 늘지 않는지 반드시 확인합니다.
