"""
HMS Application Bootstrap (main.py).

Entry point for the Hospital Management System web application.

Responsibilities:
1.  Configure the Dependency Injection container.
2.  Initialise the SQLite database (run schema migrations).
3.  Create and configure the Flask application.
4.  Register the web blueprint (routes layer).

Architecture layers (top → bottom):
  Web Routes  →  Services  →  Repositories  →  Database
Each layer depends only on the abstraction of the layer below it,
never on a concrete implementation – enforced via the DI container.
The DI container, models, repositories, and service layer are
identical to the original desktop application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so imports work on all OSes
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Load .env file when running locally (python-dotenv).
# In production (Railway / Render / PythonAnywhere) real env vars are used.
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # python-dotenv not installed – rely on real environment variables

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
from flask import Flask

# ---------------------------------------------------------------------------
# Application modules (unchanged from desktop version)
# ---------------------------------------------------------------------------
from app.container import container, DIContainer
from app.database.connection import DatabaseConnection
from app.database.schema import SchemaManager
from app.repositories.hospital_repository import HospitalRepository, IHospitalRepository
from app.services.hospital_service import HospitalService, IHospitalService

# ---------------------------------------------------------------------------
# Web layer (replaces customtkinter views)
# ---------------------------------------------------------------------------
from app.web.routes import web_bp


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# In production set DATA_DIR env var to a persistent disk path (e.g. /data).
# Locally it defaults to <project_root>/data/
DATA_DIR = Path(os.environ.get("DATA_DIR", str(PROJECT_ROOT / "data")))
DB_PATH  = DATA_DIR / "hms.db"


# ---------------------------------------------------------------------------
# DI Container Bootstrap  (identical wiring to the desktop version)
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
# Flask Application Factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    """
    Flask application factory.

    Called by gunicorn in production:  gunicorn "main:create_app()"
    Called directly in development:    python main.py

    Steps:
    1. Bootstrap DI container.
    2. Run database migrations.
    3. Register the web blueprint.
    """
    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="app/static",
    )

    # SECRET_KEY must be set via environment variable in production.
    # A missing key raises at startup so it is never silently insecure.
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        if os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError(
                "SECRET_KEY environment variable is not set. "
                "Set it before starting the server in production."
            )
        # Development fallback – never used in production
        secret = "hms-dev-only-secret-change-me"
    app.secret_key = secret

    # 1. Wire dependencies
    _bootstrap_container(container)

    # 2. Run migrations
    db: DatabaseConnection = container.resolve("DatabaseConnection")
    SchemaManager(db).migrate()

    # 3. Register blueprint (web routes replace customtkinter views)
    app.register_blueprint(web_bp)

    return app


# ---------------------------------------------------------------------------
# Entry Point  (development only – production uses gunicorn)
# ---------------------------------------------------------------------------

def main() -> None:
    app = create_app()
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    print("\n  HMS Web Application")
    print("  -------------------")
    print(f"  Open http://127.0.0.1:{port} in your browser\n")
    app.run(debug=debug, port=port, use_reloader=False)


if __name__ == "__main__":
    main()
