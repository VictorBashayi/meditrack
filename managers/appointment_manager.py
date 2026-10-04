# Owned by Alwali Kazir
"""AppointmentManager.

All persistence goes through FileHandler. This module never opens
data/appointments.csv (or any other data file) directly.
"""
from datetime import datetime

from exceptions.custom_exceptions import (
    AppointmentConflictError,
    FileOperationError,
    ValidationError,
)
from managers.file_handler import FileHandler
from models.appointment import Appointment, PATIENT_ID_PATTERN


class AppointmentManager:
    def __init__(self, file_handler: FileHandler | None = None):
        self._file_handler = file_handler or FileHandler()

    # ---- internal helpers -------------------------------------------------

    def _load(self) -> list[Appointment]:
        appointments = []
        for row in self._file_handler.load_appointments():
            # Excel's "CSV UTF-8" export prepends a BOM to the first header,
            # which would otherwise show up as a missing field.
            clean = {(k or "").lstrip("\ufeff").strip(): v for k, v in row.items()}
            appointments.append(Appointment.from_dict(clean))
        return appointments

    def _save(self, appointments: list[Appointment]) -> None:
        self._file_handler.save_appointments([a.to_dict() for a in appointments])

    def _log(self, message: str) -> None:
        # The audit log is best-effort: a logging failure must not undo or
        # hide an appointment change that was already saved.
        try:
            self._file_handler.write_log(message)
        except FileOperationError:
            pass

    @staticmethod
    def _find_conflict(appointments: list[Appointment], doctor_id: str,
                       date_time: datetime, ignore_id: str | None = None) -> Appointment | None:
        """Return an active appointment for this doctor at this exact slot, if any."""
        for existing in appointments:
            if (existing.appointment_id != ignore_id
                    and existing.status == "scheduled"
                    and existing.doctor_id == doctor_id
                    and existing.date_time == date_time):
                return existing
        return None

    @staticmethod
    def _get(appointments: list[Appointment], appointment_id: str) -> Appointment:
        for appointment in appointments:
            if appointment.appointment_id == appointment_id:
                return appointment
        # No dedicated "not found" exception exists in the shared contract,
        # so ValidationError is used rather than defining a new one here.
        raise ValidationError(f"Appointment '{appointment_id}' was not found.")

    # ---- public interface (matches CLAUDE.md contract) ---------------------

    def schedule(self, appointment: Appointment) -> None:
        """Save a new appointment. Raises AppointmentConflictError if the slot is taken."""
        appointments = self._load()

        if any(a.appointment_id == appointment.appointment_id for a in appointments):
            raise ValidationError(f"Appointment ID '{appointment.appointment_id}' already exists.")

        if appointment.status == "scheduled":
            clash = self._find_conflict(appointments, appointment.doctor_id, appointment.date_time)
            if clash:
                raise AppointmentConflictError(
                    f"Doctor {appointment.doctor_id} already has appointment "
                    f"{clash.appointment_id} at "
                    f"{appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
                )

        appointments.append(appointment)
        self._save(appointments)
        self._log(f"Scheduled {appointment.appointment_id} for {appointment.patient_id} "
                  f"with {appointment.doctor_id} at {appointment.to_dict()['date_time']}")

    def cancel(self, appointment_id: str) -> None:
        """Mark an appointment as cancelled (the record is kept for the audit trail)."""
        appointments = self._load()
        appointment = self._get(appointments, appointment_id)
        if appointment.status == "cancelled":
            raise ValidationError(f"Appointment '{appointment_id}' is already cancelled.")
        if appointment.status == "completed":
            raise ValidationError(f"Appointment '{appointment_id}' is completed and cannot be cancelled.")

        appointment.status = "cancelled"
        self._save(appointments)
        self._log(f"Cancelled {appointment_id}")

    def reschedule(self, appointment_id: str, new_datetime: datetime) -> None:
        """Move a scheduled appointment. Raises AppointmentConflictError if the new slot is taken."""
        if not isinstance(new_datetime, datetime):
            raise ValidationError("new_datetime must be a datetime object.")

        appointments = self._load()
        appointment = self._get(appointments, appointment_id)
        if appointment.status != "scheduled":
            raise ValidationError(
                f"Only scheduled appointments can be rescheduled (this one is {appointment.status})."
            )

        clash = self._find_conflict(appointments, appointment.doctor_id, new_datetime,
                                    ignore_id=appointment_id)
        if clash:
            raise AppointmentConflictError(
                f"Doctor {appointment.doctor_id} already has appointment "
                f"{clash.appointment_id} at {new_datetime.strftime('%Y-%m-%d %H:%M')}."
            )

        old_slot = appointment.to_dict()["date_time"]
        appointment.date_time = new_datetime
        self._save(appointments)
        self._log(f"Rescheduled {appointment_id} from {old_slot} to "
                  f"{new_datetime.strftime('%Y-%m-%d %H:%M')}")

    def get_by_patient(self, patient_id: str) -> list[Appointment]:
        if not isinstance(patient_id, str) or not PATIENT_ID_PATTERN.match(patient_id):
            raise ValidationError(
                f"Invalid patient ID '{patient_id}'. Expected format PAT-XXXXXX (6 digits)."
            )
        return sorted((a for a in self._load() if a.patient_id == patient_id),
                      key=lambda a: a.date_time)

    def list_all(self) -> list[Appointment]:
        return sorted(self._load(), key=lambda a: a.date_time)

    # ---- extra helper (on my own class; contract methods are unchanged) ----

    def next_appointment_id(self) -> str:
        """Generate the next free ID in APT-XXXXXX format."""
        highest = 0
        for appointment in self._load():
            highest = max(highest, int(appointment.appointment_id.split("-")[1]))
        return f"APT-{highest + 1:06d}"
