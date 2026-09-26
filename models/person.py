# Owned by Victor James
"""
models/person.py
----------------
Base class for all people in the MediTrack system.
Patient and Staff both extend this class.

Owner: Victor James
Branch: feature/patient-registration

Do not add fields here without a team-wide PR discussion.
All validation (phone, email regex) lives in the page layer or models/patient.py.
"""


class Person:
    """
    Abstract base representing any person in the system.

    Not meant to be instantiated directly — use Patient or Staff instead.
    Holds the four fields shared by every person: name, age, phone, email.
    """

    def __init__(self, name: str, age: int, phone: str, email: str):
        """
        Parameters
        ----------
        name  : Full name of the person (no length restriction enforced here;
                validate before calling if needed).
        age   : Age in whole years. Must be a positive integer.
        phone : Phone number string. Caller is responsible for regex validation
                (pattern: optional leading +, then 10-13 digits) before passing in.
        email : Email address string. Caller is responsible for regex validation
                (standard email pattern) before passing in.
        """
        self.name = name
        self.age = age
        self.phone = phone
        self.email = email

    def to_dict(self) -> dict:
        """
        Return a plain dictionary of this person's shared fields.

        Subclasses call super().to_dict() and then update the result with
        their own fields, so the final dict is always complete.

        Returns
        -------
        dict
            Keys: "name", "age", "phone", "email"
        """
        return {
            "name": self.name,
            "age": self.age,
            "phone": self.phone,
            "email": self.email,
        }

    def __repr__(self) -> str:
        # Useful for debugging — subclasses will have more informative reprs.
        return f"{self.__class__.__name__}(name={self.name!r}, age={self.age})"