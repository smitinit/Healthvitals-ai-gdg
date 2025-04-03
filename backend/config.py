import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://healthvitals-ai-43006.web.app').split(',')
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "100 per minute"
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    } 