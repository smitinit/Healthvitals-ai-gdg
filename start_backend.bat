@echo off
cd backend
echo Starting backend server...

REM Check if venv exists and activate it
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your Google API key:
    echo GOOGLE_API_KEY=your_api_key_here
    exit /b 1
)

echo Starting Flask application...
python app.py 