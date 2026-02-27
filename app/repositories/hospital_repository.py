"""
Hospital Repository – Data Access Layer.

Defines the abstract interface (IHospitalRepository) and its
concrete SQLite implementation (HospitalRepository).

The service layer depends only on IHospitalRepository, keeping it
decoupled from the storage technology.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.database.connection import DatabaseConnection
from app.models.hospital import Hospital


# ---------------------------------------------------------------------------
# Abstract Interface (the contract)
# ---------------------------------------------------------------------------

class IHospitalRepository(ABC):
    """Contract that every hospital data-access implementation must satisfy."""

    @abstractmethod
    def add(self, hospital: Hospital) -> Hospital:
        """Persist a new hospital and return it with its generated id."""

    @abstractmethod
    def update(self, hospital: Hospital) -> Hospital:
        """Update an existing hospital record."""

    @abstractmethod
    def find_by_id(self, hospital_id: int) -> Optional[Hospital]:
        """Return the hospital with the given primary key, or None."""

    @abstractmethod
    def find_by_registration_number(self, reg_no: str) -> Optional[Hospital]:
        """Return the hospital matching the registration number, or None."""

    @abstractmethod
    def find_all(self, active_only: bool = True) -> List[Hospital]:
        """Return all (optionally only active) hospitals."""

    @abstractmethod
    def exists_registration_number(self, reg_no: str, exclude_id: Optional[int] = None) -> bool:
        """Check uniqueness of a registration number."""

    @abstractmethod
    def exists_license_number(self, license_no: str, exclude_id: Optional[int] = None) -> bool:
        """Check uniqueness of a license number."""

    @abstractmethod
    def search(
        self,
        name: Optional[str] = None,
        hospital_id: Optional[int] = None,
        city: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Hospital]:
        """Return hospitals matching any combination of name / id / city filters."""


# ---------------------------------------------------------------------------
# SQLite Implementation
# ---------------------------------------------------------------------------

_INSERT_SQL = """
INSERT INTO hospitals (
    hospital_name, registration_number, hospital_type, specialization_type,
    address_line1, address_line2, city, state, pin_code, country,
    phone_primary, phone_alternate, emergency_contact, email, website,
    total_beds, icu_beds, operation_theaters,
    administrator_name, license_number, accreditation, established_year,
    gstin, is_active
) VALUES (
    :hospital_name, :registration_number, :hospital_type, :specialization_type,
    :address_line1, :address_line2, :city, :state, :pin_code, :country,
    :phone_primary, :phone_alternate, :emergency_contact, :email, :website,
    :total_beds, :icu_beds, :operation_theaters,
    :administrator_name, :license_number, :accreditation, :established_year,
    :gstin, :is_active
)
"""

_UPDATE_SQL = """
UPDATE hospitals SET
    hospital_name       = :hospital_name,
    registration_number = :registration_number,
    hospital_type       = :hospital_type,
    specialization_type = :specialization_type,
    address_line1       = :address_line1,
    address_line2       = :address_line2,
    city                = :city,
    state               = :state,
    pin_code            = :pin_code,
    country             = :country,
    phone_primary       = :phone_primary,
    phone_alternate     = :phone_alternate,
    emergency_contact   = :emergency_contact,
    email               = :email,
    website             = :website,
    total_beds          = :total_beds,
    icu_beds            = :icu_beds,
    operation_theaters  = :operation_theaters,
    administrator_name  = :administrator_name,
    license_number      = :license_number,
    accreditation       = :accreditation,
    established_year    = :established_year,
    gstin               = :gstin,
    is_active           = :is_active
WHERE id = :id
"""

_SELECT_COLS = """
    id, hospital_name, registration_number, hospital_type, specialization_type,
    address_line1, address_line2, city, state, pin_code, country,
    phone_primary, phone_alternate, emergency_contact, email, website,
    total_beds, icu_beds, operation_theaters,
    administrator_name, license_number, accreditation, established_year,
    gstin, is_active, created_at, updated_at
"""


def _hospital_to_params(h: Hospital) -> dict:
    return {
        "id": h.id,
        "hospital_name": h.hospital_name,
        "registration_number": h.registration_number,
        "hospital_type": h.hospital_type,
        "specialization_type": h.specialization_type,
        "address_line1": h.address_line1,
        "address_line2": h.address_line2,
        "city": h.city,
        "state": h.state,
        "pin_code": h.pin_code,
        "country": h.country,
        "phone_primary": h.phone_primary,
        "phone_alternate": h.phone_alternate,
        "emergency_contact": h.emergency_contact,
        "email": h.email,
        "website": h.website,
        "total_beds": h.total_beds,
        "icu_beds": h.icu_beds,
        "operation_theaters": h.operation_theaters,
        "administrator_name": h.administrator_name,
        "license_number": h.license_number,
        "accreditation": h.accreditation,
        "established_year": h.established_year,
        "gstin": h.gstin,
        "is_active": 1 if h.is_active else 0,
    }


class HospitalRepository(IHospitalRepository):
    """SQLite-backed implementation of IHospitalRepository."""

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, hospital: Hospital) -> Hospital:
        conn = self._db.get_connection()
        params = _hospital_to_params(hospital)
        cursor = conn.execute(_INSERT_SQL, params)
        conn.commit()
        hospital.id = cursor.lastrowid
        return hospital

    def update(self, hospital: Hospital) -> Hospital:
        if hospital.id is None:
            raise ValueError("Cannot update a Hospital without an id.")
        conn = self._db.get_connection()
        conn.execute(_UPDATE_SQL, _hospital_to_params(hospital))
        conn.commit()
        return hospital

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def find_by_id(self, hospital_id: int) -> Optional[Hospital]:
        cursor = self._db.execute(
            f"SELECT {_SELECT_COLS} FROM hospitals WHERE id = ?",
            (hospital_id,),
        )
        row = cursor.fetchone()
        return Hospital.from_row(row) if row else None

    def find_by_registration_number(self, reg_no: str) -> Optional[Hospital]:
        cursor = self._db.execute(
            f"SELECT {_SELECT_COLS} FROM hospitals WHERE registration_number = ?",
            (reg_no,),
        )
        row = cursor.fetchone()
        return Hospital.from_row(row) if row else None

    def find_all(self, active_only: bool = True) -> List[Hospital]:
        sql = f"SELECT {_SELECT_COLS} FROM hospitals"
        params: tuple = ()
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY hospital_name"
        cursor = self._db.execute(sql, params)
        return [Hospital.from_row(row) for row in cursor.fetchall()]

    def search(
        self,
        name: Optional[str] = None,
        hospital_id: Optional[int] = None,
        city: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Hospital]:
        """Dynamic search using any combination of name / id / city filters."""
        conditions: list[str] = []
        params: list = []

        if active_only:
            conditions.append("is_active = 1")

        if hospital_id is not None:
            conditions.append("id = ?")
            params.append(hospital_id)

        if name:
            conditions.append("hospital_name LIKE ?")
            params.append(f"%{name}%")

        if city:
            conditions.append("city LIKE ?")
            params.append(f"%{city}%")

        sql = f"SELECT {_SELECT_COLS} FROM hospitals"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY hospital_name"

        cursor = self._db.execute(sql, tuple(params))
        return [Hospital.from_row(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Existence checks
    # ------------------------------------------------------------------

    def exists_registration_number(self, reg_no: str, exclude_id: Optional[int] = None) -> bool:
        if exclude_id is not None:
            cursor = self._db.execute(
                "SELECT 1 FROM hospitals WHERE registration_number = ? AND id != ?",
                (reg_no, exclude_id),
            )
        else:
            cursor = self._db.execute(
                "SELECT 1 FROM hospitals WHERE registration_number = ?",
                (reg_no,),
            )
        return cursor.fetchone() is not None

    def exists_license_number(self, license_no: str, exclude_id: Optional[int] = None) -> bool:
        if exclude_id is not None:
            cursor = self._db.execute(
                "SELECT 1 FROM hospitals WHERE license_number = ? AND id != ?",
                (license_no, exclude_id),
            )
        else:
            cursor = self._db.execute(
                "SELECT 1 FROM hospitals WHERE license_number = ?",
                (license_no,),
            )
        return cursor.fetchone() is not None
