🤖 AI-Generated Academic Support Tools

AI-Generated Academic Support Tools is an AI-powered web application designed to help students with their academic learning and problem-solving. The platform provides assistance with academic questions, mathematics, programming, and file analysis using the Google Gemini API.

The project is built with Python and Flask and provides a simple, responsive, and user-friendly interface for students.

✨ Features
📚 Academic Question Support – Ask questions and receive AI-generated explanations.
🧮 Mathematics Support – Get help solving mathematical problems.
💻 Programming Support – Ask programming questions and get explanations and solutions.
📄 File Analysis – Upload supported files/images for AI-assisted analysis.
🤖 AI-Powered Responses – Uses Google Gemini for intelligent responses.
🌐 Web-Based Interface – Access the application directly through a browser.
⚡ Flask Backend – Lightweight and efficient Python backend.
🛠️ Technologies Used
Python
Flask
Google Gemini API
HTML5
CSS3
JavaScript
SQL
Pillow
Gunicorn
📂 Project Structure
AI-Generated-Academic-Support-Tools/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── HTML files
│
├── static/
│   ├── CSS
│   └── JavaScript
│
├── uploads/
│
└── tests/
🚀 Installation & Setup
1. Clone the Repository
git clone https://github.com/ritam827/AI-Generated-Academic-Support-Tools.git
2. Navigate to the Project
cd AI-Generated-Academic-Support-Tools
3. Create a Virtual Environment
python -m venv .venv
4. Activate the Virtual Environment

Windows:

.venv\Scripts\activate
5. Install Dependencies
pip install -r requirements.txt
🔑 API Configuration

Create a .env file in the project directory:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash

Important: Never upload your API key to GitHub. Make sure .env is included in .gitignore.

▶️ Run the Application
python app.py

The application will normally be available at:

http://127.0.0.1:5000
🌐 Deployment

The application can be deployed as a Flask web service using Render.

Render Start Command
gunicorn app:app
🎯 Project Objective

The main objective of this project is to develop an accessible AI-based academic support platform that helps students understand concepts, solve problems, and receive programming and mathematical assistance through an interactive web application.

🔮 Future Enhancements
👤 User authentication
💬 Chat history
🎤 Voice-based interaction
📖 Personalized learning assistance
📊 Student learning analytics
🧠 Support for additional AI models
📄 Enhanced document processing
👨‍💻 Developer

Ritam Bera

B.Tech CSE (AI & ML)

GitHub:
https://github.com/ritam827

LinkedIn:
https://www.linkedin.com/in/ritam-bera-3a3a75311/

📜 License

This project is developed for educational and academic purposes
