"""
Hospital Domain Model.

A plain dataclass representing a Hospital entity.  No UI or database
logic is placed here – this is pure data definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Hospital:
    """Represents a registered hospital in the HMS system."""

    # ---------------------------------------------------------------------
    # Identity
    # ---------------------------------------------------------------------
    hospital_name: str
    registration_number: str
    hospital_type: str                  # Government / Private / Semi-Government / Trust / Charitable
    specialization_type: str            # Multi-Specialty / Super-Specialty / General / Single-Specialty

    # ---------------------------------------------------------------------
    # Location
    # ---------------------------------------------------------------------
    address_line1: str
    city: str
    state: str
    pin_code: str
    country: str = "India"
    address_line2: Optional[str] = None

    # ---------------------------------------------------------------------
    # Contact
    # ---------------------------------------------------------------------
    phone_primary: str = ""
    phone_alternate: Optional[str] = None
    emergency_contact: str = ""
    email: str = ""
    website: Optional[str] = None

    # ---------------------------------------------------------------------
    # Capacity
    # ---------------------------------------------------------------------
    total_beds: int = 0
    icu_beds: int = 0
    operation_theaters: int = 0

    # ---------------------------------------------------------------------
    # Administration
    # ---------------------------------------------------------------------
    administrator_name: str = ""
    license_number: str = ""
    accreditation: str = "None"         # NABH / JCI / ISO / None
    established_year: int = 2000
    gstin: Optional[str] = None

    # ---------------------------------------------------------------------
    # Metadata (managed by DB / service layer)
    # ---------------------------------------------------------------------
    id: Optional[int] = field(default=None, compare=False)
    is_active: bool = True
    created_at: Optional[str] = field(default=None, compare=False)
    updated_at: Optional[str] = field(default=None, compare=False)

    # ------------------------------------------------------------------
    # Factory – build from a sqlite3.Row
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row) -> "Hospital":
        """Construct a Hospital from a sqlite3.Row or dict-like object."""
        return cls(
            id=row["id"],
            hospital_name=row["hospital_name"],
            registration_number=row["registration_number"],
            hospital_type=row["hospital_type"],
            specialization_type=row["specialization_type"],
            address_line1=row["address_line1"],
            address_line2=row["address_line2"],
            city=row["city"],
            state=row["state"],
            pin_code=row["pin_code"],
            country=row["country"],
            phone_primary=row["phone_primary"],
            phone_alternate=row["phone_alternate"],
            emergency_contact=row["emergency_contact"],
            email=row["email"],
            website=row["website"],
            total_beds=row["total_beds"],
            icu_beds=row["icu_beds"],
            operation_theaters=row["operation_theaters"],
            administrator_name=row["administrator_name"],
            license_number=row["license_number"],
            accreditation=row["accreditation"],
            established_year=row["established_year"],
            gstin=row["gstin"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ---------------------------------------------------------------------------
# Enumerations used as drop-down values in the UI
# ---------------------------------------------------------------------------

HOSPITAL_TYPES = [
    "Government",
    "Private",
    "Semi-Government",
    "Trust",
    "Charitable",
]

SPECIALIZATION_TYPES = [
    "Multi-Specialty",
    "Super-Specialty",
    "General",
    "Single-Specialty",
]

ACCREDITATION_OPTIONS = ["None", "NABH", "JCI", "ISO 9001", "NABH + ISO"]

INDIA_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli",
    "Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh",
    "Lakshadweep", "Puducherry",
]
