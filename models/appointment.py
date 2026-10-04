# Owned by Alwali Kazir
"""Appointment model.

Follows the shared contract in CLAUDE.md exactly:
    Appointment(appointment_id, patient_id, doctor_id, date_time, status, notes="")
    to_dict() -> dict          (keys in CSV column order)
    from_dict(data) -> Appointment   (static)
"""
import re
from datetime import datetime

from exceptions.custom_exceptions import ValidationError

APPOINTMENT_ID_PATTERN = re.compile(r"^APT-[0-9]{6}$")
PATIENT_ID_PATTERN = re.compile(r"^PAT-[0-9]{6}$")
DOCTOR_ID_PATTERN = re.compile(r"^STF-[0-9]{3}$")
DATE_TIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M"
VALID_STATUSES = ("scheduled", "completed", "cancelled")


def parse_date_time(value: str) -> datetime:
    """Validate a 'YYYY-MM-DD HH:MM' string with regex, then parse it.

    Raises ValidationError if the format or the actual date/time is invalid.
    """
    if not isinstance(value, str) or not DATE_TIME_PATTERN.match(value.strip()):
        raise ValidationError(
            f"Invalid date/time '{value}'. Use the format YYYY-MM-DD HH:MM (24-hour)."
        )
    try:
        return datetime.strptime(value.strip(), DATE_TIME_FORMAT)
    except ValueError as exc:
        raise ValidationError(f"'{value}' is not a real date/time.") from exc


class Appointment:
    def __init__(self, appointment_id: str, patient_id: str, doctor_id: str,
                 date_time: datetime, status: str, notes: str = ""):
        if not isinstance(appointment_id, str) or not APPOINTMENT_ID_PATTERN.match(appointment_id):
            raise ValidationError(
                f"Invalid appointment ID '{appointment_id}'. Expected format APT-XXXXXX (6 digits)."
            )
        if not isinstance(patient_id, str) or not PATIENT_ID_PATTERN.match(patient_id):
            raise ValidationError(
                f"Invalid patient ID '{patient_id}'. Expected format PAT-XXXXXX (6 digits)."
            )
        if not isinstance(doctor_id, str) or not DOCTOR_ID_PATTERN.match(doctor_id):
            raise ValidationError(
                f"Invalid doctor ID '{doctor_id}'. Expected format STF-XXX (3 digits)."
            )
        if not isinstance(date_time, datetime):
            raise ValidationError("date_time must be a datetime object.")

        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date_time = date_time
        self.status = status  # validated by the property setter below
        self.notes = notes or ""

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        if value not in VALID_STATUSES:
            raise ValidationError(
                f"Invalid status '{value}'. Must be one of: {', '.join(VALID_STATUSES)}."
            )
        self._status = value

    def to_dict(self) -> dict:
        # Key order matches data/appointments.csv columns.
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "date_time": self.date_time.strftime(DATE_TIME_FORMAT),
            "status": self.status,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Appointment":
        try:
            return Appointment(
                appointment_id=data["appointment_id"],
                patient_id=data["patient_id"],
                doctor_id=data["doctor_id"],
                date_time=parse_date_time(data["date_time"]),
                status=data["status"],
                notes=data.get("notes") or "",
            )
        except KeyError as exc:
            raise ValidationError(f"Appointment record is missing field {exc}.") from exc

    def __repr__(self) -> str:
        return (f"Appointment({self.appointment_id}, {self.patient_id}, {self.doctor_id}, "
                f"{self.date_time.strftime(DATE_TIME_FORMAT)}, {self.status})")
