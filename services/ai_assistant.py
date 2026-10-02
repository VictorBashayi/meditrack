"""
Original owner: Mary Tabai
Now maintained by: Victor James (covering after team change)
Branch: feature/ai-assistant
"""

"""
services/ai_assistant.py
------------------------
Gemini API wrapper for MediTrack's AI-powered features.

Owner: Mary Tabai
Branch: feature/ai-assistant

This is the ONLY place in the project where google.generativeai is called.
Pages never interact with Gemini directly — they call AIAssistant methods.

Features implemented:
    1. generate_patient_summary(patient) -> str
       Compiles the patient's full record into a structured prompt and
       returns a concise plain-English clinical summary from Gemini.

    2. suggest_triage(patient, symptoms) -> dict
       Sends symptom description + patient context to Gemini and returns
       a structured triage response: urgency, probable condition,
       referral suggestion, and precautionary notes.

Setup:
    Requires GEMINI_API_KEY in .env at the project root.
    Install: pip install google-generativeai python-dotenv
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from models.patient import Patient
from exceptions.custom_exceptions import APIError

# Load .env from project root on module import
load_dotenv()

# Model name as specified in the project proposal
_MODEL_NAME = "gemini-1.5-flash"

# Disclaimer that must accompany every AI output in the UI
AI_DISCLAIMER = "⚠️ AI-Generated — Not a Medical Diagnosis. For clinical use only as a reference aid."


def _load_client() -> genai.GenerativeModel:
    """
    Initialise and return the Gemini GenerativeModel.

    Raises
    ------
    APIError
        If GEMINI_API_KEY is missing from the environment.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise APIError(
            "Gemini API key not found. "
            "Add GEMINI_API_KEY to your .env file and restart the app."
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(_MODEL_NAME)


class AIAssistant:
    """
    Wraps the Google Gemini API for MediTrack's two AI features.

    Usage (from a page):
    --------------------
        from services.ai_assistant import AIAssistant, AI_DISCLAIMER
        from exceptions.custom_exceptions import APIError

        assistant = AIAssistant()

        try:
            summary = assistant.generate_patient_summary(patient)
            st.write(summary)
            st.caption(AI_DISCLAIMER)
        except APIError as e:
            st.warning(str(e))

    Both methods raise APIError on any failure — missing key, network
    error, or an unusable response from Gemini. The calling page is
    responsible for catching APIError and showing a graceful fallback.
    """

    def __init__(self):
        """
        Initialise the assistant and verify the API key is present.

        Raises
        ------
        APIError
            If GEMINI_API_KEY is not set in the environment.
        """
        self._model = _load_client()

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _call_gemini(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the response text.

        Parameters
        ----------
        prompt : The full prompt string to send.

        Returns
        -------
        str
            The text content of Gemini's response.

        Raises
        ------
        APIError
            If the API call fails or returns an empty/unusable response.
        """
        try:
            response = self._model.generate_content(prompt)

            # Gemini can return an empty response if content is blocked
            if not response or not response.text:
                raise APIError(
                    "Gemini returned an empty response. "
                    "The content may have been filtered. Please try again."
                )

            return response.text.strip()

        except APIError:
            raise

        except Exception as e:
            raise APIError(
                f"An error occurred while contacting the Gemini API: {e}"
            )

    # ------------------------------------------------------------------
    # Feature 1 — Patient Summary Generator
    # ------------------------------------------------------------------

    def generate_summary(self, patient: Patient) -> str:
        """
        Generate a plain-English clinical summary for a patient.

        Compiles the patient's full record — name, age, blood group,
        allergies, and medical history — into a structured prompt and
        returns a concise summary suitable for a doctor's pre-consultation
        briefing.

        Parameters
        ----------
        patient : A fully-initialised Patient instance from the registry.

        Returns
        -------
        str
            A formatted clinical summary from Gemini covering:
            - Brief narrative of the patient's background and presenting history
            - Patterns across historical visit notes (if any)
            - Flags for potential drug interactions (if applicable)
            - A structured snapshot paragraph for quick reading

        Raises
        ------
        APIError
            If the API call fails or Gemini returns an unusable response.
        """
        allergies_text = (
            ", ".join(patient.allergies) if patient.allergies else "None recorded"
        )
        history_text = (
            "\n    - " + "\n    - ".join(patient.medical_history)
            if patient.medical_history
            else "No medical history recorded."
        )

        prompt = f"""
You are a clinical documentation assistant for a hospital management system.
Your role is to generate a concise, structured patient summary for use by
attending medical staff before a consultation. Write in clear, professional
plain English. Do not invent or assume information not provided.

Patient Record:
---------------
Name:           {patient.name}
Age:            {patient.age}
Blood Group:    {patient.blood_group}
Known Allergies: {allergies_text}
Medical History:
    {history_text}

Instructions:
-------------
Write a structured patient summary with the following four sections.
Use these exact section headings:

1. Patient Overview
   A 2-3 sentence narrative covering the patient's age, blood group,
   and general medical background based on their history.

2. Key History Highlights
   Identify any notable patterns or significant entries in the medical
   history. If the history is empty, state that clearly.

3. Allergy & Interaction Flags
   List all known allergies. If the patient has a medical history involving
   medications, flag any general categories of drugs that warrant caution
   given those allergies. If no allergies, state "No known allergies."

4. Pre-Consultation Snapshot
   A single short paragraph (3-5 sentences) that a doctor can read in
   under 30 seconds to be briefed on this patient before walking in.

Keep the entire summary under 400 words. Do not include any disclaimers
or commentary outside these four sections.
""".strip()

        return self._call_gemini(prompt)

    # ------------------------------------------------------------------
    # Feature 2 — Symptom Triage Suggestion
    # ------------------------------------------------------------------

    def triage_suggestion(self, symptoms: list[str]) -> str:
        """
        Generate a structured triage suggestion based on reported symptoms.

        Sends the symptom list to Gemini with a triage-focused prompt and
        returns a triage recommendation string.

        Parameters
        ----------
        symptoms : List of symptom strings as entered by clinical staff.

        Returns
        -------
        str
            Triage recommendation string from Gemini.

        Raises
        ------
        APIError
            If the API call fails or the response cannot be parsed.
        """
        symptoms_text = "\n".join(f"- {s}" for s in symptoms) if symptoms else "None reported"

        prompt = f"""
You are a clinical triage assistant in a hospital management system.
Based on the reported symptoms below, provide a triage recommendation
for clinical staff. This is a decision support tool only — final triage
decisions rest with qualified medical staff.

Reported Symptoms:
------------------
{symptoms_text}

Instructions:
-------------
Respond with a concise triage recommendation covering:
- Urgency level (Routine / Urgent / Immediate) with a brief reason
- The broad clinical category the symptoms suggest
- Recommended department or specialist referral
- Key precautionary notes or red-flag symptoms to watch

Keep the response clear and professional. Do not invent information
not present in the symptom list.
""".strip()

        return self._call_gemini(prompt)