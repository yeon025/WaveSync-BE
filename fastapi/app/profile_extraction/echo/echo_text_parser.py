import re
from enum import Enum, auto

from app.config.logger import logger
from app.profile_extraction.constants import (
    MAIN_STAT_MAP,
    SECONDARY_STAT_MAP,
    SUB_STAT_FLAT_MAP,
    SUB_STAT_PERCENT_MAP,
)
from app.profile_extraction.schemas import Echo, ExtractedStat


class ParseState(Enum):
    START = auto()
    MAIN_VALUE_PENDING = auto()
    SECONDARY_PENDING = auto()
    COLLECTING_SUBS = auto()


class EchoMapper:
    def __init__(self):
        self.final_list = []
        self.current_echo = Echo(
            main=ExtractedStat(type="", value=0),
            secondary=ExtractedStat(type="", value=0),
        )
        self.current_subs = []
        self.state = ParseState.START

    def _finalize_echo(self):
        if self.current_echo.main.type:
            self.current_echo.subs = self.current_subs
            self.final_list.append(self.current_echo)

        self.current_echo = Echo(
            main=ExtractedStat(type="", value=0),
            secondary=ExtractedStat(type="", value=0),
        )
        self.current_subs = []

    def run(self, echo_texts):
        for text in echo_texts:
            match = re.match(r"(.*?)\s*([\d.]+)\s*(%)?$", text)

            # 수치가 없는 텍스트는 다음 에코의 메인 옵션 이름이다.
            if not match:
                self._finalize_echo()

                text = MAIN_STAT_MAP.get(text, text)

                self.current_echo.main.type = text
                logger.debug(f"{len(self.final_list) + 1}번 에코의 main type은 {text}입니다.")
                self.state = ParseState.MAIN_VALUE_PENDING
                continue

            self._process_by_state(match)

        self._finalize_echo()
        return self.final_list

    def _process_by_state(self, match):
        raw_label = match.group(1).strip()
        value = match.group(2)
        is_percent = match.group(3) is not None

        if self.state == ParseState.MAIN_VALUE_PENDING:
            self.current_echo.main.value = float(value) if "." in value else int(value)
            self.state = ParseState.SECONDARY_PENDING
            logger.debug(f"{len(self.final_list) + 1}번 에코의 main value는 {value}%입니다.")

        elif self.state == ParseState.SECONDARY_PENDING:
            label = SECONDARY_STAT_MAP.get(raw_label, raw_label)

            self.current_echo.secondary.type = label
            self.current_echo.secondary.value = float(value) if "." in value else int(value)
            self.state = ParseState.COLLECTING_SUBS
            logger.debug(
                f"{len(self.final_list) + 1}번 에코의 secondary는 {label}, {self.current_echo.secondary.value}입니다."
            )

        elif self.state == ParseState.COLLECTING_SUBS:
            if is_percent:
                label = SUB_STAT_PERCENT_MAP.get(raw_label, raw_label)
            else:
                label = SUB_STAT_FLAT_MAP.get(raw_label, raw_label)

            value = float(value) if "." in value else int(value)

            value = change_defense_percent(label, value)

            new_sub = ExtractedStat(type=label, value=value)
            self.current_subs.append(new_sub)
            logger.debug(
                f"{len(self.final_list) + 1}번 에코의 {len(self.current_subs)}번 sub는 {label}, {value}입니다."
            )


def change_defense_percent(label, value):
    if label == "defense_percent" and value == 11.9:
        value = 11.8

    return value
