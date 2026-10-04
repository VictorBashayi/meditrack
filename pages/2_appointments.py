# Owned by Alwali Kazir
"""Appointments page: schedule, view, cancel and reschedule appointments.

Talks only to AppointmentManager (and PatientRegistry to confirm a patient
exists). It never reads or writes data files itself.
"""
from datetime import date, datetime, time

import streamlit as st

from exceptions.custom_exceptions import (
    AppointmentConflictError,
    FileOperationError,
    MediTrackError,
    PatientNotFoundError,
    ValidationError,
)
from managers.appointment_manager import AppointmentManager
from models.appointment import (
    DATE_TIME_FORMAT,
    DOCTOR_ID_PATTERN,
    PATIENT_ID_PATTERN,
    Appointment,
    parse_date_time,
)

manager = AppointmentManager()

# PatientRegistry belongs to Victor and may not be merged yet. Until it is,
# the page still works and simply skips the "does this patient exist" check.
try:
    from managers.patient_registry import PatientRegistry
    registry = PatientRegistry()
except (ImportError, TypeError):
    registry = None


def show_flash() -> None:
    """Show a success message left by the previous action (survives st.rerun)."""
    message = st.session_state.pop("appointment_flash", None)
    if message:
        st.success(message)


def build_datetime(day: date, at: time) -> datetime:
    # Round-trip through the string format so the regex check in the model runs.
    return parse_date_time(f"{day.strftime('%Y-%m-%d')} {at.strftime('%H:%M')}")


st.title("Appointments")
show_flash()

try:
    all_appointments = manager.list_all()
except (FileOperationError, ValidationError) as exc:
    st.error(f"Could not load appointments: {exc}")
    st.stop()

if registry is None:
    st.caption("Patient lookup is not available yet, so patient IDs are not checked against registered patients.")

schedule_tab, manage_tab, table_tab = st.tabs(["Schedule", "Cancel or reschedule", "All appointments"])

# ---- Schedule -----------------------------------------------------------------
with schedule_tab:
    with st.form("schedule_form", clear_on_submit=False):
        left, right = st.columns(2)
        patient_id = left.text_input("Patient ID", placeholder="PAT-000001").strip()
        doctor_id = right.text_input("Doctor ID", placeholder="STF-001").strip()
        day = left.date_input("Date", value=date.today())
        at = right.time_input("Time", value=time(9, 0), step=900)
        notes = st.text_area("Notes (optional)", placeholder="Follow-up, reason for visit...")
        submitted = st.form_submit_button("Schedule appointment")

    if submitted:
        try:
            if not PATIENT_ID_PATTERN.match(patient_id):
                raise ValidationError("Patient ID must look like PAT-000001.")
            if not DOCTOR_ID_PATTERN.match(doctor_id):
                raise ValidationError("Doctor ID must look like STF-001.")

            slot = build_datetime(day, at)
            if slot < datetime.now():
                raise ValidationError("Pick a date and time in the future.")

            if registry is not None:
                registry.get_patient(patient_id)  # raises PatientNotFoundError

            appointment = Appointment(
                appointment_id=manager.next_appointment_id(),
                patient_id=patient_id,
                doctor_id=doctor_id,
                date_time=slot,
                status="scheduled",
                notes=notes.strip(),
            )
            manager.schedule(appointment)
            st.session_state["appointment_flash"] = (
                f"Scheduled {appointment.appointment_id} for {patient_id} "
                f"with {doctor_id} on {slot.strftime(DATE_TIME_FORMAT)}."
            )
            st.rerun()
        except PatientNotFoundError:
            st.error(f"No patient found with ID {patient_id}. Register the patient first.")
        except AppointmentConflictError as exc:
            st.error(f"Time slot unavailable. {exc}")
        except (ValidationError, FileOperationError) as exc:
            st.error(str(exc))
        except MediTrackError as exc:
            st.error(f"Something went wrong: {exc}")

# ---- Cancel / reschedule --------------------------------------------------------
with manage_tab:
    active = [a for a in all_appointments if a.status == "scheduled"]
    if not active:
        st.info("There are no scheduled appointments to change.")
    else:
        labels = {
            a.appointment_id: (f"{a.appointment_id} | {a.patient_id} with {a.doctor_id} | "
                               f"{a.date_time.strftime(DATE_TIME_FORMAT)}")
            for a in active
        }
        chosen_id = st.selectbox("Appointment", options=list(labels), format_func=labels.get)
        chosen = next(a for a in active if a.appointment_id == chosen_id)

        st.markdown("**Reschedule**")
        left, right = st.columns(2)
        new_day = left.date_input("New date", value=max(chosen.date_time.date(), date.today()),
                                  key="resched_day")
        new_time = right.time_input("New time", value=chosen.date_time.time(), step=900,
                                    key="resched_time")

        reschedule_col, cancel_col, _ = st.columns([1, 1, 3])
        if reschedule_col.button("Reschedule", type="primary"):
            try:
                new_slot = build_datetime(new_day, new_time)
                if new_slot < datetime.now():
                    raise ValidationError("Pick a date and time in the future.")
                manager.reschedule(chosen_id, new_slot)
                st.session_state["appointment_flash"] = (
                    f"Moved {chosen_id} to {new_slot.strftime(DATE_TIME_FORMAT)}."
                )
                st.rerun()
            except AppointmentConflictError as exc:
                st.error(f"Time slot unavailable. {exc}")
            except (ValidationError, FileOperationError) as exc:
                st.error(str(exc))
            except MediTrackError as exc:
                st.error(f"Something went wrong: {exc}")

        if cancel_col.button("Cancel appointment"):
            try:
                manager.cancel(chosen_id)
                st.session_state["appointment_flash"] = f"Cancelled {chosen_id}."
                st.rerun()
            except (ValidationError, FileOperationError) as exc:
                st.error(str(exc))
            except MediTrackError as exc:
                st.error(f"Something went wrong: {exc}")

# ---- Table ---------------------------------------------------------------------
with table_tab:
    left, right = st.columns([2, 1])
    patient_filter = left.text_input("Filter by patient ID", placeholder="PAT-000001",
                                     key="table_patient_filter").strip()
    status_filter = right.selectbox("Status", ["all", "scheduled", "completed", "cancelled"])

    rows = all_appointments
    if patient_filter:
        try:
            rows = manager.get_by_patient(patient_filter)
        except ValidationError as exc:
            st.error(str(exc))
            rows = []
    if status_filter != "all":
        rows = [a for a in rows if a.status == status_filter]

    if rows:
        st.dataframe([a.to_dict() for a in rows], use_container_width=True, hide_index=True)
    else:
        st.info("No appointments match. Schedule one from the first tab.")
