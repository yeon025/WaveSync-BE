# 에코 서브속성 점수 계산에 쓰는 고정 가중치와 등급 기준.
# 계산 로직은 resonator/echo_score_service.py에 있고, 여기엔 값만 둔다.

CRIT_DMG_WEIGHT = 2
CRIT_RATE_WEIGHT = 1
ENERGY_REGEN_WEIGHT = 2 / 3
SCALING_STAT_WEIGHT = 2 / 3
DMG_TYPE_WEIGHT = 2 / 3

GRADE_THRESHOLDS = {
    "SS": 75,
    "S": 65,
    "A": 55,
    "B": 45,
    "C": 30,
}
