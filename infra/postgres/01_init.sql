-- =========================
-- weapon_master
-- =========================
CREATE TABLE IF NOT EXISTS weapon_master (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
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
CREATE TABLE IF NOT EXISTS resonator_master (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(20) NOT NULL UNIQUE,
    element VARCHAR(20) NOT NULL,
    rarity INT NOT NULL CHECK (rarity IN (4, 5)),
    hp INT NOT NULL,
    attack INT NOT NULL,
    defense INT NOT NULL,
    release_version INT NOT NULL,
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
-- user_resonators
-- =========================
CREATE TABLE IF NOT EXISTS user_resonators (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    resonance_chain_level INT NOT NULL CHECK (resonance_chain_level BETWEEN 0 AND 6),
    refine_level INT NOT NULL CHECK (refine_level BETWEEN 1 AND 5),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    resonator_master_id BIGINT NOT NULL,
    weapon_master_id BIGINT NOT NULL,

    CONSTRAINT fk_user_resonator_master
        FOREIGN KEY (resonator_master_id)
        REFERENCES resonator_master(id),

    CONSTRAINT fk_user_weapon
        FOREIGN KEY (weapon_master_id)
        REFERENCES weapon_master(id)
);


-- =========================
-- user_echoes
-- =========================
CREATE TABLE IF NOT EXISTS user_echoes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

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


-- =========================
-- user_echo_sub
-- =========================
CREATE SEQUENCE IF NOT EXISTS user_echo_sub_seq
    START WITH 1
    INCREMENT BY 50
    CACHE 50;

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


-- =========================
-- user_resonance_nodes
-- =========================
CREATE SEQUENCE IF NOT EXISTS user_node_seq
    START WITH 1
    INCREMENT BY 50
    CACHE 50;

CREATE TABLE IF NOT EXISTS user_resonance_nodes (
    id BIGINT PRIMARY KEY DEFAULT nextval('user_node_seq'),

    branch_position VARCHAR(20) NOT NULL CHECK (branch_position IN ('left_outer', 'left_inner', 'center', 'right_outer', 'right_inner')),
    node_position VARCHAR(20) NOT NULL CHECK (node_position IN ('top', 'middle')),

    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    user_resonator_id BIGINT NOT NULL,

    CONSTRAINT fk_user_node_resonator
        FOREIGN KEY (user_resonator_id)
        REFERENCES user_resonators(id)
);


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

    user_resonator_id BIGINT NOT NULL,

    CONSTRAINT fk_final_stats_resonator
        FOREIGN KEY (user_resonator_id)
        REFERENCES user_resonators(id)
);