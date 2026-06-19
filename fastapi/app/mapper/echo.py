import re
from enum import Enum, auto
from schemas.response import Echo, Stat





# 상태 정의 (Enum을 사용하여 현재 어떤 파싱 단계인지 명시)
class ParseState(Enum):
    START = auto()
    MAIN_VALUE_PENDING = auto()
    SECONDARY_OPTION_PENDING = auto()
    COLLECTING_SUBS = auto()

class EchoMapper:
    def __init__(self):
        self.final_list = []
        self.current_echo = None
        self.current_subs = []
        self.state = ParseState.START



    def _finalize_echo(self):
        # 현재까지 작업하던 Echo를 결과 리스트에 담고 정리
        if self.current_echo:
            self.current_echo.sub = self.current_subs
            self.final_list.append(self.current_echo)
        
        self.current_echo = None
        self.current_subs = []



    def run(self, merged_texts):
        # 인덱스 2번부터 순회
        for text in merged_texts[2:]:
            # 데이터 추출 (Type, Value, Percent 여부)
            match = re.match(r"(.*?)\s*([\d.]+)\s*(%)?$", text)

            # --- 흐름 제어 (Flow Control) 핵심 로직 ---
            
            # 1. 새로운 Echo 세션 시작 조건 (매칭되지 않는 텍스트가 들어왔을 때)
            if not match:
                self._finalize_echo()
                self.current_echo = Echo(main=text)
                self.state = ParseState.MAIN_VALUE_PENDING
                continue

            # 2. 상태에 따른 데이터 처리 (Strategy 역할)
            self._process_by_state(match)

        # 마지막으로 작업 중이던 객체 저장
        self._finalize_echo()
        return self.final_list


    def _process_by_state(self, match):
        # 현재 상태에 따라 매칭된 데이터를 적절한 필드에 할당
        label = match.group(1).strip()
        value = match.group(2)
        is_percent = match.group(3) is not None

        if self.state == ParseState.MAIN_VALUE_PENDING:
            self.current_echo.mainValue = f"{value}%" if is_percent else value
            self.state = ParseState.SUB_OPTION_PENDING

        elif self.state == ParseState.SECONDARY_OPTION_PENDING:
            self.current_echo.secondaryType = label
            self.current_echo.secondaryValue = float(value) if '.' in value else int(value)
            self.state = ParseState.COLLECTING_SUBS

        elif self.state == ParseState.COLLECTING_SUBS:
            formatted_value = f"{value}%" if is_percent else value
            new_sub = Stat(type=label, value=formatted_value)
            self.current_subs.append(new_sub)