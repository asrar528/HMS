"""
Hospital Registration Window.

Presents a scrollable form with all mandatory fields required to register a
hospital.  On successful save it invokes the provided ``on_success`` callback
(typically the application bootstrapper) so the calling code can switch to
the Landing Page.

The window is intentionally decoupled from both the database and the service:
it receives an IHospitalService instance via constructor injection.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Callable, Optional

import customtkinter as ctk

from app.models.hospital import (
    Hospital,
    HOSPITAL_TYPES,
    SPECIALIZATION_TYPES,
    ACCREDITATION_OPTIONS,
    INDIA_STATES,
)
from app.services.hospital_service import IHospitalService
from app.views.base_window import (
    BaseWindow,
    TopHeaderBar,
    FONT_HEADER,
    FONT_LABEL,
    FONT_SMALL,
    FONT_BUTTON,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_SECTION_BG,
    COLOR_CARD_BG,
)


class HospitalRegistrationWindow(BaseWindow):
    """Full-screen hospital registration form."""

    def __init__(
        self,
        hospital_service: IHospitalService,
        on_success: Callable[[Hospital], None],
    ) -> None:
        super().__init__(
            title="HMS – Hospital Registration",
            width=1150,
            height=780,
        )
        self._service = hospital_service
        self._on_success = on_success

        self._build_ui()

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        header = TopHeaderBar(
            self,
            "Hospital Management System",
            "New Hospital Registration",
        )
        header.grid(row=0, column=0, sticky="ew")

        # ---- Scrollable body ----
        self._canvas = ctk.CTkScrollableFrame(
            self,
            fg_color="#F0F4F8",
            corner_radius=0,
        )
        self._canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._canvas.grid_columnconfigure(0, weight=1)

        # ---- Form card ----
        card = ctk.CTkFrame(
            self._canvas,
            fg_color="white",
            corner_radius=12,
        )
        card.grid(row=0, column=0, padx=40, pady=30, sticky="ew")
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._build_form(card)

        # ---- Status bar ----
        self._status_var = tk.StringVar(value="")
        status_bar = ctk.CTkLabel(
            self,
            textvariable=self._status_var,
            font=FONT_SMALL,
            height=26,
            fg_color="#E8EAF6",
            anchor="w",
            corner_radius=0,
        )
        status_bar.grid(row=2, column=0, sticky="ew")

    # ------------------------------------------------------------------

    def _build_form(self, parent: ctk.CTkFrame) -> None:
        row = 0

        # ---- Page title ----
        ctk.CTkLabel(
            parent,
            text="Hospital Registration Form",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_ACCENT,
        ).grid(row=row, column=0, columnspan=4, padx=20, pady=(20, 4), sticky="w")

        ctk.CTkLabel(
            parent,
            text="Fields marked with  *  are mandatory",
            font=FONT_SMALL,
            text_color="#757575",
        ).grid(row=row + 1, column=0, columnspan=4, padx=20, pady=(0, 16), sticky="w")
        row += 2

        # ==============================================================
        # SECTION 1 – Identity
        # ==============================================================
        row = self._section(parent, row, "1.  Hospital Identity")

        self._e_name = self._field(parent, row, 0, "Hospital Name", required=True)
        self._e_reg   = self._field(parent, row, 2, "Registration No.", required=True)
        row += 2

        self._cb_type = self._combo_field(parent, row, 0, "Hospital Type", HOSPITAL_TYPES, required=True)
        self._cb_spec = self._combo_field(parent, row, 2, "Specialization", SPECIALIZATION_TYPES, required=True)
        row += 2

        self._e_est_year = self._field(parent, row, 0, "Established Year", required=True, placeholder="e.g. 1995")
        self._cb_accr    = self._combo_field(parent, row, 2, "Accreditation", ACCREDITATION_OPTIONS)
        row += 2

        self._e_gstin = self._field(parent, row, 0, "GSTIN", placeholder="Optional")
        row += 2

        # ==============================================================
        # SECTION 2 – Address
        # ==============================================================
        row = self._section(parent, row, "2.  Address & Location")

        self._e_addr1 = self._field(parent, row, 0, "Address Line 1", required=True, span=3)
        row += 2
        self._e_addr2 = self._field(parent, row, 0, "Address Line 2", span=3, placeholder="Optional")
        row += 2

        self._e_city    = self._field(parent, row, 0, "City", required=True)
        self._cb_state  = self._combo_field(parent, row, 2, "State", INDIA_STATES, required=True)
        row += 2

        self._e_pin     = self._field(parent, row, 0, "PIN Code", required=True, placeholder="e.g. 400001")
        self._e_country = self._field(parent, row, 2, "Country", required=True)
        self._e_country.insert(0, "India")
        row += 2

        # ==============================================================
        # SECTION 3 – Contact
        # ==============================================================
        row = self._section(parent, row, "3.  Contact Information")

        self._e_phone1    = self._field(parent, row, 0, "Primary Phone", required=True, placeholder="+91XXXXXXXXXX")
        self._e_phone2    = self._field(parent, row, 2, "Alternate Phone", placeholder="Optional")
        row += 2

        self._e_emergency = self._field(parent, row, 0, "Emergency Contact", required=True, placeholder="+91XXXXXXXXXX")
        self._e_email     = self._field(parent, row, 2, "Email Address", required=True, placeholder="admin@hospital.com")
        row += 2

        self._e_website = self._field(parent, row, 0, "Website", placeholder="https://www.hospital.com (Optional)")
        row += 2

        # ==============================================================
        # SECTION 4 – Capacity
        # ==============================================================
        row = self._section(parent, row, "4.  Capacity & Infrastructure")

        self._e_beds     = self._field(parent, row, 0, "Total Beds", required=True, placeholder="e.g. 200")
        self._e_icu      = self._field(parent, row, 2, "ICU Beds", placeholder="e.g. 20")
        row += 2

        self._e_ot = self._field(parent, row, 0, "Operation Theaters", placeholder="e.g. 5")
        row += 2

        # ==============================================================
        # SECTION 5 – Administration & Licensing
        # ==============================================================
        row = self._section(parent, row, "5.  Administration & Licensing")

        self._e_admin   = self._field(parent, row, 0, "Administrator / CEO Name", required=True)
        self._e_license = self._field(parent, row, 2, "License Number", required=True)
        row += 2

        # ==============================================================
        # Action Buttons
        # ==============================================================
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=4, pady=28, padx=20, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="Clear Form",
            command=self._clear_form,
            font=FONT_BUTTON,
            fg_color="#616161",
            hover_color="#424242",
            width=130,
            height=42,
            corner_radius=8,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_frame,
            text="Register Hospital",
            command=self._submit,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#1B5E20",
            width=180,
            height=42,
            corner_radius=8,
        ).pack(side="left")

    # ==================================================================
    # Helper builders
    # ==================================================================

    def _section(self, parent: ctk.CTkFrame, row: int, title: str) -> int:
        ctk.CTkLabel(
            parent,
            text=f"  {title}",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_SECTION_BG,
            text_color=COLOR_ACCENT,
            anchor="w",
            corner_radius=4,
            height=34,
        ).grid(row=row, column=0, columnspan=4, sticky="ew", padx=16, pady=(14, 6))
        return row + 1

    def _field(
        self,
        parent: ctk.CTkFrame,
        row: int,
        col: int,
        label: str,
        required: bool = False,
        span: int = 1,
        placeholder: str = "",
    ) -> ctk.CTkEntry:
        col_span = span * 2  # each logical column takes 2 grid columns
        lbl_text = f"{label} *" if required else label
        ctk.CTkLabel(parent, text=lbl_text, font=FONT_LABEL, anchor="w").grid(
            row=row, column=col, columnspan=col_span, padx=(16, 4), pady=(2, 0), sticky="w"
        )
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=("Segoe UI", 12),
            height=36,
            corner_radius=6,
        )
        entry.grid(
            row=row + 1,
            column=col,
            columnspan=col_span,
            padx=(16, 16),
            pady=(0, 8),
            sticky="ew",
        )
        return entry

    def _combo_field(
        self,
        parent: ctk.CTkFrame,
        row: int,
        col: int,
        label: str,
        values: list,
        required: bool = False,
    ) -> ctk.CTkComboBox:
        lbl_text = f"{label} *" if required else label
        ctk.CTkLabel(parent, text=lbl_text, font=FONT_LABEL, anchor="w").grid(
            row=row, column=col, columnspan=2, padx=(16, 4), pady=(2, 0), sticky="w"
        )
        combo = ctk.CTkComboBox(
            parent,
            values=values,
            font=("Segoe UI", 12),
            height=36,
            corner_radius=6,
            state="readonly",
        )
        combo.set(values[0])
        combo.grid(
            row=row + 1,
            column=col,
            columnspan=2,
            padx=(16, 16),
            pady=(0, 8),
            sticky="ew",
        )
        return combo

    # ==================================================================
    # Form actions
    # ==================================================================

    def _collect(self) -> Optional[Hospital]:
        """Read all fields and return a Hospital dataclass (not validated yet)."""
        try:
            total_beds = int(self._e_beds.get().strip() or 0)
            icu_beds   = int(self._e_icu.get().strip() or 0)
            ot_count   = int(self._e_ot.get().strip() or 0)
            est_year   = int(self._e_est_year.get().strip() or 0)
        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Total Beds, ICU Beds, Operation Theaters, and Established Year must be numeric.",
                parent=self,
            )
            return None

        return Hospital(
            hospital_name       = self._e_name.get().strip(),
            registration_number = self._e_reg.get().strip(),
            hospital_type       = self._cb_type.get(),
            specialization_type = self._cb_spec.get(),
            address_line1       = self._e_addr1.get().strip(),
            address_line2       = self._e_addr2.get().strip() or None,
            city                = self._e_city.get().strip(),
            state               = self._cb_state.get(),
            pin_code            = self._e_pin.get().strip(),
            country             = self._e_country.get().strip(),
            phone_primary       = self._e_phone1.get().strip(),
            phone_alternate     = self._e_phone2.get().strip() or None,
            emergency_contact   = self._e_emergency.get().strip(),
            email               = self._e_email.get().strip(),
            website             = self._e_website.get().strip() or None,
            total_beds          = total_beds,
            icu_beds            = icu_beds,
            operation_theaters  = ot_count,
            administrator_name  = self._e_admin.get().strip(),
            license_number      = self._e_license.get().strip(),
            accreditation       = self._cb_accr.get(),
            established_year    = est_year,
            gstin               = self._e_gstin.get().strip() or None,
        )

    def _submit(self) -> None:
        hospital = self._collect()
        if hospital is None:
            return

        self._status_var.set("Saving registration…")
        self.update_idletasks()

        result = self._service.register_hospital(hospital)

        if result.success:
            self._status_var.set(f"✔  {result.message}")
            messagebox.showinfo("Registration Successful", result.message, parent=self)
            self._on_success(result.data)          # switch to landing page
        else:
            self._status_var.set(f"✘  {result.message}")
            messagebox.showerror("Validation Error", result.message, parent=self)

    def _clear_form(self) -> None:
        for widget in [
            self._e_name, self._e_reg, self._e_est_year, self._e_gstin,
            self._e_addr1, self._e_addr2, self._e_city, self._e_pin,
            self._e_phone1, self._e_phone2, self._e_emergency, self._e_email,
            self._e_website, self._e_beds, self._e_icu, self._e_ot,
            self._e_admin, self._e_license,
        ]:
            widget.delete(0, "end")

        self._e_country.insert(0, "India")
        self._cb_type.set(HOSPITAL_TYPES[0])
        self._cb_spec.set(SPECIALIZATION_TYPES[0])
        self._cb_accr.set(ACCREDITATION_OPTIONS[0])
        self._cb_state.set(INDIA_STATES[0])
        self._status_var.set("")
