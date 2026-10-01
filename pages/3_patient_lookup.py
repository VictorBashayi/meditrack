# Owned by Mohammed Usman
"""
pages/3_patient_lookup.py
--------------------------
Streamlit page for Patient Lookup with live API data.

Owner: Mohammed Usman
Branch: feature/api-integration

Allows clinic staff to:
1. Search for a registered patient by ID.
2. View their full profile and medical record.
3. Look up live drug label information for any medication on their record.
4. Check for active drug recalls via OpenFDA.
5. Fetch real-time regional COVID-19 outbreak data via disease.sh.
"""

import streamlit as st

from managers.patient_registry import PatientRegistry
from services.api_client import APIClient
from exceptions.custom_exceptions import (
    PatientNotFoundError,
    APIError,
    MediTrackError,
)


# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="MediTrack — Patient Lookup",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Patient Lookup")
st.markdown(
    "Search for a registered patient to view their profile, "
    "look up drug safety information, and check live disease data."
)
st.divider()


# ------------------------------------------------------------------
# Initialise shared objects
# ------------------------------------------------------------------

registry = PatientRegistry()
api_client = APIClient()


# ------------------------------------------------------------------
# Section 1 — Patient Search
# ------------------------------------------------------------------

st.subheader("Patient Search")

col_input, col_btn = st.columns([3, 1])

with col_input:
    patient_id_input = st.text_input(
        "Patient ID",
        placeholder="e.g. PAT-000001",
        label_visibility="collapsed",
    )

with col_btn:
    search_clicked = st.button("🔍 Search", use_container_width=True)

# ------------------------------------------------------------------
# Patient result
# ------------------------------------------------------------------

if search_clicked:

    clean_id = patient_id_input.strip().upper()

    if not clean_id:
        st.warning("Please enter a Patient ID before searching.")

    else:
        try:
            patient = registry.get_patient(clean_id)

            # ----------------------------------------------------------
            # Patient profile card
            # ----------------------------------------------------------

            st.divider()
            st.subheader(f"📋 {patient.name}")

            col1, col2, col3 = st.columns(3)

            col1.metric("Patient ID", patient.patient_id)
            col2.metric("Age", patient.age)
            col3.metric("Blood Group", patient.blood_group)

            st.write("")

            col4, col5 = st.columns(2)

            with col4:
                st.markdown("**Contact Information**")
                st.write(f"📞 {patient.phone}")
                st.write(f"✉️  {patient.email}")

            with col5:
                st.markdown("**Allergies**")
                if patient.allergies:
                    for allergy in patient.allergies:
                        st.write(f"⚠️  {allergy}")
                else:
                    st.write("None recorded.")

            st.write("")
            st.markdown("**Medical History**")

            if patient.medical_history:
                for entry in patient.medical_history:
                    st.write(f"• {entry}")
            else:
                st.write("No medical history recorded.")

            # ----------------------------------------------------------
            # Section 2 — Drug Information (OpenFDA)
            # ----------------------------------------------------------

            st.divider()
            st.subheader("💊 Drug Information — OpenFDA")
            st.caption(
                "Look up official label data and recall status for any medication. "
                "Data sourced from the U.S. Food & Drug Administration."
            )

            drug_query = st.text_input(
                "Enter a drug name to look up",
                placeholder="e.g. Amoxicillin, Metformin, Ibuprofen",
                key="drug_input",
            )

            col_drug_btn1, col_drug_btn2 = st.columns(2)

            with col_drug_btn1:
                lookup_drug = st.button(
                    "📋 Get Drug Label Info",
                    use_container_width=True,
                    key="drug_label_btn",
                )

            with col_drug_btn2:
                check_recall = st.button(
                    "🚨 Check for Recalls",
                    use_container_width=True,
                    key="drug_recall_btn",
                )

            if lookup_drug:
                if not drug_query.strip():
                    st.warning("Enter a drug name first.")
                else:
                    with st.spinner(f"Fetching label info for '{drug_query}'..."):
                        try:
                            drug_info = api_client.get_drug_info(drug_query)

                            st.success(
                                f"Label found: **{drug_info['brand_name'] or drug_info['drug_name']}**"
                            )

                            col_d1, col_d2 = st.columns(2)

                            with col_d1:
                                st.markdown("**Brand Name**")
                                st.write(drug_info["brand_name"] or "—")

                                st.markdown("**Generic Name**")
                                st.write(drug_info["generic_name"] or "—")

                                st.markdown("**Manufacturer**")
                                st.write(drug_info["manufacturer"] or "—")

                            with col_d2:
                                st.markdown("**Indications (What it treats)**")
                                indications = drug_info["indications"]
                                if indications:
                                    st.write(indications[:500] + "..." if len(indications) > 500 else indications)
                                else:
                                    st.write("—")

                                st.markdown("**Dosage & Administration**")
                                dosage = drug_info["dosage"]
                                if dosage:
                                    st.write(dosage[:500] + "..." if len(dosage) > 500 else dosage)
                                else:
                                    st.write("—")

                            with st.expander("⚠️ Warnings", expanded=False):
                                warnings = drug_info["warnings"]
                                st.write(
                                    warnings[:1000] + "..." if warnings and len(warnings) > 1000
                                    else warnings or "No warnings listed."
                                )

                            with st.expander("🩺 Adverse Reactions", expanded=False):
                                adverse = drug_info["adverse_reactions"]
                                st.write(
                                    adverse[:1000] + "..." if adverse and len(adverse) > 1000
                                    else adverse or "No adverse reactions listed."
                                )

                            st.caption(f"Source: {drug_info['source']}")

                        except APIError as e:
                            st.warning(f"⚠️ Could not retrieve drug information: {e}")

            if check_recall:
                if not drug_query.strip():
                    st.warning("Enter a drug name first.")
                else:
                    with st.spinner(f"Checking recalls for '{drug_query}'..."):
                        try:
                            recalls = api_client.get_drug_recall(drug_query)

                            if not recalls:
                                st.success(
                                    f"✅ No active recalls found for '{drug_query}'."
                                )
                            else:
                                st.error(
                                    f"🚨 {len(recalls)} recall notice(s) found for '{drug_query}'."
                                )
                                for recall in recalls:
                                    with st.expander(
                                        f"Recall #{recall['recall_number']} — {recall['date'] or 'Date unknown'}",
                                        expanded=True,
                                    ):
                                        st.markdown(f"**Status:** {recall['status'] or '—'}")
                                        st.markdown(f"**Reason:** {recall['reason'] or '—'}")
                                        st.markdown(
                                            f"**Product:** {recall['product_description'] or '—'}"
                                        )

                            st.caption("Source: OpenFDA — U.S. Food & Drug Administration")

                        except APIError as e:
                            st.warning(f"⚠️ Could not check recall data: {e}")

            # ----------------------------------------------------------
            # Section 3 — Disease Outbreak Data (disease.sh)
            # ----------------------------------------------------------

            st.divider()
            st.subheader("🌍 Disease Outbreak Data — disease.sh")
            st.caption(
                "Fetch real-time outbreak statistics relevant to this patient's "
                "travel history or reported symptoms."
            )

            col_dis1, col_dis2 = st.columns(2)

            with col_dis1:
                disease_query = st.text_input(
                    "Disease name",
                    value="covid-19",
                    placeholder="e.g. covid-19",
                    key="disease_input",
                )

            with col_dis2:
                country_query = st.text_input(
                    "Country (optional — for regional stats)",
                    placeholder="e.g. Nigeria, US, GB",
                    key="country_input",
                )

            fetch_disease = st.button(
                "🌐 Fetch Outbreak Data",
                use_container_width=False,
                key="disease_btn",
            )

            if fetch_disease:
                if not disease_query.strip():
                    st.warning("Enter a disease name first.")
                else:
                    # Global stats
                    with st.spinner("Fetching global disease data..."):
                        try:
                            stats = api_client.get_disease_stats(disease_query)

                            st.markdown(f"**Global — {stats['disease']}**")

                            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                            col_s1.metric("Total Cases", f"{stats['cases']:,}" if stats["cases"] else "—")
                            col_s2.metric("Deaths", f"{stats['deaths']:,}" if stats["deaths"] else "—")
                            col_s3.metric("Recovered", f"{stats['recovered']:,}" if stats["recovered"] else "—")
                            col_s4.metric("Active", f"{stats['active']:,}" if stats["active"] else "—")

                            st.caption(f"Source: {stats['source']}")

                        except APIError as e:
                            st.warning(f"⚠️ {e}")

                    # Country-specific stats if a country was entered
                    if country_query.strip():
                        with st.spinner(f"Fetching data for {country_query}..."):
                            try:
                                country_stats = api_client.get_country_covid_stats(
                                    country_query
                                )

                                st.write("")
                                st.markdown(f"**{country_stats['country']} — COVID-19**")

                                col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
                                col_c1.metric("Cases", f"{country_stats['cases']:,}" if country_stats["cases"] else "—")
                                col_c2.metric("Deaths", f"{country_stats['deaths']:,}" if country_stats["deaths"] else "—")
                                col_c3.metric("Recovered", f"{country_stats['recovered']:,}" if country_stats["recovered"] else "—")
                                col_c4.metric("Active", f"{country_stats['active']:,}" if country_stats["active"] else "—")
                                col_c5.metric("Critical", f"{country_stats['critical']:,}" if country_stats["critical"] else "—")

                                st.caption(f"Source: {country_stats['source']}")

                            except APIError as e:
                                st.warning(f"⚠️ Could not fetch country data: {e}")

        except PatientNotFoundError:
            st.error(
                f"❌ No patient found with ID **{clean_id}**. "
                "Check the ID and try again."
            )

        except MediTrackError as e:
            st.error(f"⚠️ An error occurred: {e}")

        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {e}")