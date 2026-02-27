"""
Web Routes – View Layer (replaces customtkinter views).

Maps HTTP requests to service calls and renders Jinja2 templates.
The blueprint depends only on IHospitalService (injected via the
module-level `container` singleton), preserving the same loose-coupling
contract used in the desktop app.

Route map
---------
GET  /                      → Home page: hospital search + register link
GET  /register              → Show hospital registration form
POST /register              → Validate + persist; redirect to / on success
GET  /dashboard/<id>        → Hospital landing page (stats + details)
"""

from __future__ import annotations

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
)

from app.container import container
from app.models.hospital import (
    Hospital,
    HOSPITAL_TYPES,
    SPECIALIZATION_TYPES,
    ACCREDITATION_OPTIONS,
    INDIA_STATES,
)
from app.services.hospital_service import IHospitalService

# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
web_bp = Blueprint("web", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _service() -> IHospitalService:
    """Resolve the hospital service from the DI container."""
    return container.resolve(IHospitalService.__name__)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@web_bp.route("/")
def index():
    """
    Home page – hospital search.

    Accepts optional GET query params:
      name        – partial match on hospital_name
      hospital_id – exact match on id
      city        – partial match on city

    If none supplied all active hospitals are listed.
    On very first run (no hospitals) redirect to registration.
    """
    svc = _service()
    if svc.is_first_run():
        return redirect(url_for("web.register"))

    # Read optional search params
    q_name = request.args.get("name", "").strip()
    q_city = request.args.get("city", "").strip()
    q_id_raw = request.args.get("hospital_id", "").strip()
    q_id: int | None = None
    id_error: str | None = None
    if q_id_raw:
        try:
            q_id = int(q_id_raw)
        except ValueError:
            id_error = "Hospital ID must be a number."

    # Determine whether user submitted the search form
    searching = bool(q_name or q_city or q_id_raw)

    hospitals = svc.search_hospitals(
        name=q_name or None,
        hospital_id=q_id,
        city=q_city or None,
    )

    return render_template(
        "home.html",
        hospitals=hospitals,
        q_name=q_name,
        q_city=q_city,
        q_id=q_id_raw,
        searching=searching,
        id_error=id_error,
    )


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    """Hospital registration form – GET renders, POST processes."""
    svc = _service()
    form_data: dict = {}
    error: str | None = None

    if request.method == "POST":
        fd = request.form
        form_data = fd.to_dict()

        # Build Hospital object from form
        try:
            hospital = Hospital(
                hospital_name=fd.get("hospital_name", "").strip(),
                registration_number=fd.get("registration_number", "").strip(),
                hospital_type=fd.get("hospital_type", "").strip(),
                specialization_type=fd.get("specialization_type", "").strip(),
                address_line1=fd.get("address_line1", "").strip(),
                address_line2=fd.get("address_line2", "").strip() or None,
                city=fd.get("city", "").strip(),
                state=fd.get("state", "").strip(),
                pin_code=fd.get("pin_code", "").strip(),
                country=fd.get("country", "India").strip(),
                phone_primary=fd.get("phone_primary", "").strip(),
                phone_alternate=fd.get("phone_alternate", "").strip() or None,
                emergency_contact=fd.get("emergency_contact", "").strip(),
                email=fd.get("email", "").strip(),
                website=fd.get("website", "").strip() or None,
                total_beds=int(fd.get("total_beds") or 0),
                icu_beds=int(fd.get("icu_beds") or 0),
                operation_theaters=int(fd.get("operation_theaters") or 0),
                administrator_name=fd.get("administrator_name", "").strip(),
                license_number=fd.get("license_number", "").strip(),
                accreditation=fd.get("accreditation", "None").strip(),
                established_year=int(fd.get("established_year") or 2000),
                gstin=fd.get("gstin", "").strip() or None,
            )
        except (ValueError, TypeError) as exc:
            error = f"Invalid input: {exc}"
            return render_template(
                "hospital_registration.html",
                hospital_types=HOSPITAL_TYPES,
                specialization_types=SPECIALIZATION_TYPES,
                accreditation_options=ACCREDITATION_OPTIONS,
                india_states=INDIA_STATES,
                form_data=form_data,
                error=error,
            )

        result = svc.register_hospital(hospital)
        if result.success:
            flash(result.message, "success")
            return redirect(url_for("web.index"))
        else:
            error = result.message

    return render_template(
        "hospital_registration.html",
        hospital_types=HOSPITAL_TYPES,
        specialization_types=SPECIALIZATION_TYPES,
        accreditation_options=ACCREDITATION_OPTIONS,
        india_states=INDIA_STATES,
        form_data=form_data,
        error=error,
    )


@web_bp.route("/dashboard/<int:hospital_id>")
def dashboard(hospital_id: int):
    """Hospital landing / dashboard page."""
    svc = _service()
    hospital = svc.get_hospital(hospital_id)
    if hospital is None:
        flash("Hospital not found.", "error")
        return redirect(url_for("web.index"))
    return render_template("hospital_landing.html", hospital=hospital)


@web_bp.route("/hospital/<int:hospital_id>/edit", methods=["GET", "POST"])
def edit_hospital(hospital_id: int):
    """Hospital edit form – GET pre-fills with existing data, POST validates and updates."""
    svc = _service()
    hospital = svc.get_hospital(hospital_id)
    if hospital is None:
        flash("Hospital not found.", "error")
        return redirect(url_for("web.index"))

    error: str | None = None
    form_data: dict = {}

    if request.method == "POST":
        fd = request.form
        form_data = fd.to_dict()
        try:
            updated = Hospital(
                id=hospital_id,
                hospital_name=fd.get("hospital_name", "").strip(),
                registration_number=fd.get("registration_number", "").strip(),
                hospital_type=fd.get("hospital_type", "").strip(),
                specialization_type=fd.get("specialization_type", "").strip(),
                address_line1=fd.get("address_line1", "").strip(),
                address_line2=fd.get("address_line2", "").strip() or None,
                city=fd.get("city", "").strip(),
                state=fd.get("state", "").strip(),
                pin_code=fd.get("pin_code", "").strip(),
                country=fd.get("country", "India").strip(),
                phone_primary=fd.get("phone_primary", "").strip(),
                phone_alternate=fd.get("phone_alternate", "").strip() or None,
                emergency_contact=fd.get("emergency_contact", "").strip(),
                email=fd.get("email", "").strip(),
                website=fd.get("website", "").strip() or None,
                total_beds=int(fd.get("total_beds") or 0),
                icu_beds=int(fd.get("icu_beds") or 0),
                operation_theaters=int(fd.get("operation_theaters") or 0),
                administrator_name=fd.get("administrator_name", "").strip(),
                license_number=fd.get("license_number", "").strip(),
                accreditation=fd.get("accreditation", "None").strip(),
                established_year=int(fd.get("established_year") or 2000),
                gstin=fd.get("gstin", "").strip() or None,
            )
        except (ValueError, TypeError) as exc:
            error = f"Invalid input: {exc}"
            return render_template(
                "hospital_edit.html",
                hospital=hospital,
                hospital_types=HOSPITAL_TYPES,
                specialization_types=SPECIALIZATION_TYPES,
                accreditation_options=ACCREDITATION_OPTIONS,
                india_states=INDIA_STATES,
                form_data=form_data,
                error=error,
            )

        result = svc.update_hospital(updated)
        if result.success:
            flash(result.message, "success")
            return redirect(url_for("web.dashboard", hospital_id=hospital_id))
        else:
            error = result.message

    return render_template(
        "hospital_edit.html",
        hospital=hospital,
        hospital_types=HOSPITAL_TYPES,
        specialization_types=SPECIALIZATION_TYPES,
        accreditation_options=ACCREDITATION_OPTIONS,
        india_states=INDIA_STATES,
        form_data=form_data,
        error=error,
    )
