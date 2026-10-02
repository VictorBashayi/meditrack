"""
Original owner: Mary Tabai
Now maintained by: Victor James (covering after team change)
Branch: feature/ai-assistant
"""

"""
pages/4_ai_assistant.py
-----------------------
Streamlit page for MediTrack's AI-powered features.

Owner: Mary Tabai
Branch: feature/ai-assistant

Allows clinical staff to:
1. Generate a plain-English clinical summary for any registered patient.
2. Get a structured triage suggestion based on reported symptoms.

Both features use the AIAssistant service which wraps the Google Gemini API.
All AI output is labelled with the mandatory disclaimer from the project proposal.
"""

import streamlit as st

from managers.patient_registry import PatientRegistry
from services.ai_assistant import AIAssistant, AI_DISCLAIMER
from exceptions.custom_exceptions import (
    PatientNotFoundError,
    APIError,
    MediTrackError,
)

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="MediTrack — AI Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Assistant")
st.markdown(
    "Use Gemini to generate clinical patient summaries and symptom triage suggestions. "
    "All outputs are clearly labelled and intended as reference aids only."
)
st.divider()


# ------------------------------------------------------------------
# Initialise shared objects
# ------------------------------------------------------------------

registry = PatientRegistry()

# Initialise AIAssistant once and cache it for the session.
# If the API key is missing, show an error immediately and stop.
if "ai_assistant" not in st.session_state:
    try:
        st.session_state.ai_assistant = AIAssistant()
    except APIError as e:
        st.error(f"⚠️ AI Assistant could not start: {e}")
        st.info(
            "Add your Gemini API key to the `.env` file in the project root:\n\n"
            "```\nGEMINI_API_KEY=your_key_here\n```\n\n"
            "Then restart the app."
        )
        st.stop()

assistant: AIAssistant = st.session_state.ai_assistant


# ------------------------------------------------------------------
# Patient ID input — shared by both tabs
# ------------------------------------------------------------------

st.subheader("Select Patient")

col_id, col_load = st.columns([3, 1])

with col_id:
    patient_id_input = st.text_input(
        "Patient ID",
        placeholder="e.g. PAT-000001",
        label_visibility="collapsed",
        key="ai_patient_id",
    )

with col_load:
    load_clicked = st.button("Load Patient", use_container_width=True)

# ------------------------------------------------------------------
# Patient loading
# ------------------------------------------------------------------

if load_clicked:
    clean_id = patient_id_input.strip().upper()

    if not clean_id:
        st.warning("Enter a Patient ID first.")
    else:
        try:
            st.session_state.ai_patient = registry.get_patient(clean_id)
            st.session_state.ai_patient_loaded = True
        except PatientNotFoundError:
            st.error(
                f"❌ No patient found with ID **{clean_id}**. "
                "Check the ID and try again."
            )
            st.session_state.ai_patient_loaded = False
        except MediTrackError as e:
            st.error(f"⚠️ {e}")
            st.session_state.ai_patient_loaded = False

# ------------------------------------------------------------------
# Main content — only shown once a patient is loaded
# ------------------------------------------------------------------

if st.session_state.get("ai_patient_loaded"):
    patient = st.session_state.ai_patient

    # Patient banner
    st.success(
        f"Patient loaded: **{patient.name}** ({patient.patient_id}) — "
        f"Age {patient.age} · Blood Group {patient.blood_group}"
    )

    st.divider()

    tab_summary, tab_triage = st.tabs(
        ["📋 Patient Summary", "🚨 Symptom Triage"]
    )

    # ------------------------------------------------------------------
    # Tab 1 — Patient Summary Generator
    # ------------------------------------------------------------------

    with tab_summary:
        st.subheader("Patient Summary Generator")
        st.markdown(
            "Click the button below to generate a concise clinical summary "
            "for **{}**. The summary is built from their registered medical "
            "record and is intended to brief the attending doctor before a "
            "consultation.".format(patient.name)
        )

        # Show what data will be used
        with st.expander("📂 Data used to generate this summary", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Blood Group**")
                st.write(patient.blood_group)

                st.markdown("**Known Allergies**")
                if patient.allergies:
                    for a in patient.allergies:
                        st.write(f"• {a}")
                else:
                    st.write("None recorded")

            with col_b:
                st.markdown("**Medical History**")
                if patient.medical_history:
                    for h in patient.medical_history:
                        st.write(f"• {h}")
                else:
                    st.write("None recorded")

        generate_btn = st.button(
            "✨ Generate Summary",
            use_container_width=False,
            key="generate_summary_btn",
        )

        if generate_btn:
            with st.spinner("Generating clinical summary..."):
                try:
                    summary = assistant.generate_summary(patient)

                    st.write("")
                    st.markdown("### Clinical Summary")
                    st.markdown(summary)

                    # Mandatory disclaimer — required by project proposal
                    st.divider()
                    st.caption(AI_DISCLAIMER)

                except APIError as e:
                    st.warning(
                        f"⚠️ Could not generate summary: {e}\n\n"
                        "Check your internet connection and API key, then try again."
                    )

    # ------------------------------------------------------------------
    # Tab 2 — Symptom Triage Suggestion
    # ------------------------------------------------------------------

    with tab_triage:
        st.subheader("Symptom Triage Suggestion")
        st.markdown(
            "Describe the patient's current symptoms below. Gemini will return "
            "a structured triage suggestion including urgency level, probable "
            "condition category, referral recommendation, and precautionary notes."
        )

        symptoms_input = st.text_area(
            "Symptom Description",
            placeholder=(
                "e.g. Patient presents with high fever (39.5°C), persistent dry cough "
                "for 5 days, shortness of breath on exertion, and fatigue. "
                "No chest pain reported."
            ),
            height=150,
            key="symptoms_input",
        )

        triage_btn = st.button(
            "🚨 Get Triage Suggestion",
            use_container_width=False,
            key="triage_btn",
        )

        if triage_btn:
            if not symptoms_input.strip():
                st.warning("Enter a symptom description before running triage.")
            else:
                with st.spinner("Analysing symptoms..."):
                    try:
                        triage = assistant.triage_suggestion([symptoms_input])

                        st.write("")
                        st.markdown(triage)

                        # Mandatory disclaimer
                        st.divider()
                        st.caption(AI_DISCLAIMER)

                    except APIError as e:
                        st.warning(
                            f"⚠️ Could not generate triage suggestion: {e}\n\n"
                            "Check your internet connection and API key, then try again."
                        )

else:
    # No patient loaded yet — show a helpful placeholder
    st.info(
        "Enter a Patient ID above and click **Load Patient** to get started. "
        "The AI features will appear once a patient record is loaded."
    )