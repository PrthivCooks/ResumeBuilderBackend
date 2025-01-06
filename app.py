import streamlit as st
import google.generativeai as genai
import PyPDF2
from io import BytesIO
import json

# Configure Gemini API
genai.configure(api_key="AIzaSyAOw3Y-QYSQ1uq8XzcEdxdUS9tOHWcSRZw")
model = genai.GenerativeModel("gemini-1.5-flash")

# Helper function to process uploaded PDF and extract text
def process_resume(file):
    try:
        resume_content = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            resume_content += page.extract_text()
        return resume_content
    except Exception as e:
        raise ValueError(f"Error processing PDF: {e}")

# Streamlit app interface
st.title("Career Guidance API")

if "is_api_request" not in st.session_state:
    st.session_state.is_api_request = False

if st.session_state.is_api_request:
    # Handle API-like requests
    request_data = st.experimental_get_query_params()

    if "name" in request_data and "cgpa" in request_data and "goals" in request_data:
        name = request_data["name"][0]
        cgpa = request_data["cgpa"][0]
        goals = request_data["goals"][0]

        if "resume" in request_data:
            try:
                resume_bytes = BytesIO(bytes(request_data["resume"][0], "utf-8"))
                resume_text = process_resume(resume_bytes)

                # Prepare input for Gemini API
                input_data = (
                    f"Name: {name}\n"
                    f"CGPA: {cgpa}\n"
                    f"Resume: {resume_text}\n"
                    f"Goals: {goals}\n"
                    "Provide personalized career guidance based on this information."
                )

                # Generate output from Gemini
                response = model.generate_content(input_data)
                st.json({"output": response.text})
            except Exception as e:
                st.json({"error": str(e)})
        else:
            st.json({"error": "Missing resume content."})
    else:
        st.json({"error": "Invalid request. Required fields: name, cgpa, goals, resume."})
else:
    # Regular Streamlit UI for local testing
    st.subheader("Test the API Locally")
    name = st.text_input("Name")
    cgpa = st.text_input("CGPA")
    goals = st.text_area("Career Goals")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if st.button("Generate Guidance"):
        try:
            if not name or not cgpa or not uploaded_file or not goals:
                st.error("All fields are required!")
            else:
                # Process resume
                resume_text = process_resume(uploaded_file)

                # Prepare input for Gemini API
                input_data = (
                    f"Name: {name}\n"
                    f"CGPA: {cgpa}\n"
                    f"Resume: {resume_text}\n"
                    f"Goals: {goals}\n"
                    "Provide personalized career guidance based on this information."
                )

                # Generate output
                response = model.generate_content(input_data)
                st.success("Generated Output:")
                st.text_area("Output", response.text, height=300)
        except Exception as e:
            st.error(f"Error: {e}")

# Add a message for API users
st.write(
    "To make API requests, pass the required parameters (`name`, `cgpa`, `goals`, `resume`) via query parameters or form submission."
)
