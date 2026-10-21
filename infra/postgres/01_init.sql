-- =========================
-- weapon_master
-- =========================
-- id는 Encore API의 무기 ID를 그대로 쓴다 (admin/master_data_sync_service.py). 별도 매핑 컬럼을 두지 않는다.
CREATE TABLE IF NOT EXISTS weapon_master (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    attack_value INT NOT NULL,
    main_type VARCHAR(50) NOT NULL,
    main_value NUMERIC(5,1) NOT NULL,
    refine_type VARCHAR(50),
    refine_1_value NUMERIC(5,1),
    refine_2_value NUMERIC(5,1),
    refine_3_value NUMERIC(5,1),
    refine_4_value NUMERIC(5,1),
    refine_5_value NUMERIC(5,1),
    image VARCHAR(255) NOT NULL
);


-- =========================
-- resonator_master
-- =========================
-- id는 Encore API의 캐릭터 ID를 그대로 쓴다. 방랑자는 원소별로 성별 변형(encore_id 2개, name 동일)이
-- 있지만 admin/master_data_sync_service.py의 sync_resonators가 남자 쪽만 동기화하므로 name은 그대로
-- UNIQUE로 둔다.
CREATE TABLE IF NOT EXISTS resonator_master (
    id BIGINT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    element VARCHAR(20) NOT NULL,
    rarity INT NOT NULL CHECK (rarity IN (4, 5)),
    hp INT NOT NULL,
    attack INT NOT NULL,
    defense INT NOT NULL,
    thumbnail_image VARCHAR(255) NOT NULL,
    standing_image VARCHAR(255)
);


-- =========================
-- resonance_node_master
-- =========================
CREATE TABLE IF NOT EXISTS resonance_node_master (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    outer_node_type VARCHAR(50) NOT NULL,
    outer_top_node_value NUMERIC(5,1) NOT NULL,
    outer_middle_node_value NUMERIC(5,1) NOT NULL,

    inner_node_type VARCHAR(50) NOT NULL,
    inner_top_node_value NUMERIC(5,1) NOT NULL,
    inner_middle_node_value NUMERIC(5,1) NOT NULL,

    resonator_master_id BIGINT NOT NULL UNIQUE,

    CONSTRAINT fk_resonance_node_resonator
        FOREIGN KEY (resonator_master_id)
        REFERENCES resonator_master(id)
);


-- =========================
-- master_data_sync_status
-- =========================
-- 대상(SyncTarget.value)당 가장 최근 동기화 실행 결과 1행만 유지한다(이력 테이블이 아니라 최신 상태만).
CREATE TABLE IF NOT EXISTS master_data_sync_status (
    target VARCHAR(30) PRIMARY KEY,

    synced_at TIMESTAMPTZ NOT NULL,
    success BOOLEAN NOT NULL,

    created INT,
    updated INT,
    unchanged INT,
    skipped INT,

    error_message VARCHAR(500)
);


-- =========================
-- users
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- =========================
-- user_sessions
-- =========================
-- 쿠키에는 원문 토큰만 담고 여기엔 SHA-256 해시만 저장한다 (원문은 서버에 남지 않음).
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    user_id BIGINT NOT NULL,
    token_hash VARCHAR(64) NOT NULL UNIQUE,

    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_user_session_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);


-- =========================
-- user_identities
-- =========================
-- Google sub 등 외부 로그인 식별자를 내부 user_id와 연결한다. 이메일이 아니라 provider+subject로만
-- 매칭한다(이메일 기반 자동 병합 금지). 이 테이블에 행이 없는 users는 게스트로 취급한다
-- (app/auth/session_service.py의 is_guest).
CREATE TABLE IF NOT EXISTS user_identities (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    provider VARCHAR(20) NOT NULL CHECK (provider IN ('google')),
    provider_user_id VARCHAR(255) NOT NULL,

    user_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_user_identity_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT uq_user_identities_provider_subject
        UNIQUE (provider, provider_user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_identities_user_id ON user_identities(user_id);


-- =========================
-- user_resonators
-- =========================
CREATE TABLE IF NOT EXISTS user_resonators (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    resonance_chain_level INT NOT NULL CHECK (resonance_chain_level BETWEEN 0 AND 6),
    refine_level INT NOT NULL CHECK (refine_level BETWEEN 1 AND 5),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    user_id BIGINT NOT NULL,
    resonator_master_id BIGINT NOT NULL,
    weapon_master_id BIGINT NOT NULL,

    CONSTRAINT fk_user_resonator_owner
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT fk_user_resonator_master
        FOREIGN KEY (resonator_master_id)
        REFERENCES resonator_master(id),

    CONSTRAINT fk_user_weapon
        FOREIGN KEY (weapon_master_id)
        REFERENCES weapon_master(id)
);

-- Postgres는 FK에 자동으로 인덱스를 만들지 않는다. user_id/resonator_master_id는 PK와 결합되지 않은
-- 단독 조건으로 조회된다(find_resonator_summary의 LEFT JOIN, find_ids_by_resonator_name의 JOIN).
CREATE INDEX IF NOT EXISTS idx_user_resonators_user_id ON user_resonators(user_id);
CREATE INDEX IF NOT EXISTS idx_user_resonators_resonator_master_id ON user_resonators(resonator_master_id);


-- =========================
-- user_echoes
-- =========================
CREATE TABLE IF NOT EXISTS user_echoes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    name VARCHAR(50),

    image VARCHAR(255),

    main_type VARCHAR(50) NOT NULL,
    main_value NUMERIC(5,1) NOT NULL,

    secondary_type VARCHAR(50) NOT NULL,
    secondary_value INT NOT NULL,

    user_resonator_id BIGINT NOT NULL,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_user_echo_resonator
        FOREIGN KEY (user_resonator_id)
        REFERENCES user_resonators(id)
);

-- 에코 목록 selectinload와 소프트삭제 캐스케이드가 이 컬럼으로 단독 조회한다.
CREATE INDEX IF NOT EXISTS idx_user_echoes_user_resonator_id ON user_echoes(user_resonator_id);


-- =========================
-- user_echo_sub
-- =========================
-- INCREMENT BY / CACHE = 25 (에코 서브 옵션 쓰기 단위: 최대 5에코 x 5서브)
CREATE SEQUENCE IF NOT EXISTS user_echo_sub_seq
    START WITH 1
    INCREMENT BY 25
    CACHE 25;

CREATE TABLE IF NOT EXISTS user_echo_sub (
    id BIGINT PRIMARY KEY DEFAULT nextval('user_echo_sub_seq'),

    type VARCHAR(50) NOT NULL,
    value NUMERIC(7,1) NOT NULL,

    user_echo_id BIGINT NOT NULL,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_echo_sub
        FOREIGN KEY (user_echo_id)
        REFERENCES user_echoes(id)
);

-- 서브속성 중첩 selectinload와 소프트삭제 캐스케이드가 이 컬럼으로 단독 조회한다.
CREATE INDEX IF NOT EXISTS idx_user_echo_sub_user_echo_id ON user_echo_sub(user_echo_id);


-- =========================
-- user_resonance_nodes
-- =========================
-- INCREMENT BY / CACHE = 10 (공명 노드 쓰기 단위: BranchPosition 5 x NodePosition 2 고정)
CREATE SEQUENCE IF NOT EXISTS user_node_seq
    START WITH 1
    INCREMENT BY 10
    CACHE 10;

CREATE TABLE IF NOT EXISTS user_resonance_nodes (
    id BIGINT PRIMARY KEY DEFAULT nextval('user_node_seq'),

    branch_position VARCHAR(20) NOT NULL CHECK (branch_position IN ('left_outer', 'left_inner', 'center', 'right_outer', 'right_inner')),
    node_position VARCHAR(20) NOT NULL CHECK (node_position IN ('top', 'middle')),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    user_resonator_id BIGINT NOT NULL,

    CONSTRAINT fk_user_node_resonator
        FOREIGN KEY (user_resonator_id)
        REFERENCES user_resonators(id)
);

-- 설정 조회 시 노드 로드와 소프트삭제 캐스케이드가 이 컬럼으로 단독 조회한다.
CREATE INDEX IF NOT EXISTS idx_user_resonance_nodes_user_resonator_id ON user_resonance_nodes(user_resonator_id);


-- =========================
-- final_stats
-- =========================
CREATE TABLE IF NOT EXISTS final_stats (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    hp INT NOT NULL,
    attack INT NOT NULL,
    defense INT NOT NULL,

    energy_regen NUMERIC(5,1) NOT NULL,
    critical_rate NUMERIC(5,1) NOT NULL,
    critical_damage NUMERIC(5,1) NOT NULL,

    resonance_skill_damage_bonus NUMERIC(5,1) NOT NULL,
    basic_attack_damage_bonus NUMERIC(5,1) NOT NULL,
    heavy_attack_damage_bonus NUMERIC(5,1) NOT NULL,
    resonance_liberation_damage_bonus NUMERIC(5,1) NOT NULL,

    glacio_damage_bonus NUMERIC(5,1) NOT NULL,
    fusion_damage_bonus NUMERIC(5,1) NOT NULL,
    conducto_damage_bonus NUMERIC(5,1) NOT NULL,
    aero_damage_bonus NUMERIC(5,1) NOT NULL,
    spectra_damage_bonus NUMERIC(5,1) NOT NULL,
    havoc_damage_bonus NUMERIC(5,1) NOT NULL,
    healing_bonus NUMERIC(5,1) NOT NULL,

    -- UserResonator.final_stat을 1:1(uselist=False)로 다루므로 UNIQUE로 DB에서도 보장한다.
    user_resonator_id BIGINT NOT NULL UNIQUE,

    CONSTRAINT fk_final_stats_resonator
        FOREIGN KEY (user_resonator_id)
        REFERENCES user_resonators(id)
);