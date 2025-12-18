# HealthVitals AI

HealthVitals AI is an advanced health monitoring and symptom analysis application powered by Google's Gemini AI. It provides users with medical insights, symptom analysis, and personalized health recommendations.

## 🚀 Features

- **AI-Powered Symptom Analysis**: Detailed analysis of symptoms using Gemini 1.5 Pro to identify possible conditions.
- **Quick Analysis**: Fast, anonymous symptom checking for immediate insights.
- **Comprehensive Reports**: Generate detailed and overview PDF reports of your health analysis.
- **Personalized Recommendations**: Tailored advice including:
    - Medical condition probabilities
    - Recommended actions and preventive measures
    - Diet plans (including specific Indian meal recommendations)
    - Exercise plans based on lifestyle and health status
    - Ayurvedic medication suggestions
- **Secure Authentication**: User management powered by Clerk.
- **Privacy Focused**: IP hashing for anonymous usage and secure data handling.

## 🛠️ Tech Stack

### Frontend
- **React 19**: Modern UI library with Vite for fast tooling.
- **TypeScript**: Type-safe development.
- **Tailwind CSS 4**: Utility-first styling.
- **Shadcn UI**: Accessible and customizable UI components.
- **Framer Motion**: Smooth animations.
- **Clerk**: Authentication and user management.

### Backend
- **Flask**: Lightweight Python web server.
- **Google Gemini API**: Advanced LLM for medical reasoning.
- **ReportLab**: PDF generation engine.
- **Flask-CORS**: Cross-Origin Resource Sharing handling.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/) (v3.9 or higher)
- [Gemini API Key](https://ai.google.dev/)

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/healthvitals-ai-gdg.git
cd healthvitals-ai-gdg
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend` directory with your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Start the Backend:**
```bash
python app.py
# The server will start at http://localhost:5000
```

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory.

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at `http://localhost:5173` (or the port shown in your terminal).

## 📖 Usage

1.  **Sign Up/Login**: Create an account using the Clerk authentication flow.
2.  **Input Details**: Enter your age, gender, biometrics, medical history, and current symptoms.
3.  **Get Analysis**: Submit the form to receive an AI-generated analysis of your condition.
4.  **Download Reports**: Generate and download PDF reports for your records or to share with a doctor.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  **Fork the repository**.
2.  **Create a new branch** (`git checkout -b feature/YourFeatureName`).
3.  **Make your changes** and commit them (`git commit -m 'Add new feature'`).
4.  **Push to the branch** (`git push origin feature/YourFeatureName`).
5.  **Open a Pull Request**.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

> **Disclaimer**: HealthVitals AI is an AI-powered tool for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
