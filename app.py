import streamlit as st
import google.generativeai as genai
import PyPDF2
from io import BytesIO
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from starlette.middleware.wsgi import WSGIMiddleware
import uvicorn

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

# Streamlit visual testing interface
st.title("Career Guidance API")

if st.checkbox("Test the API Locally"):
    name = st.text_input("Name")
    cgpa = st.text_input("CGPA")
    goals = st.text_area("Career Goals")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if st.button("Generate Guidance"):
        try:
            if not name or not cgpa or not uploaded_file or not goals:
                st.error("All fields are required!")
            else:
                resume_text = process_resume(uploaded_file)
                input_data = (
                    f"Name: {name}\n"
                    f"CGPA: {cgpa}\n"
                    f"Resume: {resume_text}\n"
                    f"Goals: {goals}\n"
                    "Provide personalized career guidance based on this information."
                )
                response = model.generate_content(input_data)
                st.success("Generated Output:")
                st.text_area("Output", response.text, height=300)
        except Exception as e:
            st.error(f"Error: {e}")

# FastAPI backend for integration with React
app = FastAPI()

@app.post("/generate")
async def generate_api(
    name: str = Form(...),
    cgpa: str = Form(...),
    goals: str = Form(...),
    resume: UploadFile = File(...),
):
    try:
        if not resume.filename.endswith(".pdf"):
            return JSONResponse(
                status_code=400, content={"error": "Resume must be a PDF file"}
            )

        resume_text = process_resume(BytesIO(await resume.read()))
        input_data = (
            f"Name: {name}\n"
            f"CGPA: {cgpa}\n"
            f"Resume: {resume_text}\n"
            f"Goals: {goals}\n"
            "Provide personalized career guidance based on this information."
        )
        response = model.generate_content(input_data)
        return {"output": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Mount FastAPI within Streamlit
st.write("API is ready to accept POST requests at `/generate`.")
st.write("Use the following endpoint in your React app:")
st.code("http://<your-streamlit-domain>/generate", language="bash")

# Run FastAPI server inside Streamlit
st.experimental_singleton(lambda: uvicorn.run(app, host="0.0.0.0", port=8501))
