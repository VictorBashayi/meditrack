# Owned by Ephraim Effiong

import streamlit as st

from managers.file_handler import FileHandler
from exceptions.custom_exceptions import (
    PatientNotFoundError,
    FileOperationError,
    MediTrackError
)


st.title("MediTrack Reports")
st.write("Generate and view patient reports and appointment records.")


# Create FileHandler
file_handler = FileHandler()


# ---------------------------------------------------------
# PATIENT HISTORY REPORT
# ---------------------------------------------------------

st.subheader("Patient History Report")

patient_id = st.text_input(
    "Enter Patient ID",
    placeholder="Example: PAT-000001"
)

if st.button("Generate Patient Report"):

    if not patient_id:
        st.warning("Please enter a Patient ID.")

    else:
        try:
            report_path = file_handler.export_patient_report(
                patient_id
            )

            st.success("Patient report generated successfully.")

            st.write("Report file:")
            st.code(report_path)

            file_handler.write_log(
                f"Patient report generated for {patient_id}"
            )

        except PatientNotFoundError as error:
            st.error(str(error))

        except FileOperationError as error:
            st.error(f"Report error: {error}")

        except MediTrackError as error:
            st.error(f"MediTrack error: {error}")

        except Exception as error:
            st.error(
                f"Unable to generate patient report: {error}"
            )


# ---------------------------------------------------------
# APPOINTMENT RECORDS
# ---------------------------------------------------------

st.divider()

st.subheader("Appointment Records")

if st.button("Load Appointment Records"):

    try:
        appointments = file_handler.load_appointments()

        if appointments:
            st.dataframe(
                appointments,
                use_container_width=True
            )

            file_handler.write_log(
                "Appointment records viewed from Reports page"
            )

        else:
            st.info("No appointment records found.")

    except PatientNotFoundError as error:
        st.error(str(error))

    except FileOperationError as error:
        st.error(f"Unable to load appointment records: {error}")

    except MediTrackError as error:
        st.error(f"MediTrack error: {error}")

    except Exception as error:
        st.error(
            f"Unable to load appointment records: {error}"
        )


# ---------------------------------------------------------
# PATIENT RECORDS
# ---------------------------------------------------------

st.divider()

st.subheader("Patient Records")

if st.button("Load Patient Records"):

    try:
        patients = file_handler.load_patients()

        if patients:
            st.dataframe(
                patients,
                use_container_width=True
            )

            file_handler.write_log(
                "Patient records viewed from Reports page"
            )

        else:
            st.info("No patient records found.")

    except PatientNotFoundError as error:
        st.error(str(error))

    except FileOperationError as error:
        st.error(f"Unable to load patient records: {error}")

    except MediTrackError as error:
        st.error(f"MediTrack error: {error}")

    except Exception as error:
        st.error(
            f"Unable to load patient records: {error}"
        )


# ---------------------------------------------------------
# REPORTING ACTIVITY
# ---------------------------------------------------------

st.divider()

st.subheader("Reporting Activity")

st.write(
    "Patient reports and record views are recorded "
    "in the MediTrack session log."
)