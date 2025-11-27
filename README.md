# TaskFlow Agent

> AI-Powered Agent Platform for Business Automation

An intelligent AI agent platform that provides pre-built AI agents for common business tasks including email analysis, content generation, data analysis, code review, customer support, and meeting notes.

[![GitHub](https://img.shields.io/badge/GitHub-TaskFlow_Agent-blue?logo=github)](https://github.com/shreyaupretyy/taskflow-agent)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

TaskFlow Agent simplifies business automation by providing ready-to-use AI agents powered by Ollama and LLaMA 3.2. No workflow building required - just select an agent, provide your input, and get instant AI-generated results.

## Features

### Pre-Built AI Agents

- **Email Summarizer** - Analyze emails and extract key information, action items, and priorities
- **Content Generator** - Create professional content including articles, blogs, and marketing copy
- **Data Analyzer** - Analyze data and provide insights, patterns, and recommendations
- **Code Reviewer** - Review code and provide corrected versions with fixes
- **Customer Support** - Generate professional customer support responses
- **Meeting Notes** - Convert meeting transcripts into structured notes with action items

### Key Capabilities

- Real AI processing with Ollama (LLaMA 3.2)
- Clean, professional UI without distractions
- Human-readable reports (not JSON)
- Fast response times (3-8 seconds after first load)
- Secure JWT authentication
- Copy results to clipboard
- Demo mode fallback when Ollama is unavailable

## Screenshots

### Dashboard
![Dashboard](uploads/dashboard.png)

### Email Summarizer
![Email Summarizer](uploads/email_summarizer.png)

### Content Generator
![Content Generator](uploads/content_generator.png)

### Data Analyzer
![Data Analyzer](uploads/data_analyzer.png)

### Code Reviewer
![Code Reviewer](uploads/code_reviewer.png)

## Technology Stack

### Backend
- **FastAPI** - High-performance async API framework
- **SQLAlchemy** - ORM with SQLite database
- **Ollama** - Local LLM inference (LLaMA 3.2)
- **LangChain** - LLM framework for agent orchestration
- **Argon2** - Password hashing
- **JWT** - Secure authentication

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Zustand** - State management
- **shadcn/ui** - UI components

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama ([Download](https://ollama.ai))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/shreyaupretyy/taskflow-agent.git
cd taskflow-agent
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and set DEFAULT_MODEL=llama3.2
```

3. **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
```

4. **Install Ollama and Model**
```bash
# Download Ollama from https://ollama.ai

# Pull LLaMA 3.2 model
ollama pull llama3.2

# Start Ollama (it usually runs automatically as a service)
ollama serve
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### First Time Setup

1. Navigate to http://localhost:3000
2. Click "Register" to create an account
3. Login with your credentials
4. Select any agent from the dashboard
5. Enter your text and click "Run Agent"
6. Get AI-generated results in seconds!

## Usage Guide

### Email Summarizer
Analyzes emails and provides:
- Concise summary
- Sender and subject information
- Priority level and category
- Action items with deadlines
- Key points

**Example Input:**
```
From: john@company.com
Subject: Q4 Budget Review - Action Required

Hi team, we need to finalize our Q4 budget numbers by Wednesday EOD. 
Please review the attached spreadsheet and provide your department's input.
```

### Content Generator
Creates professional content including:
- Engaging title
- Well-structured content
- Word count and metadata
- Key takeaways

**Example Input:**
```
Write a blog post about the benefits of AI automation in business
```

### Data Analyzer
Provides comprehensive analysis with:
- Executive summary
- Key insights
- Identified patterns
- Actionable recommendations

**Example Input:**
```
Analyze this sales data: Q1: $50K, Q2: $75K, Q3: $90K, Q4: $120K
```

### Code Reviewer
Reviews code and provides:
- Brief summary of issues
- Complete corrected code
- List of changes made

**Example Input:**
```python
def calculate(x,y):
    result = x+y
    return result
```

## Configuration

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./taskflow.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
TEMPERATURE=0.7

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

```
taskflow-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   │   └── base_agent.py
│   │   ├── api/
│   │   │   └── routes/      # API endpoints
│   │   │       ├── auth.py
│   │   │       └── agents.py
│   │   ├── core/            # Configuration and security
│   │   ├── models/          # Database models
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   │   ├── auth/        # Login/Register
│   │   │   ├── dashboard/   # Main dashboard
│   │   │   └── agents/      # Agent pages
│   │   ├── components/      # React components
│   │   │   └── AgentInterface.tsx
│   │   └── store/           # State management
│   ├── package.json
│   └── .env.local
│
└── uploads/                 # Screenshots
```

## Security

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - Argon2 for secure password storage
- **CORS Protection** - Configured origins only
- **SQL Injection Protection** - SQLAlchemy ORM
- **Rate Limiting Ready** - Backend infrastructure in place

## Troubleshooting

### Ollama Not Connected
**Error:** "Using demo mode - Ollama not connected"

**Solution:**
1. Install Ollama from https://ollama.ai
2. Run `ollama pull llama3.2`
3. Ensure Ollama is running: `ollama serve`
4. Check `OLLAMA_BASE_URL` in backend `.env`

### Backend Won't Start
**Error:** Port already in use

**Solution:**
```bash
# Kill existing Python processes
taskkill /F /IM python.exe  # Windows
# pkill -9 python  # Linux/Mac
```

### Authentication Errors
**Error:** 401 Unauthorized

**Solution:**
1. Logout and login again to refresh token
2. Clear browser localStorage
3. Check backend logs for JWT errors

## Performance

- **First Request:** 15-30 seconds (model loads into RAM)
- **Subsequent Requests:** 3-8 seconds
- **Model Size:** ~2GB (LLaMA 3.2)
- **Memory Usage:** 4-8GB RAM recommended

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **GitHub Repository:** https://github.com/shreyaupretyy/taskflow-agent
- **Ollama:** https://ollama.ai
- **LLaMA Models:** https://ai.meta.com/llama/

## Acknowledgments

- Ollama team for local LLM infrastructure
- Meta for LLaMA models
- LangChain for agent framework
- FastAPI and Next.js communities

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/shreyaupretyy/taskflow-agent/issues)
- Check existing issues for solutions

---

**Built for business automation**
