# Owned by Victor James
"""
models/patient.py
-----------------
Patient model — extends Person with medical record fields.

Owner: Victor James
Branch: feature/patient-registration

ID format enforced here: PAT-XXXXXX  (regex: ^PAT-[0-9]{6}$)
Blood group, allergies, and medical history are all required at construction
time so the registry never holds an incomplete record.

Consumers (AppointmentManager, AIAssistant, etc.) must call Patient.from_dict()
to reconstruct from stored JSON — do not build Patient objects by hand outside
of the registration page and the registry loader.
"""

import re

from models.person import Person

# Compile once at module level — reused for every ID validation call.
_PATIENT_ID_PATTERN = re.compile(r"^PAT-[0-9]{6}$")

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


class Patient(Person):
    """
    Represents a registered patient in MediTrack.

    Attributes (beyond Person)
    --------------------------
    patient_id      : Unique identifier. Format: PAT-XXXXXX.
    blood_group     : One of the 8 standard ABO/Rh groups ("O+", "AB-", …).
    allergies       : List of known allergen strings. Empty list if none.
    medical_history : List of past condition/diagnosis strings, oldest first.
    """

    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        phone: str,
        email: str,
        blood_group: str,
        allergies: list[str],
        medical_history: list[str],
    ):
        """
        Parameters
        ----------
        patient_id      : Must match ^PAT-[0-9]{6}$. A ValidationError is raised
                          if it does not — import from exceptions.custom_exceptions.
        blood_group     : Must be one of the 8 standard ABO/Rh groups. Case-sensitive.
        allergies       : Pass an empty list if the patient has no known allergies.
        medical_history : Pass an empty list for a patient with no recorded history.

        All other parameters are inherited from Person — see person.py for their
        validation responsibilities.
        """
        # Defer to the team's shared exception rather than raising ValueError
        # directly, so the UI layer only needs to catch MediTrackError subclasses.
        # Import is local to avoid a circular dependency at module load time
        # (exceptions module imports nothing from models).
        from exceptions.custom_exceptions import ValidationError

        if not _PATIENT_ID_PATTERN.match(patient_id):
            raise ValidationError(
                f"Invalid patient ID '{patient_id}'. "
                "Expected format: PAT-XXXXXX (six digits)."
            )

        if blood_group not in VALID_BLOOD_GROUPS:
            raise ValidationError(
                f"Invalid blood group '{blood_group}'. "
                f"Must be one of: {', '.join(sorted(VALID_BLOOD_GROUPS))}."
            )

        super().__init__(name=name, age=age, phone=phone, email=email)

        self.patient_id = patient_id
        self.blood_group = blood_group
        # Defensive copies so the caller can't mutate our state from outside.
        self.allergies = list(allergies)
        self.medical_history = list(medical_history)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialise this patient to a plain dictionary suitable for JSON storage.

        The returned structure matches the patients.json schema exactly:

            {
                "patient_id":      "PAT-000001",
                "name":            "Jane Doe",
                "age":             34,
                "phone":           "+2348012345678",
                "email":           "jane@example.com",
                "blood_group":     "O+",
                "allergies":       ["penicillin"],
                "medical_history": ["hypertension"]
            }

        FileHandler.save_patients() expects a list of these dicts.
        """
        base = super().to_dict()          # {"name": …, "age": …, "phone": …, "email": …}
        base.update({
            "patient_id": self.patient_id,
            "blood_group": self.blood_group,
            "allergies": list(self.allergies),
            "medical_history": list(self.medical_history),
        })
        return base

    @staticmethod
    def from_dict(data: dict) -> "Patient":
        """
        Reconstruct a Patient from a stored dictionary (e.g. one row loaded
        from patients.json by FileHandler.load_patients()).

        Parameters
        ----------
        data : A dict with exactly the keys produced by to_dict().
               Extra keys are silently ignored so that manually-added
               JSON fields don't break loading.

        Returns
        -------
        Patient
            A fully-initialised Patient instance.

        Raises
        ------
        ValidationError
            If patient_id or blood_group stored in the file is malformed.
            This should not happen with well-formed data but guards against
            manual edits to patients.json.
        KeyError
            If a required field is missing from the dict.
        """
        return Patient(
            patient_id=data["patient_id"],
            name=data["name"],
            age=data["age"],
            phone=data["phone"],
            email=data["email"],
            blood_group=data["blood_group"],
            allergies=data.get("allergies", []),
            medical_history=data.get("medical_history", []),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Patient(id={self.patient_id!r}, name={self.name!r}, "
            f"age={self.age}, blood_group={self.blood_group!r})"
        )