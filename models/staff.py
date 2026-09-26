# Owned by Victor James
"""
models/staff.py
---------------
Staff model — extends Person with employment fields.

Owner: Victor James
Branch: feature/patient-registration

ID format enforced here: STF-XXX  (regex: ^STF-[0-9]{3}$)

Staff objects are used as "doctor" references inside Appointment objects —
the doctor_id field on an Appointment must be a valid staff_id from this class.
Staff records are not persisted in this sprint (no FileHandler call for staff
yet), but to_dict() is implemented so the class is ready when that's added.
"""

import re

from models.person import Person

_STAFF_ID_PATTERN = re.compile(r"^STF-[0-9]{3}$")

# Shift values the system recognises. Extend this tuple via PR if needed.
VALID_SHIFTS = ("morning", "afternoon", "night")


class Staff(Person):
    """
    Represents a hospital staff member (doctor, nurse, administrator, etc.)

    Attributes (beyond Person)
    --------------------------
    staff_id   : Unique identifier. Format: STF-XXX (three digits).
    role       : Job title / role string, e.g. "Doctor", "Nurse", "Receptionist".
    department : Hospital department, e.g. "Cardiology", "Emergency".
    shift      : One of "morning" | "afternoon" | "night".
    """

    def __init__(
        self,
        staff_id: str,
        name: str,
        age: int,
        phone: str,
        email: str,
        role: str,
        department: str,
        shift: str,
    ):
        """
        Parameters
        ----------
        staff_id   : Must match ^STF-[0-9]{3}$. ValidationError raised if not.
        role       : Free-form string. No enum constraint — departments vary.
        department : Free-form string.
        shift      : Case-insensitive. Normalised to lowercase on storage.
                     Must be one of "morning", "afternoon", "night".

        All other parameters are inherited from Person.
        """
        from exceptions.custom_exceptions import ValidationError

        if not _STAFF_ID_PATTERN.match(staff_id):
            raise ValidationError(
                f"Invalid staff ID '{staff_id}'. "
                "Expected format: STF-XXX (three digits)."
            )

        normalised_shift = shift.strip().lower()
        if normalised_shift not in VALID_SHIFTS:
            raise ValidationError(
                f"Invalid shift '{shift}'. "
                f"Must be one of: {', '.join(VALID_SHIFTS)}."
            )

        super().__init__(name=name, age=age, phone=phone, email=email)

        self.staff_id = staff_id
        self.role = role
        self.department = department
        self.shift = normalised_shift

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialise to a plain dictionary.

        Returns
        -------
        dict
            {
                "staff_id":   "STF-001",
                "name":       "Dr. Adaeze Obi",
                "age":        42,
                "phone":      "+2348099876543",
                "email":      "adaeze.obi@hospital.ng",
                "role":       "Doctor",
                "department": "Cardiology",
                "shift":      "morning"
            }
        """
        base = super().to_dict()
        base.update({
            "staff_id": self.staff_id,
            "role": self.role,
            "department": self.department,
            "shift": self.shift,
        })
        return base

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        """
        Convenience property used by the appointment UI dropdown.
        Returns something like: "Dr. Adaeze Obi — Cardiology (morning)"
        """
        return f"{self.name} — {self.department} ({self.shift})"

    def __repr__(self) -> str:
        return (
            f"Staff(id={self.staff_id!r}, name={self.name!r}, "
            f"role={self.role!r}, department={self.department!r})"
        )