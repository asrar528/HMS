"""
Hospital Landing Page.

Displayed after a successful hospital registration (or on subsequent
application starts when a hospital is already registered).

Layout:
┌──────────────────────────────────────────────────────────┐
│  Header bar  – hospital name, city, reg-no               │
├──────────────┬───────────────────────────────────────────┤
│  Left Sidebar│  Main content area                        │
│  Navigation  │  Welcome / quick-stats panel              │
│  ──────────  │                                           │
│  📋 OPD      │                                           │
│  🏥 IPD      │                                           │
│  ──────────  │                                           │
│  ℹ  About    │                                           │
└──────────────┴───────────────────────────────────────────┘

The window receives only a Hospital dataclass and a service reference so
it stays completely decoupled from the persistence layer.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from app.models.hospital import Hospital
from app.views.base_window import (
    BaseWindow,
    TopHeaderBar,
    FONT_TITLE,
    FONT_HEADER,
    FONT_LABEL,
    FONT_SMALL,
    FONT_BUTTON,
    COLOR_ACCENT,
    COLOR_HEADER_BG,
    COLOR_HEADER_FG,
    COLOR_SECTION_BG,
    COLOR_SUCCESS,
)


# ---------------------------------------------------------------------------
# Sidebar navigation item
# ---------------------------------------------------------------------------

class _NavButton(ctk.CTkButton):
    """Custom sidebar navigation button with active-state indication."""

    _NORMAL_FG   = "#1E3A5F"
    _ACTIVE_FG   = COLOR_ACCENT
    _NORMAL_TEXT = "#ECEFF1"
    _ACTIVE_TEXT = "#FFFFFF"

    def __init__(self, parent, text: str, icon: str, command: Callable) -> None:
        super().__init__(
            parent,
            text=f"  {icon}  {text}",
            command=command,
            font=("Segoe UI", 13, "bold"),
            fg_color=self._NORMAL_FG,
            hover_color=self._ACTIVE_FG,
            text_color=self._NORMAL_TEXT,
            anchor="w",
            height=48,
            corner_radius=0,
        )

    def set_active(self, active: bool) -> None:
        self.configure(
            fg_color=self._ACTIVE_FG if active else self._NORMAL_FG,
            text_color=self._ACTIVE_TEXT if active else self._NORMAL_TEXT,
        )


# ---------------------------------------------------------------------------
# Content panels
# ---------------------------------------------------------------------------

class _WelcomePanel(ctk.CTkFrame):
    """Dashboard / welcome panel shown by default."""

    def __init__(self, parent, hospital: Hospital) -> None:
        super().__init__(parent, fg_color="#F0F4F8", corner_radius=0)
        self._hospital = hospital
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # -- Page title --
        ctk.CTkLabel(
            self,
            text=f"Welcome to {self._hospital.hospital_name}",
            font=("Segoe UI", 20, "bold"),
            text_color=COLOR_ACCENT,
            anchor="w",
        ).grid(row=0, column=0, padx=30, pady=(28, 4), sticky="w")

        ctk.CTkLabel(
            self,
            text="Hospital Management System  —  Dashboard",
            font=FONT_LABEL,
            text_color="#546E7A",
            anchor="w",
        ).grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

        # -- Quick stats row --
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=30, pady=(0, 24), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        h = self._hospital
        stats = [
            ("🛏️", "Total Beds", str(h.total_beds), "#1565C0"),
            ("🏥", "ICU Beds",   str(h.icu_beds),   "#6A1B9A"),
            ("⚕️",  "OTs",        str(h.operation_theaters), "#00695C"),
            ("📋", "Type",       h.hospital_type,    "#BF360C"),
        ]
        for col, (icon, label, value, color) in enumerate(stats):
            self._stat_card(stats_frame, col, icon, label, value, color)

        # -- Hospital info card --
        info_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10,
        )
        info_card.grid(row=3, column=0, padx=30, pady=(0, 24), sticky="ew")
        info_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            info_card,
            text="  Hospital Details",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_SECTION_BG,
            text_color=COLOR_ACCENT,
            anchor="w",
            corner_radius=4,
            height=34,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 10))

        detail_rows = [
            ("Registration No.",       h.registration_number),
            ("License Number",         h.license_number),
            ("Specialization",         h.specialization_type),
            ("Accreditation",          h.accreditation),
            ("Established",            str(h.established_year)),
            ("Administrator",          h.administrator_name),
            ("Address",                f"{h.address_line1}, {h.city}, {h.state} – {h.pin_code}"),
            ("Primary Phone",          h.phone_primary),
            ("Emergency Contact",      h.emergency_contact),
            ("Email",                  h.email),
        ]
        for idx, (lbl, val) in enumerate(detail_rows):
            bg = "#F5F5F5" if idx % 2 == 0 else "white"
            row_frame = ctk.CTkFrame(info_card, fg_color=bg, corner_radius=0, height=32)
            row_frame.grid(row=idx + 1, column=0, columnspan=2, sticky="ew", padx=16, pady=0)
            row_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_frame, text=f"{lbl}:", font=("Segoe UI", 11, "bold"),
                         text_color="#37474F", anchor="w", width=180).grid(
                row=0, column=0, padx=(8, 4), pady=4, sticky="w")
            ctk.CTkLabel(row_frame, text=val, font=("Segoe UI", 11),
                         text_color="#546E7A", anchor="w").grid(
                row=0, column=1, padx=(0, 8), pady=4, sticky="w")

        ctk.CTkLabel(info_card, text="").grid(row=len(detail_rows) + 1, column=0, pady=6)

    @staticmethod
    def _stat_card(
        parent: ctk.CTkFrame,
        col: int,
        icon: str,
        label: str,
        value: str,
        color: str,
    ) -> None:
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=100)
        card.grid(row=0, column=col, padx=6, pady=4, sticky="ew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=icon, font=("Segoe UI", 22)).place(relx=0.12, rely=0.25)
        ctk.CTkLabel(card, text=value, font=("Segoe UI", 22, "bold"),
                     text_color=color).place(relx=0.42, rely=0.18)
        ctk.CTkLabel(card, text=label, font=("Segoe UI", 10),
                     text_color="#78909C").place(relx=0.42, rely=0.62)


class _OPDPanel(ctk.CTkFrame):
    """OPD (Out-Patient Department) placeholder panel."""

    def __init__(self, parent, hospital: Hospital) -> None:
        super().__init__(parent, fg_color="#F0F4F8", corner_radius=0)
        self._build(hospital)

    def _build(self, hospital: Hospital) -> None:
        ctk.CTkLabel(
            self,
            text="📋  Out-Patient Department (OPD)",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_ACCENT,
        ).pack(pady=(60, 16), padx=40, anchor="w")

        ctk.CTkLabel(
            self,
            text=(
                f"OPD module for  {hospital.hospital_name}  is coming in the next phase.\n\n"
                "This section will include:\n"
                "  •  Patient Registration & Lookup\n"
                "  •  Appointment Scheduling\n"
                "  •  Doctor Consultation Queue\n"
                "  •  Prescription & Diagnosis Entry\n"
                "  •  Billing & Receipts"
            ),
            font=("Segoe UI", 13),
            text_color="#455A64",
            justify="left",
        ).pack(pady=12, padx=60, anchor="w")

        _coming_soon_badge(self)


class _IPDPanel(ctk.CTkFrame):
    """IPD (In-Patient Department) placeholder panel."""

    def __init__(self, parent, hospital: Hospital) -> None:
        super().__init__(parent, fg_color="#F0F4F8", corner_radius=0)
        self._build(hospital)

    def _build(self, hospital: Hospital) -> None:
        ctk.CTkLabel(
            self,
            text="🏥  In-Patient Department (IPD)",
            font=("Segoe UI", 18, "bold"),
            text_color="#6A1B9A",
        ).pack(pady=(60, 16), padx=40, anchor="w")

        ctk.CTkLabel(
            self,
            text=(
                f"IPD module for  {hospital.hospital_name}  is coming in the next phase.\n\n"
                "This section will include:\n"
                "  •  Admission & Discharge Management\n"
                "  •  Bed / Ward Allocation\n"
                "  •  ICU & Operation Theater Scheduling\n"
                "  •  Nursing Notes & Care Plans\n"
                "  •  Discharge Summary & Billing"
            ),
            font=("Segoe UI", 13),
            text_color="#455A64",
            justify="left",
        ).pack(pady=12, padx=60, anchor="w")

        _coming_soon_badge(self, color="#6A1B9A")


def _coming_soon_badge(parent: ctk.CTkFrame, color: str = COLOR_ACCENT) -> None:
    ctk.CTkLabel(
        parent,
        text="  🚧  Coming Soon – Phase 2  ",
        font=("Segoe UI", 12, "bold"),
        fg_color=color,
        text_color="white",
        corner_radius=20,
        padx=20,
        pady=8,
    ).pack(pady=(24, 0), padx=60, anchor="w")


# ---------------------------------------------------------------------------
# Main Landing Page Window
# ---------------------------------------------------------------------------

class HospitalLandingPage(BaseWindow):
    """
    Main application window displayed after a hospital is registered.

    Provides a sidebar navigation and swappable content area.
    """

    def __init__(self, hospital: Hospital) -> None:
        super().__init__(
            title=f"HMS – {hospital.hospital_name}",
            width=1200,
            height=750,
        )
        self._hospital = hospital
        self._active_section: Optional[str] = None
        self._nav_buttons: dict[str, _NavButton] = {}
        self._build_ui()
        self._navigate("dashboard")

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # -- Header --
        header = ctk.CTkFrame(self, fg_color=COLOR_HEADER_BG, height=72, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text=f"🏥  {self._hospital.hospital_name}",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_HEADER_FG,
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkLabel(
            header,
            text=(
                f"Reg. No: {self._hospital.registration_number}   |   "
                f"{self._hospital.city}, {self._hospital.state}   |   "
                f"{self._hospital.hospital_type}"
            ),
            font=("Segoe UI", 10),
            text_color="#BBDEFB",
        ).grid(row=0, column=1, padx=16, sticky="w")

        ctk.CTkLabel(
            header,
            text=f"{self._hospital.specialization_type}",
            font=("Segoe UI", 10, "bold"),
            text_color="#E3F2FD",
        ).grid(row=0, column=2, padx=20, sticky="e")

        # -- Left Sidebar --
        sidebar = ctk.CTkFrame(self, fg_color="#1E3A5F", width=220, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(20, weight=1)  # push footer down

        ctk.CTkLabel(
            sidebar,
            text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color="#78909C",
        ).pack(pady=(20, 6), padx=16, anchor="w")

        nav_items = [
            ("Dashboard",  "🏠", "dashboard"),
            ("OPD",        "📋", "opd"),
            ("IPD",        "🏥", "ipd"),
        ]
        for label, icon, key in nav_items:
            btn = _NavButton(sidebar, label, icon, command=lambda k=key: self._navigate(k))
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        # Divider
        ctk.CTkFrame(sidebar, fg_color="#37474F", height=1, corner_radius=0).pack(
            fill="x", padx=12, pady=16
        )

        ctk.CTkLabel(
            sidebar,
            text="SYSTEM",
            font=("Segoe UI", 9, "bold"),
            text_color="#78909C",
        ).pack(pady=(0, 4), padx=16, anchor="w")

        _NavButton(sidebar, "Hospital Info", "ℹ️", command=lambda: self._navigate("info")).pack(fill="x")
        self._nav_buttons["info"] = sidebar.winfo_children()[-1]

        # Footer
        ctk.CTkLabel(
            sidebar,
            text="HMS v1.0  |  Phase 1",
            font=("Segoe UI", 9),
            text_color="#546E7A",
        ).pack(side="bottom", pady=14)

        # -- Content area --
        self._content_area = ctk.CTkFrame(self, fg_color="#F0F4F8", corner_radius=0)
        self._content_area.grid(row=1, column=1, sticky="nsew")
        self._content_area.grid_rowconfigure(0, weight=1)
        self._content_area.grid_columnconfigure(0, weight=1)

        self._current_panel: Optional[ctk.CTkFrame] = None

    # ==================================================================
    # Navigation
    # ==================================================================

    def _navigate(self, section: str) -> None:
        if self._active_section == section:
            return

        # Deactivate previous
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == section)

        # Destroy previous panel
        if self._current_panel:
            self._current_panel.destroy()

        # Build new panel
        panel_map = {
            "dashboard": lambda: _WelcomePanel(self._content_area, self._hospital),
            "opd":       lambda: _OPDPanel(self._content_area, self._hospital),
            "ipd":       lambda: _IPDPanel(self._content_area, self._hospital),
            "info":      lambda: _WelcomePanel(self._content_area, self._hospital),
        }
        builder = panel_map.get(section, panel_map["dashboard"])
        self._current_panel = builder()
        self._current_panel.grid(row=0, column=0, sticky="nsew")
        self._active_section = section
