@echo off
REM Run backend server in development mode

echo Starting TaskFlow Agent Backend...

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please run setup.py first.
    exit /b 1
)

REM Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
