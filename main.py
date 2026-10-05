# Owned by Abdulmujeeb Alatise
import streamlit as st

st.set_page_config(page_title="MediTrack", page_icon="🏥", layout="wide")

# Streamlit builds the sidebar page list automatically from the pages/ folder.
# We only add a title above it.
st.sidebar.title("🏥 MediTrack")
st.sidebar.caption("Patient and appointment management")

st.title("🏥 MediTrack")
st.write("Choose a section to get started.")

col1, col2 = st.columns(2)
with col1:
    # page_link makes a clickable link to another page file.
    st.page_link("pages/1_registration.py", label="Patient registration", icon="📝")
    st.caption("Register new patients and update their records.")
    st.page_link("pages/2_appointments.py", label="Appointments", icon="📅")
    st.caption("Book, reschedule, and cancel appointments.")
    st.page_link("pages/3_patient_lookup.py", label="Patient lookup", icon="🔍")
    st.caption("Find a patient and check drug and disease reference data.")
with col2:
    st.page_link("pages/4_ai_assistant.py", label="AI assistant", icon="🤖")
    st.caption("Generate patient summaries and triage suggestions.")
    st.page_link("pages/5_reports.py", label="Reports", icon="📊")
    st.caption("Export patient histories and appointment logs.")
