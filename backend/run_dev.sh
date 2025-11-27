#!/bin/bash

# Run backend server in development mode

echo "Starting TaskFlow Agent Backend..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
