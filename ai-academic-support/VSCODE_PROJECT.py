"""
AI-Powered Academic Support and Visual Learning System
Flask Backend - Main Application

This is the main server file that handles:
- Serving the frontend
- Processing academic questions via Gemini AI
- Analyzing uploaded images via Gemini AI
- Generating Mermaid.js diagram code for visual learning
"""

import os
import json
import re
import traceback
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
import PIL.Image

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Load environment variables from .env file (for local development)
load_dotenv()

app = Flask(__name__)

# Maximum upload size: 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Gemini model to use (current multimodal model)
GEMINI_MODEL = "gemini-2.0-flash"

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def get_gemini_client():
    """Create and return a Gemini API client. Raises an error if API key is missing."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY.")
    return genai.Client(api_key=api_key)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_json_from_response(text):
    """
    Extract a JSON object from the AI response text.
    Handles cases where the AI wraps JSON in markdown code fences.
    """
    # Try to find JSON inside ```json ... ``` code fences
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def build_question_prompt(question):
    """Build the prompt for academic question answering."""
    return f"""You are an AI academic tutor helping students learn. 
A student has asked the following question:

"{question}"

Please provide a comprehensive, student-friendly answer in the following JSON format. 
Return ONLY valid JSON, no other text before or after.

{{
    "short_answer": "A brief 1-2 sentence answer",
    "detailed_explanation": "A clear, detailed explanation using simple language suitable for students. Use paragraphs for readability.",
    "step_by_step": "If the question involves a process, calculation, or procedure, explain it step-by-step as a numbered list. If steps are not applicable, write 'Not applicable for this topic.'",
    "example": "A practical, easy-to-understand example. For programming questions, include code with comments. For math, show a worked example.",
    "important_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
    "related_topics": ["Related Topic 1", "Related Topic 2", "Related Topic 3"],
    "mermaid_diagram": "If this topic can be explained with a flowchart, process diagram, or concept map, provide valid Mermaid.js diagram code (e.g., graph TD, flowchart LR, etc.). Use simple labels without special characters. If a diagram is not useful for this topic, set this to null."
}}

Important rules:
- For programming questions, include properly formatted code examples in the example field.
- For math questions, show the complete solution with all steps.
- Keep language simple and student-friendly.
- The mermaid_diagram field should contain ONLY valid Mermaid.js syntax or null.
- Do NOT wrap the Mermaid code in code fences inside the JSON.
- Return ONLY the JSON object, nothing else."""


def build_image_prompt():
    """Build the prompt for image-based question analysis."""
    return """You are an AI academic tutor. A student has uploaded an image containing an academic question, problem, or diagram.

Please analyze the image carefully and provide a comprehensive response in the following JSON format.
Return ONLY valid JSON, no other text before or after.

{
    "detected_content": "Describe what you see in the image - the question, problem, diagram, or content shown.",
    "answer": "Provide the answer to the question or problem shown in the image.",
    "step_by_step": "Explain the solution or analysis step-by-step as a numbered list.",
    "important_concepts": ["Concept 1", "Concept 2", "Concept 3"],
    "diagram_explanation": "If the image contains a diagram, explain its important parts and what they represent. If no diagram is present, write 'No diagram detected in the image.'",
    "student_tip": "Give one useful study or learning tip related to this topic.",
    "mermaid_diagram": "If this topic benefits from a visual diagram, provide valid Mermaid.js code. Otherwise set to null."
}

Important rules:
- Be thorough in analyzing the image content.
- If you see handwritten text, transcribe it accurately.
- For math problems, show complete step-by-step solutions.
- Keep language simple and student-friendly.
- Return ONLY the JSON object, nothing else."""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route('/')
def home():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle academic question requests."""
    try:
        # Get the question from the request
        data = request.get_json()
        if not data or not data.get('question', '').strip():
            return jsonify({'error': 'Please enter a question.'}), 400

        question = data['question'].strip()

        # Get the Gemini client
        try:
            client = get_gemini_client()
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

        # Send to Gemini API
        prompt = build_question_prompt(question)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        # Check for empty response
        if not response or not response.text:
            return jsonify({'error': 'No answer was generated. Please try another question.'}), 500

        # Parse the JSON response
        result = extract_json_from_response(response.text)
        if not result:
            # If JSON parsing fails, return a basic response
            return jsonify({
                'short_answer': response.text[:200],
                'detailed_explanation': response.text,
                'step_by_step': 'Not applicable.',
                'example': 'Not available.',
                'important_points': ['See the detailed explanation above.'],
                'related_topics': [],
                'mermaid_diagram': None
            })

        return jsonify(result)

    except Exception as e:
        print(f"Error in /ask: {traceback.format_exc()}")
        return jsonify({'error': 'AI service is temporarily unavailable. Please try again.'}), 500


@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Handle image upload and analysis."""
    try:
        # Check if a file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file was uploaded.'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file was selected.'}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Please upload a valid PNG, JPG, JPEG, or WEBP image.'}), 400

        # Save the file temporarily
        filename = 'uploaded_image.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Check file size (double-check after save)
        file_size = os.path.getsize(filepath)
        if file_size > 5 * 1024 * 1024:
            os.remove(filepath)
            return jsonify({'error': 'Image size must be less than 5 MB.'}), 400

        # Get the Gemini client
        try:
            client = get_gemini_client()
        except ValueError as e:
            os.remove(filepath)
            return jsonify({'error': str(e)}), 500

        # Open image with PIL
        image = PIL.Image.open(filepath)

        # Send to Gemini for analysis
        prompt = build_image_prompt()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[image, prompt]
        )

        # Clean up uploaded file
        try:
            image.close()
            os.remove(filepath)
        except OSError:
            pass

        # Check for empty response
        if not response or not response.text:
            return jsonify({'error': 'No answer was generated. Please try uploading a clearer image.'}), 500

        # Parse the JSON response
        result = extract_json_from_response(response.text)
        if not result:
            return jsonify({
                'detected_content': 'Image analyzed.',
                'answer': response.text,
                'step_by_step': 'See the answer above.',
                'important_concepts': [],
                'diagram_explanation': 'Not available.',
                'student_tip': 'Try asking more specific questions for better results.',
                'mermaid_diagram': None
            })

        return jsonify(result)

    except Exception as e:
        print(f"Error in /analyze-image: {traceback.format_exc()}")
        return jsonify({'error': 'AI service is temporarily unavailable. Please try again.'}), 500


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'Image size must be less than 5 MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Page not found.'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'An internal server error occurred.'}), 500


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  AI-Powered Academic Support System")
    print("  Starting server...")
    print("=" * 60)

    # Check if API key is configured
    if not os.environ.get('GEMINI_API_KEY'):
        print("\n  WARNING: GEMINI_API_KEY is not set!")
        print("  The AI features will not work without it.")
        print("  Create a .env file with: GEMINI_API_KEY=your_key_here")
        print("  Or set it as an environment variable.\n")
    else:
        print("\n  Gemini API key: Configured ✓\n")

    print(f"  Open http://127.0.0.1:5000 in your browser")
    print("=" * 60 + "\n")

    app.run(debug=True, host='127.0.0.1', port=5000)
