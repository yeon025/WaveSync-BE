import re
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup, Tag

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode

_CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)
_HEADERS = {"User-Agent": "Mozilla/5.0"}
_TIMEOUT_SECONDS = 15

# 공명자 속성은 이 6종으로 고정되어 있다 (encore_client 쪽 _ELEMENT_NAME_MAP과 동일 집합).
_ATTRIBUTE_NAMES = ("응결", "용융", "전도", "기류", "회절", "인멸")

# namu.wiki가 동명이인 문서를 구분하려고 이름 뒤에 붙이는 표기. 예: "산화(명조: 워더링 웨이브)" -> "산화"
_DISAMBIGUATION_SUFFIX = re.compile(r"\(명조:\s*워더링\s*웨이브\)")


def _fetch_soup(url: str) -> BeautifulSoup:
    try:
        response = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if e.response is not None else None
        logger.error(f"나무위키 요청 실패: {url}, {e} (body={body})")
        raise CustomException(ErrorCode.EXTERNAL_API_FAILED)

    return BeautifulSoup(response.text, "html.parser")


def _find_attribute_heading(soup: BeautifulSoup) -> Optional[Tag]:
    # "3. 속성" 섹션의 <h2> 헤딩을 찾는다. 섹션 번호를 하드코딩하지 않고 id="속성" span, 없으면
    # id="s-3" 앵커로 폴백한다 (실제 응답에서 나무위키가 앵커 id를 섹션 제목/번호 기반으로 혼용해서 씀).
    for heading in soup.find_all("h2"):
        if heading.find("span", id="속성"):
            return heading
        if heading.find("a", id="s-3"):
            return heading

    return None


def crawl_character_urls() -> Dict[str, str]:
    """[ 속성 ] 섹션 아래 속성별 표(이름 tr 다음 형제 tr에 링크)에서 캐릭터 이름 -> 나무위키
    문서 URL 딕셔너리를 만든다. (character/1402 등 실제 응답 구조로 검증한 로직.)"""
    soup = _fetch_soup(_CHARACTER_LIST_URL)

    heading = _find_attribute_heading(soup)
    if heading is None:
        logger.error("나무위키 캐릭터 목록에서 [ 속성 ] 섹션을 찾을 수 없습니다 (페이지 구조가 바뀌었을 수 있습니다).")
        raise CustomException(ErrorCode.MASTER_DATA_SYNC_FAILED)

    character_urls: Dict[str, str] = {}
    seen_hrefs = set()

    # _ATTRIBUTE_NAMES로 "시작하는" tr을 찾는다 (실제 라벨은 "응결(Glacio | 冷凝)"처럼 영문/한자가
    # 붙어 있어 정확 일치 대신 접두어 일치로 확인한다).
    for el in heading.find_all_next():
        if el.name == "h2":
            break

        if el.name != "tr":
            continue

        label_text = el.get_text(strip=True)
        if not any(label_text.startswith(name) for name in _ATTRIBUTE_NAMES):
            continue

        data_tr = el.find_next_sibling("tr")
        if data_tr is None:
            continue

        for link in data_tr.find_all("a"):
            href = link.get("href")

            if not href or not href.startswith("/w/") or href in seen_hrefs:
                continue

            seen_hrefs.add(href)

            name = link.get("title")
            if not name:
                strong = link.find("strong")
                name = strong.get_text(strip=True) if strong else None

            if not name:
                continue

            name = _DISAMBIGUATION_SUFFIX.sub("", name).strip()
            if not name:
                continue

            # 방랑자는 원소별 하위 문서(예: /방랑자(...)/인멸)로 나뉘어 있지만 전신 이미지는
            # 공용 문서(/방랑자(...))에만 있으므로 하나로 합친다.
            if name.startswith("방랑자/"):
                name = "방랑자"
                href = href.rsplit("/", 1)[0]

            character_urls[name] = "https://namu.wiki" + href

    return character_urls


def _extract_img_src(img: Tag) -> Optional[str]:
    # 지연 로딩용 data-src를 우선한다.
    return img.get("data-src") or img.get("src")


def _to_https(src: str) -> str:
    if src.startswith("//"):
        return "https:" + src
    return src


def _find_standing_image(details_section: Tag) -> Optional[Tag]:
    # [ 스탠딩 ] details 내부의 실제 이미지를 찾는다. placeholder(data:image)는 제외한다.
    for img in details_section.select("img"):
        src = _extract_img_src(img)

        if not src or src.startswith("data:image"):
            continue

        return img

    return None


def find_standing_url(wiki_url: str, name: str) -> Optional[str]:
    """캐릭터 문서에서 [ 스탠딩 ] 섹션의 전신 이미지 URL을 찾는다. 섹션이나 이미지를 찾지
    못하면 None을 반환한다 — 호출부가 기존 standing_image를 지우지 않고 그대로 둬야 한다."""
    soup = _fetch_soup(wiki_url)

    summary = None
    for s in soup.find_all("summary"):
        if "스탠딩" in s.get_text(strip=True):
            summary = s
            break

    if summary is None:
        logger.info(f"{name}: 나무위키 문서에 스탠딩 섹션이 없습니다.")
        return None

    standing_section = summary.find_parent("details")
    if standing_section is None:
        logger.warning(f"{name}: 스탠딩 summary의 부모 details를 찾을 수 없습니다.")
        return None

    image = _find_standing_image(standing_section)
    if image is None:
        logger.warning(f"{name}: 스탠딩 섹션에 유효한 이미지가 없습니다.")
        return None

    src = _extract_img_src(image)
    # 참고 코드는 src가 "//"로 시작할 때만 값을 반환해, 이미 절대 URL(https://...)인 이미지는
    # 조용히 None이 되는 버그가 있었다. _to_https는 "//"가 아니면 원본을 그대로 돌려주므로
    # 항상 거쳐도 안전하다 — 여기서는 매번 호출해 그 버그를 고친다.
    return _to_https(src)
