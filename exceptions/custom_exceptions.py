# Owned by Ireoluwade Oyerinde
"""
exceptions/custom_exceptions.py
--------------------------------
All custom exceptions for the MediTrack system.

Original owner: Ireoluwade Oyerinde
Now maintained by: Victor James (covering after team change)
Branch: feature/exception-handling

─────────────────────────────────────────────────────────────────
RULES FOR THE WHOLE TEAM — read before touching this file
─────────────────────────────────────────────────────────────────
1. This is the ONE place exceptions are defined. Do not define
   exception classes anywhere else in the project.

2. Every module that needs to raise or catch a MediTrack error
   imports from here:

       from exceptions.custom_exceptions import PatientNotFoundError

3. Do not catch bare Exception in page code. Catch the most
   specific subclass you expect, then fall back to MediTrackError
   for anything unexpected, e.g.:

       try:
           registry.get_patient(pid)
       except PatientNotFoundError:
           st.error("Patient not found.")
       except MediTrackError as e:
           st.error(f"Unexpected error: {e}")

4. When raising, always pass a human-readable message. The UI
   layer surfaces these directly to the user, so write them in
   plain English not developer jargon.

       raise PatientNotFoundError(f"No patient found with ID '{patient_id}'.")

5. Do not add new exception classes without a team PR discussion.
   The six classes below cover every error category in the system.
─────────────────────────────────────────────────────────────────
"""


class MediTrackError(Exception):
    """
    Base exception for every error raised by MediTrack.

    Catch this class when you want a single handler that covers
    all application-level errors regardless of category:

        except MediTrackError as e:
            st.error(str(e))

    Never raise MediTrackError directly — raise one of its
    subclasses so the caller can handle specific cases
    differently if needed.
    """


class PatientNotFoundError(MediTrackError):
    """
    Raised when a patient_id lookup returns no matching record.

    Where it's raised
    -----------------
    PatientRegistry.get_patient() — when the requested ID does
    not exist in patients.json.

    How to raise it
    ---------------
        raise PatientNotFoundError(
            f"No patient found with ID '{patient_id}'. "
            "Check the ID and try again."
        )

    How to catch it (in page code)
    --------------------------------
        try:
            patient = registry.get_patient(patient_id)
        except PatientNotFoundError:
            st.warning("Patient not found. Please check the ID.")
    """


class AppointmentConflictError(MediTrackError):
    """
    Raised when a doctor already has an appointment at the
    requested date/time slot.

    Where it's raised
    -----------------
    AppointmentManager.schedule() — after checking existing
    appointments for the same doctor_id and date_time.

    How to raise it
    ---------------
        raise AppointmentConflictError(
            f"Dr. {doctor_name} already has an appointment at "
            f"{date_time}. Please choose a different time slot."
        )

    How to catch it (in page code)
    --------------------------------
        try:
            manager.schedule(appointment)
        except AppointmentConflictError as e:
            st.error(str(e))
    """


class FileOperationError(MediTrackError):
    """
    Raised when a file read, write, or export operation fails.

    Covers: missing files, permission errors, corrupted JSON/CSV,
    failed TXT report exports.

    Where it's raised
    -----------------
    FileHandler — wraps all open(), json.load(), csv.writer(),
    and os-level calls.

    How to raise it
    ---------------
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise FileOperationError(
                f"Could not read patient data from '{path}': {e}"
            ) from e

    The "from e" part chains the original exception so the full
    traceback is preserved in logs even though the UI sees a
    clean message.

    How to catch it (in page code)
    --------------------------------
        try:
            patients = file_handler.load_patients()
        except FileOperationError as e:
            st.error(f"Failed to load patient records: {e}")
    """


class APIError(MediTrackError):
    """
    Raised when an external API call fails or returns an
    unusable response.

    Covers: network timeouts, HTTP error status codes (4xx/5xx),
    malformed JSON responses from Gemini, disease.sh, or OpenFDA.

    Where it's raised
    -----------------
    AIAssistant and APIClient — wrap every requests.get() /
    requests.post() call.

    How to raise it
    ---------------
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise APIError(
                "The request to the disease API timed out. "
                "Check your internet connection and try again."
            )
        except requests.exceptions.HTTPError as e:
            raise APIError(
                f"The API returned an error: {e.response.status_code}."
            ) from e

    How to catch it (in page code)
    --------------------------------
        try:
            stats = api_client.get_disease_stats(disease)
        except APIError as e:
            st.warning(f"Could not fetch data: {e}")
    """


class ValidationError(MediTrackError):
    """
    Raised when a field value fails regex or business-rule
    validation before it reaches the data layer.

    Covers: malformed patient IDs, invalid phone/email formats,
    bad date strings, unrecognised blood groups, invalid shift
    values, and any other input that does not pass a format check.

    Where it's raised
    -----------------
    models/patient.py  — patient_id format, blood_group values
    models/staff.py    — staff_id format, shift values
    pages/*.py         — phone, email, date/time regex checks
                         before data is passed to a model or manager

    How to raise it
    ---------------
        # compile your pattern at module level, then check:
        if not PHONE_PATTERN.match(phone):
            raise ValidationError(
                f"'{phone}' is not a valid phone number. "
                "Use 10-13 digits, optionally starting with +."
            )

    How to catch it (in page code)
    --------------------------------
        try:
            patient = Patient(patient_id, name, age, ...)
        except ValidationError as e:
            st.error(str(e))
            st.stop()
    """