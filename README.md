# MediTrack
Hospital Appointment & Patient Management System

## Team Members
- **Victor James** - Patient Registration & Models (`feature/patient-registration`)
- **Alwali Kazir** - Appointment Scheduling (`feature/appointment-scheduling`)
- **Usman Yahya** - File Handling (`feature/file-handling`)
- **Mary Tabai** - AI Assistant (`feature/ai-assistant`)
- **Mohammed Usman** - API Integration (`feature/api-integration`)
- **Ireoluwade Oyerinde** - Exception Handling (`feature/exception-handling`)
- **Abdulmujeeb Alatise** - UI Layout (`feature/ui-layout`)
- **Ephraim Effiong** - Reporting (`feature/reporting`)

## Tech Stack
- **Language:** Python 3.11+
- **UI Framework:** Streamlit
- **AI API:** Google Gemini (`gemini-1.5-flash`)
- **Public APIs:** disease.sh, OpenFDA
- **Data Storage:** JSON (patients), CSV (appointments), TXT (logs)

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd meditrack
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install streamlit google-generativeai python-dotenv requests
```

### 4. Create `.env` file
Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_key_here
```

### 5. Run the application
```bash
streamlit run main.py
```

## Project Structure
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
└── logs/
```

## Development Guidelines
- **Never commit directly to `main`** — always work on your feature branch
- **Read `CLAUDE.md`** for the complete coding contract
- **Branch naming:** `feature/<your-module>` as listed above
- **PR requirement:** At least one team member must review before merging
- **API keys:** Never hardcode keys — use `.env` only

## Git Workflow
```bash
# Create your feature branch
git checkout -b feature/your-module

# Make changes, then commit
git add .
git commit -m "Description of changes"

# Push to your branch
git push origin feature/your-module

# Pull latest main before opening PR
git pull origin main

# Open PR on GitHub for review
```

---

**Read the full team coding contract in `CLAUDE.md` before writing any code.**
