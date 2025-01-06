from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import PyPDF2

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key="AIzaSyAOw3Y-QYSQ1uq8XzcEdxdUS9tOHWcSRZw")
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def home():
    return jsonify({"message": "API is running. Use the /generate endpoint to generate output."}), 200

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Retrieve form data
        name = request.form.get('name')
        cgpa = request.form.get('cgpa')
        resume_file = request.files.get('resume')
        goals = request.form.get('goals')  # Retrieve the goals input

        # Validate inputs
        if not name or not cgpa or not resume_file or not goals:
            return jsonify({"error": "Missing required fields (name, cgpa, resume, or goals)"}), 400

        # Process the uploaded resume (PDF format)
        resume_content = ""
        if resume_file.filename.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(resume_file)
                for page in pdf_reader.pages:
                    resume_content += page.extract_text()
            except Exception as e:
                print("PDF Reading Error:", str(e))  # Log PDF reading error
                return jsonify({"error": "Failed to process the uploaded PDF"}), 500
        else:
            return jsonify({"error": "Unsupported file format. Please upload a PDF."}), 400

        # Prepare input for the Gemini API
        input_data = (
            f"Name: {name}\n"
            f"CGPA: {cgpa}\n"
            f"Resume: {resume_content}\n"
            f"Goals: {goals}\n"
            "Provide personalized career guidance based on this information."
        )
        print("Input Data for Gemini API:", input_data)

        # Call the Gemini API
        try:
            response = model.generate_content(input_data)  # Correct method call
            print("API Response:", response)  # Debugging
            generated_text = response.text  # Extract the generated text
        except Exception as e:
            print("Gemini API Error:", str(e))  # Log Gemini API error
            return jsonify({"error": "Failed to process data with the Gemini API"}), 500

        # Return the generated output
        return jsonify({"output": generated_text}), 200

    except Exception as e:
        # Handle unexpected errors
        print("Unexpected Error:", str(e))  # Log unexpected error
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
