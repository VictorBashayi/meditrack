# MediTrack — Hospital Appointment & Patient Management System

A desktop application that digitises and streamlines how small to mid-sized hospitals and clinics
manage patient records and appointments. Built with Python and Streamlit.

---

## How GitHub Branching Works on This Project

> **Read this before touching any file.** This is the most important section if you are new to GitHub.

Think of `main` as the **official, always-working version** of the project. Nobody writes code directly on `main`. Instead, every member works on their **own personal branch** — a separate copy of the project that only they touch. When their work is ready and reviewed, it gets merged into `main`.

Here is the full picture:

```
main  ──────────────────────────────────────────────────────► (always stable)
  │
  ├── feature/exception-handling     (Ireoluwade Oyerinde's branch)
  ├── feature/patient-registration   (Victor James's branch)
  ├── feature/file-handling          (Usman Yahya's branch)
  ├── feature/appointment-scheduling (Alwali Kazir's branch)
  ├── feature/ai-assistant           (Mary Tabai's branch)
  ├── feature/api-integration        (Mohammed Usman's branch)
  ├── feature/ui-layout              (Abdulmujeeb Alatise's branch)
  └── feature/reporting              (Ephraim Effiong's branch)
```

Each branch is a **safe sandbox**. Changes on your branch do not affect `main` or anyone else's branch until you open a Pull Request and the team merges it.

---

## Team & Branch Assignments

| Member | Module | Branch Name | Files You Own |
|--------|--------|-------------|---------------|
| Victor James | Patient Registration | `feature/patient-registration` | `models/person.py`, `models/patient.py`, `models/staff.py`, `managers/patient_registry.py`, `pages/1_registration.py` |
| Alwali Kazir | Appointment Scheduling | `feature/appointment-scheduling` | `models/appointment.py`, `managers/appointment_manager.py`, `pages/2_appointments.py` |
| Usman Yahya | File Handling & Data Persistence | `feature/file-handling` | `managers/file_handler.py` |
| Mary Tabai | AI Assistant | `feature/ai-assistant` | `services/ai_assistant.py`, `pages/4_ai_assistant.py` |
| Mohammed Usman | Public API Integration | `feature/api-integration` | `services/api_client.py`, `pages/3_patient_lookup.py` |
| Ireoluwade Oyerinde | Exception Handling | `feature/exception-handling` | `exceptions/custom_exceptions.py` |
| Abdulmujeeb Alatise | UI Layout & Navigation | `feature/ui-layout` | `main.py` |
| Ephraim Effiong | Reporting & Export | `feature/reporting` | `pages/5_reports.py` |

> **Rule:** You write code **only** inside the files listed under your name. If you need something from another member's file, call their functions — do not copy or rewrite their code.

---

## Step-by-Step Setup (Do This Once)

### Step 1 — Install Git
If you don't have Git installed, download it from https://git-scm.com and install it.
To check if it's already installed, open your terminal and run:
```bash
git --version
```

### Step 2 — Clone the repository
This downloads the project to your computer. Run this once:
```bash
git clone https://github.com/VictorBashayi/meditrack.git
cd meditrack
```

### Step 3 — Create a virtual environment and install dependencies
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install streamlit google-generativeai python-dotenv requests
```

### Step 4 — Create your `.env` file
Create a file named `.env` in the `meditrack/` folder (never commit this file):
```
GEMINI_API_KEY=your_key_here
```
Confirm `.env` is listed in `.gitignore` before you do anything else.

### Step 5 — Create YOUR branch
This is the most important step. Find your branch name in the team table above, then run:
```bash
git checkout -b feature/your-module-name
```
For example, if you are Ireoluwade:
```bash
git checkout -b feature/exception-handling
```
Then push the branch to GitHub so it exists online:
```bash
git push -u origin feature/your-module-name
```
You are now on your own branch. You will stay here for all your work.

---

## Daily Workflow (What You Do Every Time You Work)

```bash
# 1. Make sure you are on YOUR branch (always check this first)
git branch
# The branch with a * next to it is your current branch

# 2. Do your work — edit only your assigned files

# 3. Save your changes to Git
git add .
git commit -m "Short description of what you did"

# 4. Push your changes to GitHub
git push origin feature/your-module-name
```

That is it. Your changes go to your branch only — not to `main`, not to anyone else's branch.

---

## How to Merge Into Main (When Your Work is Ready)

Only do this when your module is fully complete and tested.

1. Go to https://github.com/VictorBashayi/meditrack
2. Click **"Pull requests"** → **"New pull request"**
3. Set **base** to `main` and **compare** to your branch
4. Write a short description of what you built
5. Request at least one other team member to review it
6. Once approved, click **"Merge pull request"**

> **Do not merge your own PR without a review.** This is what keeps `main` stable.

---

## Keeping Your Branch Up to Date

When other members merge their work into `main`, you need to pull those changes into your branch so you are not working on an outdated version:

```bash
# While on your own branch:
git pull origin main
```

Do this before you open a Pull Request. Resolve any conflicts locally before pushing.

---

## Run the App

```bash
streamlit run main.py
```

---

## Project Structure

```
meditrack/
├── main.py                        # Owned by Abdulmujeeb Alatise
├── pages/
│   ├── 1_registration.py          # Owned by Victor James
│   ├── 2_appointments.py          # Owned by Alwali Kazir
│   ├── 3_patient_lookup.py        # Owned by Mohammed Usman
│   ├── 4_ai_assistant.py          # Owned by Mary Tabai
│   └── 5_reports.py               # Owned by Ephraim Effiong
├── models/
│   ├── person.py                  # Owned by Victor James
│   ├── patient.py                 # Owned by Victor James
│   ├── staff.py                   # Owned by Victor James
│   └── appointment.py             # Owned by Alwali Kazir
├── managers/
│   ├── patient_registry.py        # Owned by Victor James
│   ├── appointment_manager.py     # Owned by Alwali Kazir
│   └── file_handler.py            # Owned by Usman Yahya
├── services/
│   ├── ai_assistant.py            # Owned by Mary Tabai
│   └── api_client.py              # Owned by Mohammed Usman
├── exceptions/
│   └── custom_exceptions.py       # Owned by Ireoluwade Oyerinde
├── data/
│   ├── patients.json
│   └── appointments.csv
├── logs/
├── CLAUDE.md                      # Full team coding contract
├── .gitignore
└── README.md
```

---

**Read the full team coding contract in `CLAUDE.md` before writing any code.**
