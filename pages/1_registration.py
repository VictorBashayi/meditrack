# Owned by Victor James
"""
pages/1_registration.py
-----------------------
Streamlit page for Patient Registration.

Owner: Victor James
Branch: feature/patient-registration

Allows clinic staff to:
1. Register new patients with full demographic and medical records.
2. Auto-generate or specify standard patient IDs (format: PAT-XXXXXX).
3. Validate phone, email, and blood group according to project rules.
4. View the registry of all currently registered patients.
"""

import re
import random
import streamlit as st

from models.patient import Patient, VALID_BLOOD_GROUPS
from managers.patient_registry import PatientRegistry
from exceptions.custom_exceptions import (
    ValidationError,
    PatientNotFoundError,
    MediTrackError,
)

# Regex validation patterns from CLAUDE.md
PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,13}$")
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
PATIENT_ID_PATTERN = re.compile(r"^PAT-[0-9]{6}$")


def generate_next_patient_id(existing_ids: set[str]) -> str:
    """Generate a unique sequential or random 6-digit patient ID."""
    # Attempt sequential first based on count
    for idx in range(1, 1000000):
        candidate = f"PAT-{idx:06d}"
        if candidate not in existing_ids:
            return candidate
    # Fallback to random if needed
    while True:
        candidate = f"PAT-{random.randint(100000, 999999)}"
        if candidate not in existing_ids:
            return candidate


def main():
    st.set_page_config(
        page_title="MediTrack - Patient Registration",
        page_icon="📋",
        layout="wide",
    )

    st.title("📋 Patient Registration")
    st.markdown(
        "Register a new patient into the MediTrack system. "
        "All required demographic, contact, and medical details are validated upon submission."
    )
    st.divider()

    # Instantiate registry
    registry = PatientRegistry()
    all_patients = registry.list_all()
    existing_ids = {p.patient_id for p in all_patients}

    # Top stats metric cards
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    col_metric1.metric("Total Patients Registered", len(all_patients))
    col_metric2.metric("Next Suggested ID", generate_next_patient_id(existing_ids))
    col_metric3.metric("Supported Blood Groups", len(VALID_BLOOD_GROUPS))

    st.write("")

    # Form layout
    tab_register, tab_view = st.tabs(["➕ Register New Patient", "👥 View Registered Patients"])

    with tab_register:
        st.subheader("New Patient Details")

        with st.form("patient_registration_form", clear_on_submit=False):
            # Row 1: Identification & Basic Info
            col1, col2 = st.columns(2)

            with col1:
                suggested_id = generate_next_patient_id(existing_ids)
                patient_id = st.text_input(
                    "Patient ID *",
                    value=suggested_id,
                    help="Format must match PAT-XXXXXX (e.g., PAT-000001)",
                )

                name = st.text_input(
                    "Full Name *",
                    placeholder="e.g. Jane Doe",
                )

                age = st.number_input(
                    "Age *",
                    min_value=0,
                    max_value=150,
                    value=30,
                    step=1,
                )

            with col2:
                phone = st.text_input(
                    "Phone Number *",
                    placeholder="+2348012345678",
                    help="10 to 13 digits, optional leading + (e.g., +2348012345678)",
                )

                email = st.text_input(
                    "Email Address *",
                    placeholder="jane.doe@example.com",
                    help="Valid email format: user@domain.com",
                )

                blood_group = st.selectbox(
                    "Blood Group *",
                    options=sorted(list(VALID_BLOOD_GROUPS)),
                    index=sorted(list(VALID_BLOOD_GROUPS)).index("O+") if "O+" in VALID_BLOOD_GROUPS else 0,
                )

            st.markdown("---")
            st.subheader("Medical Information")

            col3, col4 = st.columns(2)

            with col3:
                allergies_input = st.text_area(
                    "Allergies (comma-separated or one per line)",
                    placeholder="e.g. Penicillin, Peanuts, Latex\n(Leave blank if none)",
                    help="Enter any known allergies. Separate multiple entries with commas or newlines.",
                )

            with col4:
                medical_history_input = st.text_area(
                    "Medical History (comma-separated or one per line)",
                    placeholder="e.g. Hypertension, Asthma, Type 2 Diabetes\n(Leave blank if none)",
                    help="Enter previous medical conditions or diagnoses.",
                )

            submitted = st.form_submit_button("💾 Save Patient Record", use_container_width=True)

        if submitted:
            # Client-side / UI validations
            errors = []

            # 1. Clean and validate Patient ID
            clean_patient_id = patient_id.strip().upper()
            if not clean_patient_id:
                errors.append("Patient ID is required.")
            elif not PATIENT_ID_PATTERN.match(clean_patient_id):
                errors.append(f"Patient ID '{clean_patient_id}' is invalid. Format must be PAT-XXXXXX with 6 digits.")

            # 2. Validate Name
            clean_name = name.strip()
            if not clean_name:
                errors.append("Full Name is required.")

            # 3. Validate Phone
            clean_phone = phone.strip()
            if not clean_phone:
                errors.append("Phone number is required.")
            elif not PHONE_PATTERN.match(clean_phone):
                errors.append(f"Phone number '{clean_phone}' is invalid. Must be 10-13 digits (optional leading +).")

            # 4. Validate Email
            clean_email = email.strip()
            if not clean_email:
                errors.append("Email address is required.")
            elif not EMAIL_PATTERN.match(clean_email):
                errors.append(f"Email '{clean_email}' is invalid.")

            # Parse Allergies & Medical History
            allergies = [
                item.strip()
                for item in re.split(r"[,\n]+", allergies_input)
                if item.strip()
            ]

            medical_history = [
                item.strip()
                for item in re.split(r"[,\n]+", medical_history_input)
                if item.strip()
            ]

            # Display any client validation errors
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                try:
                    # Construct patient model
                    new_patient = Patient(
                        patient_id=clean_patient_id,
                        name=clean_name,
                        age=int(age),
                        phone=clean_phone,
                        email=clean_email,
                        blood_group=blood_group,
                        allergies=allergies,
                        medical_history=medical_history,
                    )

                    # Persist via registry
                    registry.register(new_patient)

                    st.success(f"✅ Successfully registered patient **{clean_name}** ({clean_patient_id})!")
                    st.balloons()

                    # Show summary card
                    with st.expander("📋 View Registered Record Summary", expanded=True):
                        st.json(new_patient.to_dict())

                except ValidationError as e:
                    st.error(f"⚠️ Validation Error: {e}")
                except MediTrackError as e:
                    st.error(f"⚠️ MediTrack Error: {e}")
                except Exception as e:
                    st.error(f"⚠️ An unexpected error occurred: {e}")

    with tab_view:
        st.subheader("Registered Patients Directory")

        # Reload list in case a new patient was just added
        current_patients = registry.list_all()

        if not current_patients:
            st.info("No patients registered yet. Use the 'Register New Patient' tab to add records.")
        else:
            search_query = st.text_input("🔍 Search by Name or ID", placeholder="e.g. Jane or PAT-000001")

            filtered_patients = current_patients
            if search_query:
                q = search_query.strip().lower()
                filtered_patients = [
                    p for p in current_patients
                    if q in p.name.lower() or q in p.patient_id.lower()
                ]

            st.write(f"Showing **{len(filtered_patients)}** of **{len(current_patients)}** patients")

            # Convert to displayable format
            table_data = []
            for p in filtered_patients:
                table_data.append({
                    "Patient ID": p.patient_id,
                    "Name": p.name,
                    "Age": p.age,
                    "Phone": p.phone,
                    "Email": p.email,
                    "Blood Group": p.blood_group,
                    "Allergies": ", ".join(p.allergies) if p.allergies else "None",
                    "Medical History": ", ".join(p.medical_history) if p.medical_history else "None",
                })

            st.dataframe(table_data, use_container_width=True)


if __name__ == "__main__":
    main()
