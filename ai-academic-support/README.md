# 🎓 AI-Powered Academic Support and Visual Learning System

## 📋 Project Overview

The **AI-Powered Academic Support and Visual Learning System** is an intelligent web application designed to help students understand academic concepts across multiple subjects. Built as a final-year college project, this platform leverages Google's Gemini AI to provide comprehensive explanations, step-by-step solutions, visual diagrams, and image-based question analysis.

## 🎯 Problem Statement

Students often struggle with complex academic topics and lack access to instant, personalized tutoring. Traditional search engines provide fragmented information, and not every student can afford private tutoring. There is a need for an intelligent, accessible platform that can:

- Explain academic concepts in simple language
- Solve mathematical problems step by step
- Help with programming concepts and code examples
- Analyze handwritten questions and diagrams
- Provide visual representations for better understanding

## 🏆 Objectives

1. Develop an AI-powered question-answering system for academic subjects
2. Implement image-based question analysis for handwritten problems and diagrams
3. Generate visual diagrams automatically to enhance conceptual understanding
4. Create a user-friendly, responsive web interface accessible on all devices
5. Ensure secure handling of API keys and user uploads

## ✨ Features

### A. AI Academic Question Answering
- Ask any academic question across subjects
- Receive structured responses with:
  - Short answer
  - Detailed explanation
  - Step-by-step solution
  - Practical example
  - Important points
  - Related topics

### B. Mathematical Problem Solver
- Input mathematical equations (e.g., "Solve 2x + 5 = 15")
- Get formula/method identification
- Step-by-step calculation walkthrough
- Clear final answer

### C. Programming Question Support
- Ask programming questions (e.g., "Explain Python for loop")
- Receive syntax explanation, code examples, and expected output
- Code displayed in formatted code blocks

### D. Image Question Solver
- Upload handwritten questions, math problems, or diagrams
- Supports PNG, JPG, JPEG, WEBP formats (max 5 MB)
- AI analyzes the image and provides:
  - Content detection
  - Answer and explanation
  - Important concepts
  - Diagram explanation
  - Study tips

### E. Automatic Visual Diagram Generation
- AI generates Mermaid.js diagrams when a topic benefits from visual explanation
- Diagrams rendered directly in the browser
- Supports flowcharts, process diagrams, concept maps, and more
- Optional "View Diagram Code" button

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.x | Backend programming language |
| Flask | Web framework for API and routing |
| HTML5 | Frontend structure |
| CSS3 | Styling and responsive design |
| Vanilla JavaScript | Frontend logic and API communication |
| Google Gemini AI | AI-powered content generation |
| Mermaid.js | Diagram rendering |
| Pillow (PIL) | Image processing |
| python-dotenv | Environment variable management |

## 🏗️ System Architecture

```
┌─────────────┐     HTTP Requests      ┌──────────────┐
│             │ ───────────────────────> │              │
│   Browser   │                         │  Flask App   │
│  (HTML/CSS/ │ <─────────────────────  │  (app.py)    │
│   JS)       │     JSON Responses      │              │
└─────────────┘                         └──────┬───────┘
                                               │
                                               │ API Calls
                                               ▼
                                        ┌──────────────┐
                                        │  Google      │
                                        │  Gemini AI   │
                                        │  API         │
                                        └──────────────┘
```

## 🔄 How the System Works

1. **Student enters a question** in the web interface (text or image)
2. **JavaScript sends the request** to the Flask backend using `fetch()`
3. **Flask processes the request** and sends it to the Google Gemini API
4. **Gemini AI generates a response** with structured content and optional Mermaid diagram code
5. **Flask returns the response** as JSON to the frontend
6. **JavaScript renders the response** in visually attractive cards
7. **Mermaid.js renders any diagrams** in the browser

## 📁 Folder Structure

```
ai-academic-support/
│
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .env                    # Actual environment variables (not committed)
├── .gitignore              # Git ignore rules
├── README.md               # This file
│
├── templates/
│   └── index.html          # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css       # Stylesheet
│   └── js/
│       └── script.js       # Frontend JavaScript
│
└── uploads/                # Temporary upload directory
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- A Google Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/apikey))

### Step 1: Clone or Download the Project

```bash
cd ai-academic-support
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure the Gemini API Key

Create a `.env` file in the project root:

```bash
copy .env.example .env
```

Edit the `.env` file and replace `your_api_key_here` with your actual Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

> ⚠️ **IMPORTANT:** Never share your API key or commit it to version control.

### Step 6: Run the Application

```bash
python app.py
```

### Step 7: Open in Browser

Navigate to:

```
http://127.0.0.1:5000
```

## 📖 How to Use

### Asking a Text Question
1. Scroll to the "Ask Your Question" section
2. Type your question in the text area (or click an example button)
3. Click "Ask AI"
4. Wait for the AI to generate a response
5. View the answer in organized cards (Short Answer, Explanation, Steps, etc.)

### Uploading an Image
1. Scroll to the "Image Question Solver" section
2. Click the upload area or drag and drop an image
3. Preview the image
4. Click "Analyze Image"
5. View the AI's analysis alongside the uploaded image

### Viewing Diagrams
- When a topic benefits from visual representation, a diagram is automatically generated
- The "Visual Diagram" card appears with the rendered diagram
- Click "View Diagram Code" to see the Mermaid source code

## 🧪 Testing

### Test Checklist

| # | Test | Expected Result |
|---|------|----------------|
| 1 | Open homepage | Page loads with all sections visible |
| 2 | Ask "Explain photosynthesis" | AI returns structured answer |
| 3 | Ask "Solve 2x + 5 = 15" | Step-by-step math solution |
| 4 | Ask "Explain Python for loop" | Code example in formatted block |
| 5 | Ask "Explain the water cycle" | Answer + Mermaid diagram |
| 6 | Upload a math problem image | Image analysis + solution |
| 7 | Upload invalid file type | Friendly error message |
| 8 | Submit empty question | "Please enter a question" message |
| 9 | Test mobile layout | Responsive design works |
| 10 | Test without API key | Configuration error message |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Gemini API key is not configured" | Create a `.env` file with your `GEMINI_API_KEY` |
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` in the virtual environment |
| Port 5000 already in use | Change the port in `app.py` or stop the other process |
| Image upload fails | Check file format (PNG/JPG/JPEG/WEBP) and size (< 5 MB) |
| Mermaid diagram not rendering | Check browser console for JavaScript errors; try refreshing |
| "Unable to connect to the server" | Make sure Flask is running on port 5000 |

## ⚠️ Limitations

1. Requires an active internet connection for Gemini AI API calls
2. Response quality depends on the Gemini AI model's capabilities
3. Image analysis accuracy varies with image quality
4. Mermaid diagram generation is not guaranteed for every topic
5. The system does not store conversation history
6. Large or complex diagrams may not render perfectly

## 🚀 Future Enhancements

1. **User Authentication** — Login system with personal question history
2. **Chat Mode** — Conversational follow-up questions
3. **Subject Selection** — Dedicated modes for different subjects
4. **PDF Export** — Download answers as PDF documents
5. **Voice Input** — Ask questions using speech
6. **Quiz Generator** — Auto-generate quizzes from topics
7. **Dark Mode** — Toggle between light and dark themes
8. **Multi-language Support** — Support for multiple languages
9. **Offline Mode** — Cache common answers for offline access
10. **Performance Analytics** — Track learning progress

## 📝 Conclusion

The AI-Powered Academic Support and Visual Learning System demonstrates the practical application of artificial intelligence in education. By combining Google's Gemini AI with modern web technologies, this project creates an accessible, intelligent tutoring platform that can help students across diverse academic subjects. The system's ability to generate visual diagrams, analyze images, and provide structured explanations makes it a valuable tool for enhancing the learning experience.

---

**Built with ❤️ for learning** | Final Year Project
