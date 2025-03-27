@echo off
cd frontend
echo Starting frontend server...

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    npm install
)

echo Starting Vite development server...
npm run dev 