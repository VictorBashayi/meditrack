# Owned by Usman Yahya

import csv
import json
from datetime import datetime
from pathlib import Path

from exceptions.custom_exceptions import FileOperationError


class FileHandler:
    """Handles MediTrack file storage and file operations."""

    def __init__(self):
        # Project root folder
        self.base_dir = Path(__file__).resolve().parent.parent

        # Data and logs folders
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"

        # Data files
        self.patients_file = self.data_dir / "patients.json"
        self.appointments_file = self.data_dir / "appointments.csv"

        # Create folders if they do not already exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # STEP 1: SAVE PATIENTS
    # ---------------------------------------------------------

    def save_patients(self, patients: list[dict]) -> None:
        """Save patient records to patients.json."""

        try:
            with open(
                self.patients_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(patients, file, indent=2)

        except (OSError, TypeError, ValueError) as error:
            raise FileOperationError(
                f"Unable to save patient records: {error}"
            )

    # ---------------------------------------------------------
    # STEP 2: LOAD PATIENTS
    # ---------------------------------------------------------

    def load_patients(self) -> list[dict]:
        """Load patient records from patients.json."""

        try:
            if not self.patients_file.exists():
                return []

            with open(
                self.patients_file,
                "r",
                encoding="utf-8"
            ) as file:
                patients = json.load(file)

            if not isinstance(patients, list):
                raise ValueError(
                    "Patient data must be stored as a list."
                )

            return patients

        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise FileOperationError(
                f"Unable to load patient records: {error}"
            )

    # ---------------------------------------------------------
    # STEP 3: SAVE APPOINTMENTS
    # ---------------------------------------------------------

    def save_appointments(
        self,
        appointments: list[dict]
    ) -> None:
        """Save appointment records to appointments.csv."""

        fieldnames = [
            "appointment_id",
            "patient_id",
            "doctor_id",
            "date_time",
            "status",
            "notes"
        ]

        try:
            with open(
                self.appointments_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames
                )

                writer.writeheader()
                writer.writerows(appointments)

        except (OSError, csv.Error, TypeError) as error:
            raise FileOperationError(
                f"Unable to save appointment records: {error}"
            )

    # ---------------------------------------------------------
    # STEP 4: LOAD APPOINTMENTS
    # ---------------------------------------------------------

    def load_appointments(self) -> list[dict]:
        """Load appointment records from appointments.csv."""

        try:
            if not self.appointments_file.exists():
                return []

            with open(
                self.appointments_file,
                "r",
                newline="",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)
                appointments = list(reader)

            return appointments

        except (OSError, csv.Error) as error:
            raise FileOperationError(
                f"Unable to load appointment records: {error}"
            )

    # ---------------------------------------------------------
    # STEP 5: WRITE SESSION LOG
    # ---------------------------------------------------------

    def write_log(self, message: str) -> None:
        """Write an activity message to today's session log."""

        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            log_file = (
                self.logs_dir /
                f"session_{current_date}.txt"
            )

            with open(
                log_file,
                "a",
                encoding="utf-8"
            ) as file:
                file.write(
                    f"[{current_time}] {message}\n"
                )

        except OSError as error:
            raise FileOperationError(
                f"Unable to write session log: {error}"
            )

    # ---------------------------------------------------------
    # STEP 6: EXPORT PATIENT REPORT
    # ---------------------------------------------------------

    def export_patient_report(
        self,
        patient_id: str
    ) -> str:
        """
        Export a patient's information and appointment
        history into a TXT file.

        Returns:
            str: Path of the exported report.
        """

        try:
            # Load patient information
            patients = self.load_patients()

            patient = None

            for record in patients:
                if record.get("patient_id") == patient_id:
                    patient = record
                    break

            if patient is None:
                raise FileOperationError(
                    f"Patient with ID {patient_id} was not found."
                )

            # Load appointment information
            appointments = self.load_appointments()

            # Find this patient's appointments
            patient_appointments = [
                appointment
                for appointment in appointments
                if appointment.get("patient_id") == patient_id
            ]

            # Create reports folder
            reports_dir = self.data_dir / "reports"
            reports_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # Report filename
            report_file = (
                reports_dir /
                f"{patient_id}_report.txt"
            )

            # Write report
            with open(
                report_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write("=" * 60 + "\n")
                file.write("           MEDITRACK PATIENT REPORT\n")
                file.write("=" * 60 + "\n\n")

                # Patient information
                file.write("PATIENT INFORMATION\n")
                file.write("-" * 60 + "\n")

                file.write(
                    f"Patient ID: "
                    f"{patient.get('patient_id', '')}\n"
                )

                file.write(
                    f"Name: "
                    f"{patient.get('name', '')}\n"
                )

                file.write(
                    f"Age: "
                    f"{patient.get('age', '')}\n"
                )

                file.write(
                    f"Phone: "
                    f"{patient.get('phone', '')}\n"
                )

                file.write(
                    f"Email: "
                    f"{patient.get('email', '')}\n"
                )

                file.write(
                    f"Blood Group: "
                    f"{patient.get('blood_group', '')}\n"
                )

                # Allergies
                file.write("\nAllergies:\n")

                allergies = patient.get(
                    "allergies",
                    []
                )

                if allergies:
                    for allergy in allergies:
                        file.write(f"- {allergy}\n")
                else:
                    file.write("- None recorded\n")

                # Medical history
                file.write("\nMedical History:\n")

                medical_history = patient.get(
                    "medical_history",
                    []
                )

                if medical_history:
                    for history in medical_history:
                        file.write(f"- {history}\n")
                else:
                    file.write("- None recorded\n")

                # Appointment history
                file.write("\nAPPOINTMENT HISTORY\n")
                file.write("-" * 60 + "\n")

                if patient_appointments:

                    for appointment in patient_appointments:

                        file.write(
                            f"Appointment ID: "
                            f"{appointment.get('appointment_id', '')}\n"
                        )

                        file.write(
                            f"Doctor ID: "
                            f"{appointment.get('doctor_id', '')}\n"
                        )

                        file.write(
                            f"Date & Time: "
                            f"{appointment.get('date_time', '')}\n"
                        )

                        file.write(
                            f"Status: "
                            f"{appointment.get('status', '')}\n"
                        )

                        file.write(
                            f"Notes: "
                            f"{appointment.get('notes', '')}\n"
                        )

                        file.write("-" * 60 + "\n")

                else:
                    file.write(
                        "No appointments recorded.\n"
                    )

                file.write("\n")
                file.write("=" * 60 + "\n")
                file.write("End of Report\n")
                file.write("=" * 60 + "\n")

            return str(report_file)

        except FileOperationError:
            raise

        except OSError as error:
            raise FileOperationError(
                f"Unable to export patient report: {error}"
            )# Owned by Usman Yahya
