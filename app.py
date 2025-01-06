import streamlit as st
import google.generativeai as genai
import PyPDF2
from io import BytesIO

# Configure Gemini API
genai.configure(api_key="AIzaSyAOw3Y-QYSQ1uq8XzcEdxdUS9tOHWcSRZw")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to process API requests
def process_request(name, cgpa, resume_file, goals):
    # Process the uploaded resume (PDF format)
    resume_content = ""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(resume_file))
        for page in pdf_reader.pages:
            resume_content += page.extract_text()
    except Exception as e:
        return {"error": "Failed to process the uploaded PDF: " + str(e)}, 500

    # Prepare input for the Gemini API
    input_data = (
        f"Name: {name}\n"
        f"CGPA: {cgpa}\n"
        f"Resume: {resume_content}\n"
        f"Goals: {goals}\n"
        "Provide personalized career guidance based on this information."
    )

    # Call the Gemini API
    try:
        response = model.generate_content(input_data)
        generated_text = response.text
        return {"output": generated_text}, 200
    except Exception as e:
        return {"error": "Failed to process data with the Gemini API: " + str(e)}, 500

# Streamlit app configuration
st.set_page_config(page_title="Streamlit API Endpoint", layout="wide")
st.title("Streamlit API Endpoint")

# Input Fields
st.header("Provide Your Details")
name = st.text_input("Name", help="Enter your full name")
cgpa = st.text_input("CGPA", help="Enter your CGPA (e.g., 3.8)")
resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf", help="Upload your resume in PDF format")
goals = st.text_area("Career Goals", help="Describe your career aspirations and goals")

# Button to trigger API call
if st.button("Generate Guidance"):
    if not name or not cgpa or not resume_file or not goals:
        st.error("Please fill out all required fields (Name, CGPA, Resume, and Goals).")
    else:
        file_content = resume_file.read() if resume_file else None
        result, status_code = process_request(name, cgpa, file_content, goals)

        if status_code == 200:
            st.success("Output Generated Successfully")
            st.text_area("Generated Output", result["output"], height=300)
        else:
            st.error(result["error"])

# API Endpoint Information
st.sidebar.header("API Usage Instructions")
st.sidebar.write("This app acts as an API endpoint.")
st.sidebar.write("1. Deploy this app using Streamlit Cloud or a similar service.")
st.sidebar.write("2. Use the app's URL in your React frontend to send inputs and receive outputs.")
st.sidebar.write("3. Ensure all inputs (Name, CGPA, Resume, Goals) are provided correctly.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Developed with ❤️ using Streamlit and OpenAI's Generative AI.")
