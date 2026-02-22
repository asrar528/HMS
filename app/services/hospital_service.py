"""
Hospital Service – Business Logic Layer.

Defines the IHospitalService interface and its concrete implementation.
All validations, business rules, and orchestration live here.
The service depends on IHospitalRepository (injected), not on any
concrete database class – maintaining full loose coupling.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from app.models.hospital import Hospital
from app.repositories.hospital_repository import IHospitalRepository


# ---------------------------------------------------------------------------
# Value object for validation/operation results
# ---------------------------------------------------------------------------

@dataclass
class ServiceResult:
    """Carries the outcome of a service operation."""
    success: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def ok(cls, message: str = "Success", data: object = None) -> "ServiceResult":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str) -> "ServiceResult":
        return cls(success=False, message=message, data=None)


# ---------------------------------------------------------------------------
# Abstract Interface
# ---------------------------------------------------------------------------

class IHospitalService(ABC):

    @abstractmethod
    def register_hospital(self, hospital: Hospital) -> ServiceResult:
        """Validate and persist a new hospital registration."""

    @abstractmethod
    def get_hospital(self, hospital_id: int) -> Optional[Hospital]:
        """Retrieve a hospital by primary key."""

    @abstractmethod
    def get_all_hospitals(self) -> List[Hospital]:
        """Return all active hospitals."""

    @abstractmethod
    def is_first_run(self) -> bool:
        """Return True when no hospitals have been registered yet."""


# ---------------------------------------------------------------------------
# Concrete Implementation
# ---------------------------------------------------------------------------

class HospitalService(IHospitalService):
    """Business-logic orchestrator for hospital operations."""

    # Email regex – reasonably permissive
    _EMAIL_RE = re.compile(r"^[\w.%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$")
    # Phone: 7-15 digits, optionally starting with +
    _PHONE_RE = re.compile(r"^\+?\d{7,15}$")
    # PIN code: 6 digits (India) or 5–10 alphanumeric
    _PIN_RE = re.compile(r"^[A-Z0-9\s\-]{4,10}$", re.IGNORECASE)

    def __init__(self, repository: IHospitalRepository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # Public Service Methods
    # ------------------------------------------------------------------

    def register_hospital(self, hospital: Hospital) -> ServiceResult:
        """
        Validate all mandatory fields, check uniqueness constraints,
        then delegate persistence to the repository.
        """
        validation = self._validate(hospital)
        if not validation.success:
            return validation

        try:
            saved = self._repo.add(hospital)
            return ServiceResult.ok(
                f"Hospital '{saved.hospital_name}' registered successfully "
                f"(ID: {saved.id}).",
                data=saved,
            )
        except Exception as exc:
            return ServiceResult.fail(f"Database error: {exc}")

    def get_hospital(self, hospital_id: int) -> Optional[Hospital]:
        return self._repo.find_by_id(hospital_id)

    def get_all_hospitals(self) -> List[Hospital]:
        return self._repo.find_all(active_only=True)

    def is_first_run(self) -> bool:
        return len(self._repo.find_all(active_only=False)) == 0

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self, h: Hospital) -> ServiceResult:
        """Run all business validation rules; return first failure found."""

        # --- Mandatory text fields ---
        mandatory: list[tuple[str, str]] = [
            (h.hospital_name.strip(),        "Hospital Name"),
            (h.registration_number.strip(),  "Registration Number"),
            (h.hospital_type.strip(),        "Hospital Type"),
            (h.specialization_type.strip(),  "Specialization Type"),
            (h.address_line1.strip(),        "Address Line 1"),
            (h.city.strip(),                 "City"),
            (h.state.strip(),                "State"),
            (h.pin_code.strip(),             "PIN Code"),
            (h.country.strip(),              "Country"),
            (h.phone_primary.strip(),        "Primary Phone"),
            (h.emergency_contact.strip(),    "Emergency Contact"),
            (h.email.strip(),                "Email"),
            (h.administrator_name.strip(),   "Administrator Name"),
            (h.license_number.strip(),       "License Number"),
        ]
        for value, label in mandatory:
            if not value:
                return ServiceResult.fail(f"{label} is required.")

        # --- Numeric/range validations ---
        if h.total_beds <= 0:
            return ServiceResult.fail("Total Beds must be greater than 0.")
        if h.icu_beds < 0:
            return ServiceResult.fail("ICU Beds cannot be negative.")
        if h.icu_beds > h.total_beds:
            return ServiceResult.fail("ICU Beds cannot exceed Total Beds.")
        if h.operation_theaters < 0:
            return ServiceResult.fail("Operation Theaters cannot be negative.")
        current_year = 2026
        if not (1800 <= h.established_year <= current_year):
            return ServiceResult.fail(
                f"Established Year must be between 1800 and {current_year}."
            )

        # --- Format validations ---
        if not self._EMAIL_RE.match(h.email.strip()):
            return ServiceResult.fail("Email address format is invalid.")
        if not self._PHONE_RE.match(h.phone_primary.strip()):
            return ServiceResult.fail("Primary Phone number format is invalid.")
        if not self._PHONE_RE.match(h.emergency_contact.strip()):
            return ServiceResult.fail("Emergency Contact format is invalid.")
        if not self._PIN_RE.match(h.pin_code.strip()):
            return ServiceResult.fail("PIN Code format is invalid.")

        # --- Uniqueness constraints ---
        if self._repo.exists_registration_number(h.registration_number.strip(), h.id):
            return ServiceResult.fail(
                f"Registration Number '{h.registration_number}' is already in use."
            )
        if self._repo.exists_license_number(h.license_number.strip(), h.id):
            return ServiceResult.fail(
                f"License Number '{h.license_number}' is already in use."
            )

        return ServiceResult.ok()
