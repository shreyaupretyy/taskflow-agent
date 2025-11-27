# TaskFlow Agent Backend

Backend API server for TaskFlow Agent platform.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python migrate.py
```

6. Start server:
```bash
python -m uvicorn app.main:app --reload
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
