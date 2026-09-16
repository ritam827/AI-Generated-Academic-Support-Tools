"""
AI-Powered Academic Support and Visual Learning System
Flask Backend - Main Application

This is the main server file that handles:
- Serving the frontend
- Processing academic questions via Gemini AI
- Analyzing uploaded images via Gemini AI
- Generating Mermaid.js diagram code for visual learning
- Searching Wikipedia for quick facts and references
"""

import json
import os
import re
import traceback
import urllib.parse
import urllib.request
import urllib.error

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
import PIL.Image

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATE_PROJECT_DIR = os.path.join(BASE_DIR, 'ai-academic-support')
PROJECT_DIR = CANDIDATE_PROJECT_DIR if os.path.isdir(CANDIDATE_PROJECT_DIR) else BASE_DIR

for env_path in [
    os.path.join(PROJECT_DIR, '.env'),
    os.path.join(BASE_DIR, '.env'),
    os.path.join(os.path.dirname(PROJECT_DIR), '.env')
]:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=False)

app = Flask(__name__, template_folder=os.path.join(PROJECT_DIR, 'templates'), static_folder=os.path.join(PROJECT_DIR, 'static'))

# Maximum upload size: 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# Upload folder
UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed study-file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}

# Gemini model to use (current multimodal model)
DEFAULT_GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
GEMINI_MODEL = DEFAULT_GEMINI_MODEL
FALLBACK_GEMINI_MODELS = [
    DEFAULT_GEMINI_MODEL
]

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def get_gemini_client():
    """Create and return a Gemini API client. Raises an error if API key is missing."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('Gemini API key is not configured. Please set GEMINI_API_KEY.')
    return genai.Client(api_key=api_key)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_json_from_response(text):
    """Extract a JSON object from the AI response text."""
    if not text:
        return None

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

\"{question}\"

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
    """Build the prompt for image or PDF-based question analysis."""
    return """You are an AI academic tutor. A student has uploaded an image or PDF containing an academic question, problem, diagram, or textbook content.

Please analyze the image carefully and provide a comprehensive response in the following JSON format.
Return ONLY valid JSON, no other text before or after.

{
    "detected_content": "Describe what you see in the image - the question, problem, diagram, or content shown.",
    "answer": "Provide the answer to the question or problem shown in the image.",
    "step_by_step": "Explain the solution or analysis step-by-step as a numbered list.",
    "important_concepts": ["Concept 1", "Concept 2", "Concept 3"],
    "diagram_explanation": "If the image contains a diagram, explain its important parts and what they represent. If no diagram is present, write 'No diagram detected in the image.'",
    "student_tip": "Give one useful study or learning tip related to this topic.",
    "source_links": ["https://www.google.com/search?q=...", "https://www.google.com/search?q=..."],
    "mermaid_diagram": "If this topic benefits from a visual diagram, provide valid Mermaid.js code. Otherwise set to null."
}

Important rules:
- Be thorough in analyzing the image content.
- If you see handwritten text, transcribe it accurately.
- For math problems, show complete step-by-step solutions.
- Keep language simple and student-friendly.
- The source_links field must contain 2 to 5 direct Google search URLs relevant to the topic.
- Return ONLY the JSON object, nothing else."""


def fetch_wikipedia_summary(query):
    """Fetch a Wikipedia summary, including when the input is a full question."""
    topic = (query or '').strip()
    if not topic:
        raise ValueError('Please enter a topic to search.')

    headers = {'User-Agent': 'AI Academic Support/1.0 (academic helper)'}
    cleaned_topic = re.sub(
        r'^(what is|what are|who is|who was|explain|define|tell me about)\s+',
        '', topic, flags=re.IGNORECASE
    )
    cleaned_topic = re.sub(
        r'\s+(in detail|with examples?|and examples?|step by step|briefly)\s*$',
        '', cleaned_topic, flags=re.IGNORECASE
    ).strip(' ?!.')
    cleaned_topic = re.split(r'\s*[?!.,;]\s*(?:explain|show|give|with)\b', cleaned_topic, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    search_topics = [topic]
    if cleaned_topic and cleaned_topic.casefold() != topic.casefold():
        search_topics.append(cleaned_topic)

    title = None
    for search_topic in search_topics:
        search_url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({
            'action': 'opensearch',
            'search': search_topic,
            'limit': 1,
            'namespace': 0,
            'format': 'json'
        })
        try:
            with urllib.request.urlopen(urllib.request.Request(search_url, headers=headers), timeout=8) as response:
                search_payload = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError('Wikipedia is taking too long to respond. Please try again.') from exc

        titles = search_payload[1] if isinstance(search_payload, list) and len(search_payload) > 1 else []
        if titles:
            title = titles[0]
            break

    if not title:
        raise LookupError(f'No Wikipedia article was found for "{topic}".')

    encoded_title = urllib.parse.quote(title.replace(' ', '_'), safe='')
    summary_url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}'
    try:
        with urllib.request.urlopen(urllib.request.Request(summary_url, headers=headers), timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise LookupError(f'No Wikipedia article was found for "{topic}".') from exc
        raise RuntimeError('Wikipedia could not load that article. Please try again.') from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError('Wikipedia is taking too long to respond. Please try again.') from exc

    if payload.get('type') == 'https://mediawiki.org/wiki/HyperSwitch/errors/not_found':
        raise LookupError(f'No Wikipedia article was found for "{topic}".')

    title = payload.get('title') or title or topic
    summary = payload.get('extract') or 'No summary is available for this topic yet.'
    description = payload.get('description') or ''
    content_urls = payload.get('content_urls') or {}
    desktop = content_urls.get('desktop') or {}
    wiki_url = desktop.get('page') or f'https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(" ", "_"))}'

    return {
        'title': title,
        'description': description,
        'summary': summary,
        'url': wiki_url
    }


def normalize_source_links(raw_links):
    """Ensure answer source links are a clean list of Google search URLs."""
    if not raw_links:
        return []
    if isinstance(raw_links, str):
        raw_links = [raw_links]

    cleaned = []
    for item in raw_links:
        if not item:
            continue
        text = str(item).strip()
        if text.startswith('http://') or text.startswith('https://'):
            cleaned.append(text)
        elif text.startswith('www.'):
            cleaned.append('https://' + text)
    return cleaned[:5]


def build_google_source_links(topic):
    """Build dependable Google research links when AI returns no sources."""
    search_topic = (topic or 'academic topic').strip()
    queries = [
        search_topic,
        f'{search_topic} explanation',
        f'{search_topic} examples'
    ]
    return [
        'https://www.google.com/search?' + urllib.parse.urlencode({'q': query})
        for query in queries
    ]


def build_standard_diagram(topic):
    """Create a safe baseline diagram when Gemini omits a diagram."""
    label = re.sub(r'[^A-Za-z0-9 ]+', ' ', str(topic or 'Academic topic'))
    label = re.sub(r'\s+', ' ', label).strip()[:45] or 'Academic topic'
    return f'''flowchart TD
    A["Question"] --> B["{label}"]
    B --> C["Core idea"]
    C --> D["Key points"]
    D --> E["Example or method"]
    E --> F["Conclusion"]'''


def generate_with_fallback(client, prompt, image=None, uploaded_file=None):
    """Try the preferred Gemini model and fall back for deprecated names."""
    last_error = None
    for model_name in FALLBACK_GEMINI_MODELS:
        try:
            if uploaded_file is not None:
                return client.models.generate_content(model=model_name, contents=[uploaded_file, prompt])
            if image is None:
                return client.models.generate_content(model=model_name, contents=prompt)
            return client.models.generate_content(model=model_name, contents=[image, prompt])
        except Exception as exc:
            last_error = exc
            if (
                '404' not in str(exc)
                and 'NOT_FOUND' not in str(exc)
                and not is_quota_error(exc)
            ):
                raise

    if last_error is not None:
        raise last_error
    raise RuntimeError('No Gemini model was available for this request.')


def is_quota_error(exc):
    """Identify Gemini quota and rate-limit failures without exposing raw traces."""
    message = str(exc).upper()
    return '429' in message or 'RESOURCE_EXHAUSTED' in message or 'QUOTA' in message


def quota_error_response():
    """Return a concise response for exhausted Gemini quotas."""
    return jsonify({
        'error': 'Gemini API quota is temporarily exhausted. Please wait about one minute and try again, or use a Gemini API key with available billing/quota.',
        'code': 'QUOTA_EXHAUSTED'
    }), 429


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route('/')
def home():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/wiki', methods=['POST'])
def wikipedia_search():
    """Search Wikipedia for a quick summary."""
    try:
        data = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        if not query:
            return jsonify({'error': 'Please enter a topic to search on Wikipedia.'}), 400

        result = fetch_wikipedia_summary(query)
        return jsonify(result)
    except LookupError as exc:
        return jsonify({'error': str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503
    except Exception:
        print(f'Error in /wiki: {traceback.format_exc()}')
        return jsonify({'error': 'Wikipedia search failed. Please try another topic.'}), 502


@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle academic question requests."""
    try:
        data = request.get_json(silent=True) or {}
        if not data or not data.get('question', '').strip():
            return jsonify({'error': 'Please enter a question.'}), 400

        question = data['question'].strip()

        try:
            client = get_gemini_client()
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 500

        prompt = build_question_prompt(question)
        response = generate_with_fallback(client, prompt)

        if not response or not getattr(response, 'text', None):
            return jsonify({'error': 'No answer was generated. Please try another question.'}), 500

        result = extract_json_from_response(response.text)
        if not result:
            return jsonify({
                'short_answer': response.text[:200],
                'detailed_explanation': response.text,
                'step_by_step': 'Not applicable.',
                'example': 'Not available.',
                'important_points': ['See the detailed explanation above.'],
                'related_topics': [],
                'source_links': build_google_source_links(question),
                'mermaid_diagram': build_standard_diagram(question)
            })

        if 'source_links' not in result:
            result['source_links'] = build_google_source_links(question)
        result['source_links'] = normalize_source_links(result.get('source_links'))
        if not result['source_links']:
            result['source_links'] = build_google_source_links(question)
        if not isinstance(result.get('mermaid_diagram'), str) or not result['mermaid_diagram'].strip():
            result['mermaid_diagram'] = build_standard_diagram(question)
        return jsonify(result)

    except Exception as exc:
        if is_quota_error(exc):
            return quota_error_response()
        print(f'Error in /ask: {traceback.format_exc()}')
        message = str(exc).strip() or 'AI service is temporarily unavailable. Please try again.'
        return jsonify({'error': message}), 500


@app.route('/analyze-file', methods=['POST'])
def analyze_file():
    """Analyze an uploaded image or PDF with Gemini."""
    filepath = None
    remote_file = None
    try:
        file_key = 'file' if 'file' in request.files else 'image'
        if file_key not in request.files:
            return jsonify({'error': 'No image or PDF file was uploaded.'}), 400

        file = request.files[file_key]
        if file.filename == '':
            return jsonify({'error': 'No file was selected.'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Please upload a PNG, JPG, JPEG, WEBP, or PDF file.'}), 400

        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = 'uploaded_study_file.' + extension
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        file_size = os.path.getsize(filepath)
        if file_size > 5 * 1024 * 1024:
            os.remove(filepath)
            return jsonify({'error': 'File size must be less than 5 MB.'}), 400

        try:
            client = get_gemini_client()
        except ValueError as exc:
            os.remove(filepath)
            return jsonify({'error': str(exc)}), 500

        if extension == 'pdf':
            remote_file = client.files.upload(file=filepath)
            response = generate_with_fallback(client, build_image_prompt(), uploaded_file=remote_file)
        else:
            image = PIL.Image.open(filepath)
            response = generate_with_fallback(client, build_image_prompt(), image=image)
            image.close()

        try:
            os.remove(filepath)
        except OSError:
            pass

        if remote_file is not None:
            try:
                client.files.delete(name=remote_file.name)
            except Exception:
                pass

        if not response or not getattr(response, 'text', None):
            return jsonify({'error': 'No answer was generated. Please try uploading a clearer image.'}), 500

        result = extract_json_from_response(response.text)
        if not result:
            return jsonify({
                'detected_content': 'File analyzed.',
                'answer': response.text,
                'step_by_step': 'See the answer above.',
                'important_concepts': [],
                'diagram_explanation': 'Not available.',
                'student_tip': 'Try asking more specific questions for better results.',
                'source_links': build_google_source_links('academic study topic'),
                'mermaid_diagram': build_standard_diagram('Uploaded academic file')
            })

        if 'source_links' not in result:
            result['source_links'] = build_google_source_links(result.get('detected_content') or 'academic study topic')
        result['source_links'] = normalize_source_links(result.get('source_links'))
        if not result['source_links']:
            result['source_links'] = build_google_source_links(result.get('detected_content') or 'academic study topic')
        if not isinstance(result.get('mermaid_diagram'), str) or not result['mermaid_diagram'].strip():
            result['mermaid_diagram'] = build_standard_diagram(result.get('detected_content') or 'Uploaded academic file')
        return jsonify(result)

    except Exception as exc:
        if is_quota_error(exc):
            return quota_error_response()
        print(f'Error in /analyze-file: {traceback.format_exc()}')
        message = str(exc).strip() or 'File analysis is temporarily unavailable. Please try again.'
        return jsonify({'error': message}), 500


@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Keep the original image endpoint compatible with existing clients."""
    return analyze_file()


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
    print('\n' + '=' * 60)
    print('  AI-Powered Academic Support System')
    print('  Starting server...')
    print('=' * 60)

    if not os.environ.get('GEMINI_API_KEY'):
        print('\n  WARNING: GEMINI_API_KEY is not set!')
        print('  The AI features will not work without it.')
        print('  Create a .env file with: GEMINI_API_KEY=your_key_here')
        print('  Or set it as an environment variable.\n')
    else:
        print('\n  Gemini API key: Configured ✓\n')

    print('  Open http://127.0.0.1:5000 in your browser')
    print('=' * 60 + '\n')

    app.run(debug=True, host='127.0.0.1', port=5000)
