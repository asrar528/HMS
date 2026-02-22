"""
Database Schema Manager for HMS Application.

Defines and applies all DDL statements (CREATE TABLE, indexes, etc.)
in a single, versioned migration approach.
"""

from __future__ import annotations

from app.database.connection import DatabaseConnection


# ---------------------------------------------------------------------------
# DDL – Hospital Registration Table
# ---------------------------------------------------------------------------

SQL_CREATE_HOSPITALS = """
CREATE TABLE IF NOT EXISTS hospitals (
    id                      INTEGER  PRIMARY KEY AUTOINCREMENT,

    -- Identity
    hospital_name           TEXT     NOT NULL,
    registration_number     TEXT     NOT NULL UNIQUE,
    hospital_type           TEXT     NOT NULL,          -- Government / Private / Semi-Government / Trust / Charitable
    specialization_type     TEXT     NOT NULL,          -- Multi-Specialty / Super-Specialty / General / Single-Specialty

    -- Location
    address_line1           TEXT     NOT NULL,
    address_line2           TEXT,
    city                    TEXT     NOT NULL,
    state                   TEXT     NOT NULL,
    pin_code                TEXT     NOT NULL,
    country                 TEXT     NOT NULL DEFAULT 'India',

    -- Contact
    phone_primary           TEXT     NOT NULL,
    phone_alternate         TEXT,
    emergency_contact       TEXT     NOT NULL,
    email                   TEXT     NOT NULL,
    website                 TEXT,

    -- Capacity
    total_beds              INTEGER  NOT NULL CHECK(total_beds > 0),
    icu_beds                INTEGER  DEFAULT 0,
    operation_theaters      INTEGER  DEFAULT 0,

    -- Administration
    administrator_name      TEXT     NOT NULL,
    license_number          TEXT     NOT NULL UNIQUE,
    accreditation           TEXT     DEFAULT 'None',   -- NABH / JCI / ISO / None
    established_year        INTEGER  NOT NULL,
    gstin                   TEXT,

    -- Metadata
    is_active               INTEGER  NOT NULL DEFAULT 1,
    created_at              TEXT     NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at              TEXT     NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

SQL_CREATE_HOSPITAL_UPDATED_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS trg_hospital_updated_at
    AFTER UPDATE ON hospitals
    FOR EACH ROW
BEGIN
    UPDATE hospitals
       SET updated_at = datetime('now','localtime')
     WHERE id = OLD.id;
END;
"""

SQL_CREATE_HOSPITALS_IDX_REG = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_hospitals_reg_no
    ON hospitals (registration_number);
"""

SQL_CREATE_HOSPITALS_IDX_LICENSE = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_hospitals_license
    ON hospitals (license_number);
"""

# ---------------------------------------------------------------------------
# DDL – Schema version tracking
# ---------------------------------------------------------------------------

SQL_CREATE_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    description TEXT
);
"""

# ---------------------------------------------------------------------------
# All migrations in order – add new entries; never modify existing ones
# ---------------------------------------------------------------------------

MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (
        1,
        "Initial schema – hospitals table",
        [
            SQL_CREATE_SCHEMA_VERSION,
            SQL_CREATE_HOSPITALS,
            SQL_CREATE_HOSPITAL_UPDATED_TRIGGER,
            SQL_CREATE_HOSPITALS_IDX_REG,
            SQL_CREATE_HOSPITALS_IDX_LICENSE,
        ],
    ),
]


class SchemaManager:
    """Applies pending DDL migrations to bring the database up to date."""

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def migrate(self) -> None:
        """Apply all pending migrations in version order."""
        self._ensure_version_table()
        current_version = self._get_current_version()

        for version, description, statements in MIGRATIONS:
            if version <= current_version:
                continue  # Already applied

            conn = self._db.get_connection()
            try:
                for sql in statements:
                    conn.execute(sql)
                conn.execute(
                    "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                    (version, description),
                )
                conn.commit()
                print(f"[SchemaManager] Applied migration v{version}: {description}")
            except Exception as exc:
                conn.rollback()
                raise RuntimeError(
                    f"[SchemaManager] Migration v{version} failed: {exc}"
                ) from exc

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_version_table(self) -> None:
        conn = self._db.get_connection()
        conn.execute(SQL_CREATE_SCHEMA_VERSION)
        conn.commit()

    def _get_current_version(self) -> int:
        cursor = self._db.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        )
        row = cursor.fetchone()
        return int(row[0]) if row else 0
