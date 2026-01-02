from flask import Flask, request, jsonify, render_template
from google import genai
from pypdf import PdfReader
import json
import os

app = Flask(__name__)

# Replace with your actual API key
client = genai.Client(api_key="AIzaSyCmqpexhnBhVKKXqy0CnGTFKbz3oMg_Jg4")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

@app.route('/')
def index():
    return render_template('Ats.html')

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        resume_text = extract_text_from_pdf(file)

        prompt = f"""
        You are an expert ATS (Applicant Tracking System) scanner. 
        Analyze the resume text below for a job application.
        
        Return a strict JSON object with this exact structure:
        {{
            "score": <integer 0-100>,
            "advantages": [
                "Short point on strength (max 8 words)",
                "Short point on strength (max 8 words)",
                "Short point on strength (max 8 words)"
            ],
            "improvements": [
                "Short fix recommendation (max 8 words)",
                "Short fix recommendation (max 8 words)",
                "Short fix recommendation (max 8 words)"
            ]
        }}
        
        Keep the points concise so they fit in a UI column.
        
        RESUME TEXT:
        {resume_text}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        return jsonify(json.loads(response.text))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080, debug=True)
