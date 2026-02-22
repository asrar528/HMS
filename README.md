# 🏥 Hospital Management System (HMS)
## Phase 1 – Hospital Registration & Landing Page

---

### Tech Stack
| Layer | Technology |
|---|---|
| UI Framework | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 5.x |
| Language | Python 3.11+ |
| Database | SQLite 3 (built-in `sqlite3`) |
| Architecture | Layered + Repository + DI Container |

---

### Project Structure
```
E:\HMS\
├── main.py                          ← Entry point; wires DI & launches app
├── requirements.txt
└── app/
    ├── container.py                 ← Lightweight DI IoC container
    ├── database/
    │   ├── connection.py            ← SQLite connection manager
    │   └── schema.py                ← Versioned DDL migrations
    ├── models/
    │   └── hospital.py              ← Hospital dataclass + domain enums
    ├── repositories/
    │   └── hospital_repository.py   ← IHospitalRepository + SQLite impl
    ├── services/
    │   └── hospital_service.py      ← IHospitalService + validation rules
    └── views/
        ├── base_window.py           ← Shared theme helpers & base class
        ├── hospital_registration.py ← Registration form window
        └── hospital_landing.py      ← Dashboard with OPD / IPD navigation
```

---

### Setup & Run

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

---

### Application Flow

```
First Launch
    └─► Hospital Registration Window
            ↓ (fill all mandatory fields and click "Register Hospital")
            └─► Hospital Landing Page

Subsequent Launches (hospital already saved)
    └─► Hospital Landing Page directly
```

---

### Hospital Registration – Mandatory Fields

| Section | Fields |
|---|---|
| Identity | Hospital Name, Registration No., Hospital Type, Specialization Type, Established Year |
| Address | Address Line 1, City, State, PIN Code, Country |
| Contact | Primary Phone, Emergency Contact, Email |
| Capacity | Total Beds |
| Administration | Administrator Name, License Number |

---

### Database Schema (Phase 1)

**`hospitals`** table – 27 columns covering identity, address, contact,
capacity, administration, accreditation, and audit timestamps.

**`schema_version`** table – tracks applied migrations.

---

### Architecture Highlights

- **Dependency Injection**: `app/container.py` – custom `DIContainer` supports
  singleton, factory, and pre-built instance registrations.
- **Repository Pattern**: `IHospitalRepository` abstract interface; only the
  service layer knows this interface, not the concrete `HospitalRepository`.
- **Service Layer**: `IHospitalService` contains all validation and business
  rules; views never talk to the database directly.
- **Loose Coupling**: Each layer depends on the abstraction of the layer below,
  making components independently testable and swappable.

---

### Phase 2 (Planned)
- OPD: Patient registration, appointments, prescriptions, billing
- IPD: Admissions, bed/ward allocation, discharge management
- User authentication & role-based access
- Reporting & analytics dashboard
