CREATE_EXTENSION_UUID = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

CREATE_USER_TYPE_ENUM = """
CREATE TYPE USER_TYPE AS ENUM ('ADMIN', 'PATIENT', 'DOCTOR', 'HEALTHCARE PROFESSIONAL', 'PARENT');
"""

DROP_USER_TYPE_ENUM = "DROP TYPE IF EXISTS USER_TYPE CASCADE;"

CREATE_USER_ID_INDEX = "CREATE INDEX idx_user_id ON users(user_id);"
DROP_USER_ID_INDEX = "DROP INDEX IF EXISTS idx_user_id RESTRICT"
CREATE_MEDICAL_INSURANCE_ID_INDEX = "CREATE INDEX idx_medical_insurance_id ON users(medical_insurance_id);"
DROP_MEDICAL_INSURANCE_ID_INDEX = "DROP INDEX IF EXISTS idx_medical_insurance_id RESTRICT"

CREATE_COORDINATE_ID_INDEX = "CREATE INDEX idx_coordinate_id ON coordinates(coordinate_id);"
DROP_COORDINATE_ID_INDEX = "DROP INDEX IF EXISTS idx_coordinate_id RESTRICT"

CREATE_HISTORY_ID_INDEX = "CREATE INDEX idx_history_id ON medical_history(history_id);"
DROP_HISTORY_ID_INDEX = "DROP INDEX IF EXISTS idx_history_id RESTRICT"

CREATE_VISIT_ID_INDEX = "CREATE INDEX idx_visit_id ON medical_visits(visit_id);"
DROP_VISIT_ID_INDEX = "DROP INDEX IF EXISTS idx_visit_id RESTRICT"

CREATE_JTI_INDEX = "CREATE INDEX idx_jti ON token_blacklist(jti);"
DROP_JTI_INDEX = "DROP INDEX IF EXISTS idx_jti RESTRICT;"
CREATE_USER_BLACKLIST_INDEX = "CREATE INDEX idx_user_blacklist ON token_blacklist(user_id);"
DROP_USER_BLACKLIST_INDEX = "DROP INDEX IF EXISTS idx_user_blacklist RESTRICT;"

CREATE_MFA_CONFIG_INDEX = "CREATE INDEX idx_mfa_user_id ON mfa_config(user_id);"
DROP_MFA_CONFIG_INDEX = "DROP INDEX IF EXISTS idx_mfa_user_id RESTRICT;"

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    unique_id               SERIAL PRIMARY KEY,
    user_id                 UUID NOT NULL DEFAULT uuid_generate_v4(),
    medical_insurance_id    TEXT,
    login                   TEXT NOT NULL DEFAULT '',
    password_hash           TEXT NOT NULL DEFAULT '',
    user_type               USER_TYPE NOT NULL DEFAULT 'PARENT',
    first_name              TEXT NOT NULL,
    last_name               TEXT NOT NULL,
    phone_number            TEXT NOT NULL,
    email                   TEXT NOT NULL,
    gender                  TEXT,
    city_of_birth           TEXT,
    date_of_birth           DATE,
    hidden                  BOOL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

DROP_USERS_TABLE = "DROP TABLE IF EXISTS users CASCADE;"

CREATE_PARENTS_TABLE = """
CREATE TABLE IF NOT EXISTS parents (
    parent_id       UUID NOT NULL,
    child_id        UUID NOT NULL,
    hidden          BOOL DEFAULT FALSE,

    PRIMARY KEY(parent_id, child_id)
);
"""

DROP_PARENTS_TABLE = "DROP TABLE IF EXISTS parents CASCADE;"

CREATE_COORDINATES_TABLE = """
CREATE TABLE IF NOT EXISTS coordinates (
    unique_id           SERIAL PRIMARY KEY,
    coordinate_id       UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    street_address      TEXT NOT NULL,
    apartment           TEXT,
    postal_code         TEXT NOT NULL,
    city                TEXT NOT NULL,
    country             TEXT NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hidden              BOOL DEFAULT FALSE
);
"""

DROP_COORDINATES_TABLE = "DROP TABLE IF EXISTS coordinates CASCADE;"

CREATE_MEDICAL_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS medical_history (
    unique_id           SERIAL PRIMARY KEY,
    history_id          UUID NOT NULL DEFAULT uuid_generate_v4(),
    patient_id          TEXT NOT NULL,
    diagnostic          TEXT NOT NULL,
    treatment           TEXT NOT NULL,
    doctor_id           UUID NOT NULL,
    start_date          DATE,
    end_date            DATE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hidden              BOOL DEFAULT FALSE
);
"""

DROP_MEDICAL_HISTORY_TABLE = "DROP TABLE IF EXISTS medical_history CASCADE;"

CREATE_MEDICAL_VISITS_TABLE = """
CREATE TABLE IF NOT EXISTS medical_visits (
    unique_id               SERIAL PRIMARY KEY,
    visit_id                UUID NOT NULL DEFAULT uuid_generate_v4(),
    patient_id              TEXT NOT NULL,
    establishment_id        UUID NOT NULL,
    doctor_id               UUID NOT NULL,
    visit_date              TIMESTAMP WITH TIME ZONE,
    diagnostic_established  TEXT,
    treatment               TEXT,
    visit_summary           TEXT NOT NULL,
    notes                   TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hidden                  BOOL DEFAULT FALSE,
    FOREIGN KEY (establishment_id) REFERENCES establishments(establishment_id)
);
"""

DROP_MEDICAL_VISITS_TABLE = "DROP TABLE IF EXISTS medical_visits CASCADE;"

CREATE_ESTABLISHMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS establishments (
    establishment_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    establishment_name      TEXT NOT NULL,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hidden                  BOOL DEFAULT FALSE
);
"""

DROP_ESTABLISHMENTS_TABLE = "DROP TABLE IF EXISTS establishments CASCADE;"

CREATE_TOKEN_BLACKLIST_TABLE = """
CREATE TABLE IF NOT EXISTS token_blacklist (
    id              SERIAL PRIMARY KEY,
    jti             VARCHAR(36) NOT NULL UNIQUE,
    token_type      VARCHAR(10) NOT NULL,
    user_id         UUID NOT NULL,
    revoked_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    hidden          BOOL DEFAULT FALSE
);
"""

DROP_TOKEN_BLACKLIST_TABLE = "DROP TABLE IF EXISTS token_blacklist CASCADE;"

CREATE_MFA_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS mfa_config (
    user_id         UUID PRIMARY KEY,
    secret          TEXT NOT NULL,
    enabled         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    backup_codes    TEXT[] DEFAULT ARRAY[]::TEXT[],
    hidden          BOOLEAN DEFAULT FALSE
);
"""

DROP_MFA_CONFIG_TABLE = "DROP TABLE IF EXISTS mfa_config CASCADE;"
