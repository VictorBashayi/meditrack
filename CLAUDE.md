# MediTrack — Shared AI Coding Contract

> **Read this before writing any code.**
> This file is the single source of truth for the entire team.
> Every AI assistant and every developer must follow the contracts here.
> Do not rename, move, or restructure anything defined in this file without a team-wide PR discussion.

---

## Project Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| UI Framework | Streamlit |
| AI API | Google Gemini (`gemini-1.5-flash`) |
| Public APIs | disease.sh, OpenFDA (`api.fda.gov/drug/`) |
| Data Storage | JSON (patients), CSV (appointments), TXT (logs) |
| Version Control | Git + GitHub (feature branches → PR → main) |

---

## Directory Structure (Do Not Reorganize)

```
meditrack/
├── main.py
├── pages/
│   ├── 1_registration.py
│   ├── 2_appointments.py
│   ├── 3_patient_lookup.py
│   ├── 4_ai_assistant.py
│   └── 5_reports.py
├── models/
│   ├── person.py
│   ├── patient.py
│   ├── staff.py
│   └── appointment.py
├── managers/
│   ├── patient_registry.py
│   ├── appointment_manager.py
│   └── file_handler.py
├── services/
│   ├── ai_assistant.py
│   └── api_client.py
├── exceptions/
│   └── custom_exceptions.py
├── data/
│   ├── patients.json
│   └── appointments.csv
├── logs/
├── CLAUDE.md
├── .gitignore
└── README.md
```

---

## Module Ownership

Each member owns exactly one module. You write code **only inside your assigned files**.
If your feature needs something from another module, call its public interface — do not rewrite or copy it.

| Member | Branch | Owns These Files | Must Not Touch |
|--------|--------|-----------------|----------------|
| Victor James | `feature/patient-registration` | `models/person.py`, `models/patient.py`, `models/staff.py`, `pages/1_registration.py` | Everything else |
| Alwali Kazir | `feature/appointment-scheduling` | `models/appointment.py`, `managers/appointment_manager.py`, `pages/2_appointments.py` | `models/patient.py`, FileHandler |
| Usman Yahya | `feature/file-handling` | `managers/file_handler.py` | All model classes, all pages |
| Mary Tabai | `feature/ai-assistant` | `services/ai_assistant.py`, `pages/4_ai_assistant.py` | Patient/Appointment models directly |
| Mohammed Usman | `feature/api-integration` | `services/api_client.py`, `pages/3_patient_lookup.py` | FileHandler, AI service |
| Ireoluwade Oyerinde | `feature/exception-handling` | `exceptions/custom_exceptions.py` | No logic files — only define exceptions here |
| Abdulmujeeb Alatise | `feature/ui-layout` | `main.py`, shared layout utilities inside `pages/` (sidebar, navigation only) | Page content logic |
| Ephraim Effiong | `feature/reporting` | `pages/5_reports.py` | FileHandler internals — call its methods, don't rewrite |

---

## Shared Class Contracts

These are the **exact signatures** everyone must use. Do not change method names, parameters, or return types.
If you are building a class, implement exactly this interface. If you are consuming a class, call exactly these methods.

### `Person` (base) — `models/person.py`

```python
class Person:
    def __init__(self, name: str, age: int, phone: str, email: str):
        self.name = name
        self.age = age
        self.phone = phone
        self.email = email

    def to_dict(self) -> dict: ...
```

### `Patient(Person)` — `models/patient.py`

```python
class Patient(Person):
    def __init__(self, patient_id: str, name: str, age: int, phone: str,
                 email: str, blood_group: str, allergies: list[str],
                 medical_history: list[str]):
        ...
        self.patient_id = patient_id   # format: PAT-XXXXXX

    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict) -> "Patient": ...
```

### `Staff(Person)` — `models/staff.py`

```python
class Staff(Person):
    def __init__(self, staff_id: str, name: str, age: int, phone: str,
                 email: str, role: str, department: str, shift: str):
        ...
        self.staff_id = staff_id

    def to_dict(self) -> dict: ...
```

### `Appointment` — `models/appointment.py`

```python
class Appointment:
    def __init__(self, appointment_id: str, patient_id: str, doctor_id: str,
                 date_time: datetime, status: str, notes: str = ""):
        ...
        # status values: "scheduled" | "completed" | "cancelled"

    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict) -> "Appointment": ...
```

### `PatientRegistry` — `managers/patient_registry.py`

```python
class PatientRegistry:
    def register(self, patient: Patient) -> None: ...
    def get_patient(self, patient_id: str) -> Patient: ...
        # raises PatientNotFoundError if not found
    def update_patient(self, patient_id: str, updates: dict) -> None: ...
    def list_all(self) -> list[Patient]: ...
```

### `AppointmentManager` — `managers/appointment_manager.py`

```python
class AppointmentManager:
    def schedule(self, appointment: Appointment) -> None: ...
        # raises AppointmentConflictError if slot taken
    def cancel(self, appointment_id: str) -> None: ...
    def reschedule(self, appointment_id: str, new_datetime: datetime) -> None: ...
    def get_by_patient(self, patient_id: str) -> list[Appointment]: ...
    def list_all(self) -> list[Appointment]: ...
```

### `FileHandler` — `managers/file_handler.py`

```python
class FileHandler:
    def save_patients(self, patients: list[dict]) -> None: ...
    def load_patients(self) -> list[dict]: ...
    def save_appointments(self, appointments: list[dict]) -> None: ...
    def load_appointments(self) -> list[dict]: ...
    def write_log(self, message: str) -> None: ...
    def export_patient_report(self, patient_id: str) -> str: ...
        # returns the file path of the exported TXT file
```

### `AIAssistant` — `services/ai_assistant.py`

```python
class AIAssistant:
    def generate_summary(self, patient: Patient) -> str: ...
        # returns plain-English clinical summary from Gemini
    def triage_suggestion(self, symptoms: list[str]) -> str: ...
        # returns triage recommendation string
```

### `APIClient` — `services/api_client.py`

```python
class APIClient:
    def get_disease_stats(self, disease: str) -> dict: ...
        # calls disease.sh, returns stats dict
    def get_drug_info(self, drug_name: str) -> dict: ...
        # calls OpenFDA, returns label/adverse event info
```

---

## Custom Exceptions — `exceptions/custom_exceptions.py`

**Ireoluwade Oyerinde defines these. Everyone else imports from here. Do not define exceptions anywhere else.**

```python
class MediTrackError(Exception):
    """Base exception for all MediTrack errors."""

class PatientNotFoundError(MediTrackError):
    """Raised when a patient_id lookup returns no result."""

class AppointmentConflictError(MediTrackError):
    """Raised when a doctor already has an appointment at the requested time slot."""

class FileOperationError(MediTrackError):
    """Raised when a read/write/export operation fails."""

class APIError(MediTrackError):
    """Raised when an external API call fails or returns a bad response."""

class ValidationError(MediTrackError):
    """Raised when regex or input validation fails."""
```

Import pattern everyone must use:
```python
from exceptions.custom_exceptions import PatientNotFoundError, AppointmentConflictError
```

---

## Data Formats

### `data/patients.json`
```json
[
  {
    "patient_id": "PAT-000001",
    "name": "Jane Doe",
    "age": 34,
    "phone": "+2348012345678",
    "email": "jane@example.com",
    "blood_group": "O+",
    "allergies": ["penicillin"],
    "medical_history": ["hypertension"]
  }
]
```

### `data/appointments.csv`
```
appointment_id,patient_id,doctor_id,date_time,status,notes
APT-000001,PAT-000001,STF-001,2025-09-15 10:30,scheduled,Follow-up
```

### Patient ID format: `PAT-XXXXXX` (regex: `^PAT-[0-9]{6}$`)
### Appointment ID format: `APT-XXXXXX` (regex: `^APT-[0-9]{6}$`)
### Staff ID format: `STF-XXX` (regex: `^STF-[0-9]{3}$`)
### Date/time format: `YYYY-MM-DD HH:MM` (24-hour)

---

## Validation Rules (Regex)

All validation logic lives in **Victor James's module** (`models/`) or in the page that collects input.
Ireoluwade Oyerinde raises `ValidationError` when these fail.

| Field | Pattern |
|-------|---------|
| Phone | `^\+?[0-9]{10,13}$` |
| Email | `^[\w\.-]+@[\w\.-]+\.\w{2,}$` |
| Patient ID | `^PAT-[0-9]{6}$` |
| Date/Time | `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$` |

---

## How to Import Across Modules

```python
# Correct — always use full module paths from project root
from models.patient import Patient
from models.appointment import Appointment
from managers.file_handler import FileHandler
from managers.patient_registry import PatientRegistry
from managers.appointment_manager import AppointmentManager
from services.ai_assistant import AIAssistant
from services.api_client import APIClient
from exceptions.custom_exceptions import PatientNotFoundError, ValidationError
```

Run the app from the `meditrack/` root:
```bash
streamlit run main.py
```

---

## Git Rules

1. **Never commit directly to `main`.** Always work on your feature branch.
2. **Branch naming:** `feature/<your-module>` — exactly as listed in the ownership table.
3. **Before opening a PR:** pull the latest `main` into your branch and resolve any conflicts locally.
4. **PR requirement:** at least one other member must review and approve before merging.
5. **`.gitignore` must include:**
   ```
   .env
   *.env
   logs/
   __pycache__/
   .streamlit/secrets.toml
   ```
6. **API keys go in `.env` only.** Never hardcode keys. Load them with `os.getenv("GEMINI_API_KEY")`.

---

## Environment Variables

Create a `.env` file locally (never commit it):
```
GEMINI_API_KEY=your_key_here
```

Load in code:
```python
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

---

## Merge Conflict Prevention — Quick Rules

- **Models (Victor James):** Define all fields in `__init__`. Don't add fields elsewhere.
- **FileHandler (Usman Yahya):** The only file that reads/writes to `data/`. No other member should open those files directly.
- **Exceptions (Ireoluwade Oyerinde):** The only file that defines exception classes. Import, don't redefine.
- **UI (Abdulmujeeb Alatise):** Owns sidebar and navigation in `main.py`. Page members own only their page's content, not layout.
- **If you need a new method on someone else's class:** open a GitHub issue or message the owner — do not add it yourself.
