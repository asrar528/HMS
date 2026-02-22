"""
HMS Application Bootstrap (main.py).

Entry point for the Hospital Management System desktop application.

Responsibilities:
1.  Configure the Dependency Injection container.
2.  Initialise the SQLite database (run schema migrations).
3.  Decide which window to show on startup:
    - If no hospital is registered yet → Hospital Registration Window.
    - If a hospital exists            → Hospital Landing Page.

Architecture layers (top → bottom):
  Views  →  Services  →  Repositories  →  Database
Each layer depends only on the abstraction of the layer below it,
never on a concrete implementation – enforced via the DI container.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so imports work on all OSes
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
import customtkinter as ctk

# ---------------------------------------------------------------------------
# Application modules
# ---------------------------------------------------------------------------
from app.container import container, DIContainer
from app.database.connection import DatabaseConnection
from app.database.schema import SchemaManager
from app.models.hospital import Hospital
from app.repositories.hospital_repository import HospitalRepository, IHospitalRepository
from app.services.hospital_service import HospitalService, IHospitalService
from app.views.base_window import apply_theme
from app.views.hospital_registration import HospitalRegistrationWindow
from app.views.hospital_landing import HospitalLandingPage


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH = PROJECT_ROOT / "data" / "hms.db"


# ---------------------------------------------------------------------------
# DI Container Bootstrap
# ---------------------------------------------------------------------------

def _bootstrap_container(ioc: DIContainer) -> None:
    """Wire all dependencies into the DI container."""

    # --- Infrastructure ---
    ioc.register_singleton(
        "DatabaseConnection",
        lambda: DatabaseConnection(DB_PATH),
    )

    # --- Repositories ---
    ioc.register_singleton(
        IHospitalRepository.__name__,
        lambda: HospitalRepository(ioc.resolve("DatabaseConnection")),
    )

    # --- Services ---
    ioc.register_singleton(
        IHospitalService.__name__,
        lambda: HospitalService(ioc.resolve(IHospitalRepository.__name__)),
    )


# ---------------------------------------------------------------------------
# Application Controller
# ---------------------------------------------------------------------------

class HMSApplication:
    """
    Top-level application controller.

    Owns the window lifecycle:
    - Shows the Registration window on first run.
    - Shows the Landing Page when a hospital is already registered.
    - Switches from Registration → Landing Page after successful save.
    """

    def __init__(self, ioc: DIContainer) -> None:
        self._ioc = ioc
        self._service: IHospitalService = ioc.resolve(IHospitalService.__name__)
        self._current_window: ctk.CTk | None = None

    def run(self) -> None:
        apply_theme()

        if self._service.is_first_run():
            self._show_registration()
        else:
            hospitals = self._service.get_all_hospitals()
            self._show_landing(hospitals[0])

        if self._current_window:
            self._current_window.mainloop()

    # ------------------------------------------------------------------
    # Window transitions
    # ------------------------------------------------------------------

    def _show_registration(self) -> None:
        """Display the Hospital Registration window."""
        win = HospitalRegistrationWindow(
            hospital_service=self._service,
            on_success=self._on_registration_success,
        )
        self._current_window = win
        win.mainloop()

    def _on_registration_success(self, hospital: Hospital) -> None:
        """Called by the Registration window after a successful save."""
        # Destroy the registration window
        if self._current_window:
            self._current_window.destroy()

        # Open the landing page in a fresh top-level loop
        self._show_landing(hospital)

    def _show_landing(self, hospital: Hospital) -> None:
        """Display the Hospital Landing Page."""
        win = HospitalLandingPage(hospital)
        self._current_window = win
        win.mainloop()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Bootstrap DI container
    _bootstrap_container(container)

    # 2. Run database migrations
    db: DatabaseConnection = container.resolve("DatabaseConnection")
    schema_manager = SchemaManager(db)
    schema_manager.migrate()

    # 3. Launch application
    app = HMSApplication(container)
    app.run()


if __name__ == "__main__":
    main()
