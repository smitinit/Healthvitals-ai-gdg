# HealthVitals AI Backend

This is the backend service for the HealthVitals AI application, providing symptom analysis using the Gemini API.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your Gemini API key to the `.env` file

4. Run the application:
```bash
flask run
```

The server will start at `http://localhost:5000`

## API Endpoints

### POST /api/analyze-symptoms
Analyzes symptoms and provides medical recommendations using the Gemini API.

Request body:
```json
{
    "symptoms": [
        {
            "name": "Symptom name",
            "severity": 7,
            "duration": "2 days"
        }
    ],
    "age": "25",
    "gender": "Male",
    "medicalHistory": ["Condition 1", "Condition 2"]
}
```

## Security Considerations

1. API Key Protection:
   - Never commit the `.env` file containing your API key
   - Use environment variables for sensitive data
   - Rotate API keys regularly

2. Input Validation:
   - All inputs are validated before processing
   - Rate limiting is implemented to prevent abuse

3. CORS:
   - CORS is enabled only for the frontend domain
   - Configure allowed origins in production

## Deployment

For production deployment:
1. Set `FLASK_ENV=production`
2. Use a production-grade server (Gunicorn)
3. Enable HTTPS
4. Set up proper logging
5. Configure proper CORS settings
