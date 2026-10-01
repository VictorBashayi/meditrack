# Owned by Victor James
"""
managers/patient_registry.py
-----------------------------
In-memory patient registry backed by FileHandler for persistence.

Owner: Victor James
Branch: feature/patient-registration

This is the single gateway for patient CRUD operations. Pages and services
call these methods — they never read/write patients.json directly.

Contract (from CLAUDE.md):
    register(patient)            -> None
    get_patient(patient_id)      -> Patient   (raises PatientNotFoundError)
    update_patient(patient_id, updates) -> None
    list_all()                   -> list[Patient]
"""

from models.patient import Patient
from managers.file_handler import FileHandler
from exceptions.custom_exceptions import (
    PatientNotFoundError,
    ValidationError,
)


class PatientRegistry:
    """
    Manages the collection of registered patients.

    On construction the registry loads every record from patients.json
    into an internal dict keyed by patient_id. All mutations are flushed
    back to disk immediately through FileHandler so no data is lost if
    the Streamlit process restarts.
    """

    def __init__(self, file_handler: FileHandler | None = None):
        """
        Parameters
        ----------
        file_handler : Optional FileHandler instance. A default one is
                       created when omitted, which is fine for production.
                       Passing one explicitly is useful in tests or when
                       the same handler is shared across managers.
        """
        self._file_handler = file_handler or FileHandler()

        # keyed by patient_id for O(1) lookups
        self._patients: dict[str, Patient] = {}
        self._load()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the in-memory dict from patients.json."""
        raw_records = self._file_handler.load_patients()
        self._patients = {
            record["patient_id"]: Patient.from_dict(record)
            for record in raw_records
        }

    def _save(self) -> None:
        """Flush the full patient list back to patients.json."""
        all_dicts = [patient.to_dict() for patient in self._patients.values()]
        self._file_handler.save_patients(all_dicts)

    # ------------------------------------------------------------------
    # Public interface (matches CLAUDE.md contract exactly)
    # ------------------------------------------------------------------

    def register(self, patient: Patient) -> None:
        """
        Add a new patient to the registry.

        Parameters
        ----------
        patient : A fully-constructed Patient instance (ID already assigned).

        Raises
        ------
        ValidationError
            If a patient with the same patient_id is already registered.
            Duplicate IDs would silently overwrite data, so we reject them.
        """
        if patient.patient_id in self._patients:
            raise ValidationError(
                f"Patient '{patient.patient_id}' is already registered. "
                "Use update_patient() to modify an existing record."
            )

        self._patients[patient.patient_id] = patient
        self._save()
        self._file_handler.write_log(
            f"Registered new patient: {patient.patient_id} ({patient.name})"
        )

    def get_patient(self, patient_id: str) -> Patient:
        """
        Look up a single patient by ID.

        Parameters
        ----------
        patient_id : Must match the PAT-XXXXXX format.

        Returns
        -------
        Patient

        Raises
        ------
        PatientNotFoundError
            If no patient with that ID exists in the registry.
        """
        patient = self._patients.get(patient_id)
        if patient is None:
            raise PatientNotFoundError(
                f"No patient found with ID '{patient_id}'. "
                "Check the ID and try again."
            )
        return patient

    def update_patient(self, patient_id: str, updates: dict) -> None:
        """
        Apply partial updates to an existing patient record.

        Parameters
        ----------
        patient_id : ID of the patient to update.
        updates    : Dict of field names to new values. Only the keys
                     present are changed; everything else stays the same.

                     Allowed keys (any subset):
                         name, age, phone, email,
                         blood_group, allergies, medical_history

                     patient_id cannot be changed — it is silently ignored
                     if included in *updates*.

        Raises
        ------
        PatientNotFoundError
            If the patient_id does not exist.
        ValidationError
            If a new blood_group value is invalid (caught by Patient.__init__).
        """
        patient = self.get_patient(patient_id)  # raises if missing

        # Build a fresh dict from the current state, overlay the updates,
        # then reconstruct via from_dict so all validation re-runs.
        current = patient.to_dict()

        # Never allow the ID itself to be changed.
        updates.pop("patient_id", None)

        current.update(updates)

        # Reconstruct — Patient.__init__ re-validates blood_group, etc.
        updated_patient = Patient.from_dict(current)

        self._patients[patient_id] = updated_patient
        self._save()
        self._file_handler.write_log(
            f"Updated patient: {patient_id} (fields: {', '.join(updates.keys())})"
        )

    def list_all(self) -> list[Patient]:
        """
        Return every registered patient.

        Returns
        -------
        list[Patient]
            Sorted by patient_id for deterministic ordering in the UI.
            Returns an empty list if no patients are registered.
        """
        return sorted(
            self._patients.values(),
            key=lambda p: p.patient_id,
        )
