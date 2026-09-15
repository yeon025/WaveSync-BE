import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "images/tmp")
TEMPLATE_DIR = os.path.join(BASE_DIR, "images/template")


CHAIN_IMG_DIRS = [
    os.path.join(TMP_DIR, "resonance_chain_1.png"),
    os.path.join(TMP_DIR, "resonance_chain_2.png"),
    os.path.join(TMP_DIR, "resonance_chain_3.png"),
    os.path.join(TMP_DIR, "resonance_chain_4.png"),
    os.path.join(TMP_DIR, "resonance_chain_5.png"),
    os.path.join(TMP_DIR, "resonance_chain_6.png"),
]
TEMPLATE_IMG_DIR = os.path.join(TEMPLATE_DIR, "locked_resonance_chain.png")


RECTANGLES = [
    # 공명자 이름
    (62, 16, 750, 82),
    # 무기 이름
    (1603, 449, 1850, 484),
    # 에코
    (220, 720, 380, 750),  # 에코 주옵 옵션
    (315, 750, 380, 790),  # 에코 주옵 수치
    (63, 840, 380, 875),  # 에코 보조옵
    (63, 875, 380, 910),  # 에코 부옵 1
    (63, 910, 380, 945),  # 에코 부옵 2
    (63, 945, 380, 980),  # 에코 부옵 3
    (63, 980, 380, 1015),  # 에코 부옵 4
    (63, 1015, 380, 1050),  # 에코 부옵 5
    # ====================================
    (590, 720, 760, 750),  # 에코 주옵 옵션
    (685, 750, 760, 790),  # 에코 주옵 수치
    (436, 840, 760, 875),  # 에코 보조옵
    (436, 875, 760, 910),  # 에코 부옵 1
    (436, 910, 760, 945),  # 에코 부옵 2
    (436, 945, 760, 980),  # 에코 부옵 3
    (436, 980, 760, 1015),  # 에코 부옵 4
    (436, 1015, 760, 1050),  # 에코 부옵 5
    # ====================================
    (970, 720, 1135, 750),  # 에코 주옵 옵션
    (1060, 750, 1135, 790),  # 에코 주옵 수치
    (811, 840, 1135, 875),  # 에코 보조옵
    (811, 875, 1135, 910),  # 에코 부옵 1
    (811, 910, 1135, 945),  # 에코 부옵 2
    (811, 945, 1135, 980),  # 에코 부옵 3
    (811, 980, 1135, 1015),  # 에코 부옵 4
    (811, 1015, 1135, 1050),  # 에코 부옵 5
    # ====================================
    (1340, 720, 1505, 750),  # 에코 주옵 옵션
    (1435, 750, 1505, 790),  # 에코 주옵 수치
    (1185, 840, 1505, 875),  # 에코 보조옵
    (1185, 875, 1505, 910),  # 에코 부옵 1
    (1185, 910, 1505, 945),  # 에코 부옵 2
    (1185, 945, 1505, 980),  # 에코 부옵 3
    (1185, 980, 1505, 1015),  # 에코 부옵 4
    (1185, 1015, 1505, 1050),  # 에코 부옵 5
    # ====================================
    (1720, 720, 1880, 750),  # 에코 주옵 옵션
    (1815, 750, 1880, 790),  # 에코 주옵 수치
    (1562, 840, 1880, 875),  # 에코 보조옵
    (1562, 875, 1880, 910),  # 에코 부옵 1
    (1562, 910, 1880, 945),  # 에코 부옵 2
    (1562, 945, 1880, 980),  # 에코 부옵 3
    (1562, 980, 1880, 1015),  # 에코 부옵 4
    (1562, 1015, 1880, 1050),  # 에코 부옵 5
]


CIRCLES = [
    # 돌파
    (189, 575, 15),
    (263, 575, 15),
    (343, 575, 15),
    (423, 575, 15),
    (503, 575, 15),
    (583, 575, 15),
]


# 에코 슬롯 1~5의 "아이콘" 영역 (ORB 매칭용)
ECHO_ICON_RECTANGLES = [
    (20, 648, 214, 831),  # 1 이미지
    (398, 648, 587, 831),  # 2 이미지
    (768, 648, 963, 831),  # 3 이미지
    (1142, 648, 1335, 831),  # 4 이미지
    (1518, 648, 1708, 831),  # 5 이미지
]


# 이미지 투명 배경을 합성할 배경색 (게임 내 슬롯이 어두우므로 검은색)
IMAGE_BG_COLOR = (0, 0, 0)

# 에코 ORB 특징 로컬 캐시 (echo-images 버킷 객체를 매번 다운로드/재계산하지 않기 위함)
ECHO_ORB_CACHE_PATH = os.path.join(TMP_DIR, "echo_orb_cache.pkl")

# cv2.ORB_create 파라미터
ECHO_ORB_PROC_SIZE = 256  # 비교 전 통일할 이미지 크기 (정사각형, px)
ECHO_ORB_NFEATURES = 800
ECHO_ORB_SCALE_FACTOR = 1.2
ECHO_ORB_NLEVELS = 8
ECHO_ORB_FAST_THRESHOLD = 20

# 매칭 방식: "ratio" (knnMatch + Lowe ratio test) | "crosscheck" (BFMatcher crossCheck=True)
ECHO_MATCHER_MODE = "ratio"
ECHO_LOWE_RATIO = 0.75  # Lowe ratio test 임계값 (ECHO_MATCHER_MODE == "ratio"일 때)
ECHO_MIN_KEYPOINTS = 8  # 매칭 성립을 위한 최소 특징점 수
ECHO_MIN_MARGIN_RATIO = 0.12  # 1등이 2등보다 (1등점수 * 이 비율) 이상 높아야 채택, 아니면 모호 → None


MAIN_STAT_MAP = {
    "HP": "hp_percent",
    "공격력": "attack_percent",
    "방어력": "defense_percent",
    "공명 효율": "energy_regen",
    "크리티컬": "critical_rate",
    "크리티컬 피해": "critical_damage",
    "응결 피해 보너스": "glacio_damage_bonus",
    "용융 피해 보너스": "fusion_damage_bonus",
    "전도 피해 보너스": "conducto_damage_bonus",
    "기류 피해 보너스": "aero_damage_bonus",
    "회절 피해 보너스": "spectra_damage_bonus",
    "인멸 피해 보너스": "havoc_damage_bonus",
    "치료 효과 보너스": "healing_bonus",
}


SECONDARY_STAT_MAP = {"HP": "hp", "공격력": "attack"}


SUB_STAT_PERCENT_MAP = {
    "HP": "hp_percent",
    "공격력": "attack_percent",
    "방어력": "defense_percent",
    "공명 효율": "energy_regen",
    "크리티컬": "critical_rate",
    "크리티컬 피해": "critical_damage",
    "공명 스킬 피해 보너스": "resonance_skill_damage_bonus",
    "일반 공격 피해 보너스": "basic_attack_damage_bonus",
    "강공격 피해 보너스": "heavy_attack_damage_bonus",
    "공명 해방 피해 보너스": "resonance_liberation_damage_bonus",
    "치료 효과 보너스": "healing_bonus",
}

SUB_STAT_FLAT_MAP = {"HP": "hp", "공격력": "attack", "방어력": "defense"}
