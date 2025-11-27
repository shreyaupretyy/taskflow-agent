# TaskFlow Agent: Multi-Agent Workflow Builder

An advanced AI automation platform that enables users to create, orchestrate, and execute complex multi-agent workflows through an intuitive drag-and-drop interface.

## Overview

TaskFlow Agent is a comprehensive workflow automation system designed for businesses, recruiters, lawyers, and founders who need to automate repetitive data workflows without requiring engineering teams. Build sophisticated AI-powered workflows such as website monitoring, data extraction, content summarization, automated emailing, and database updates.

## Key Features

- **Visual Workflow Builder**: Drag-and-drop node-based editor for creating complex AI agent workflows
- **Multi-Agent System**: Specialized agents (Researcher, Extractor, Writer) with persistent memory and state management
- **Long-Running Orchestration**: Robust task execution with Celery for handling complex, time-intensive workflows
- **Intelligent Web Scraping**: Advanced scraping capabilities with anti-bot detection strategies
- **Real-Time Execution Logs**: WebSocket-powered live monitoring of workflow execution
- **Vector-Powered Search**: ChromaDB integration for semantic search and embeddings
- **Enterprise Security**: Role-based access control and API key management system
- **Structured Data Generation**: LLM-generated data automatically stored in PostgreSQL
- **Containerized Deployment**: Docker support for simplified deployment and scaling

## Technology Stack

### Frontend
- Next.js 14 (App Router)
- React Flow - Node-based workflow editor
- Tailwind CSS - Modern, responsive styling
- shadcn/ui - Professional UI components
- WebSocket client - Real-time updates

### Backend
- Python 3.11+
- FastAPI - High-performance async API framework
- LangGraph - Multi-agent orchestration
- PostgreSQL - Primary data store
- ChromaDB - Vector database for embeddings
- Celery + Redis - Task queue and workflow orchestration
- WebSocket - Real-time communication

### AI/ML
- Ollama (Llama 3 / Mixtral) - Local LLM inference
- Sentence Transformers - Open-source embeddings
- LangChain - LLM framework

## Architecture

```
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   └── lib/       # Utilities and helpers
│   └── package.json
│
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── agents/    # AI agent implementations
│   │   ├── api/       # API routes
│   │   ├── core/      # Core configuration
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   └── tasks/     # Celery tasks
│   ├── requirements.txt
│   └── main.py
│
└── docker-compose.yml # Container orchestration
```

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 14+
- Redis 7+
- Ollama (for local LLM inference)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shreyaupretyy/ai-automation-platform.git
cd ai-automation-platform
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations (from backend directory)
python -m alembic upgrade head
```

### 5. Install Ollama and Models

```bash
# Install Ollama from https://ollama.ai

# Pull required models
ollama pull llama3
ollama pull mixtral
```

## Running the Application

### Using Docker (Recommended)

```bash
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

**Terminal 1 - Backend API:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery_app beat --loglevel=info
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

## Usage

### Creating a Workflow

1. Navigate to the Workflow Builder
2. Drag nodes from the sidebar onto the canvas
3. Connect nodes to define the workflow sequence
4. Configure each node with specific parameters
5. Save and execute the workflow

### Available Node Types

- **Trigger Nodes**: Schedule, Webhook, Manual
- **AI Agent Nodes**: Researcher, Extractor, Writer, Analyzer
- **Action Nodes**: HTTP Request, Database Query, Email Sender
- **Logic Nodes**: Condition, Loop, Data Transformer
- **Storage Nodes**: Save to Database, Save to Vector DB

### Example Workflows

**Content Monitoring Pipeline:**
```
Website Monitor → Content Extractor → Summarizer → Email Notification
```

**Data Research Pipeline:**
```
Search Query → Researcher Agent → Data Analyzer → Database Storage
```

**Report Generation:**
```
Database Query → Writer Agent → PDF Generator → Email Sender
```

## API Documentation

Interactive API documentation is available at `/docs` when running the backend server.

### Key Endpoints

- `POST /api/workflows` - Create new workflow
- `GET /api/workflows/{id}` - Get workflow details
- `POST /api/workflows/{id}/execute` - Execute workflow
- `GET /api/executions/{id}/logs` - Get execution logs
- `POST /api/auth/login` - User authentication
- `POST /api/auth/api-keys` - Generate API key

## Configuration

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/taskflow
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PERSIST_DIR=./chroma_data
SECRET_KEY=your-secret-key
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
black app/
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

## Deployment

### Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configurations

- Development: Hot-reload enabled, verbose logging
- Production: Optimized builds, error tracking, rate limiting

## Security Considerations

- API keys are hashed before storage
- Rate limiting on all public endpoints
- CORS properly configured for production
- SQL injection protection via ORM
- Input validation on all user data
- WebSocket authentication required

## Performance Optimization

- Connection pooling for database
- Redis caching for frequent queries
- Lazy loading of workflow nodes
- Batch processing for large datasets
- Worker auto-scaling based on queue length

## Troubleshooting

### Common Issues

**Ollama connection errors:**
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL in environment variables

**Database connection failures:**
- Verify PostgreSQL is running
- Check DATABASE_URL credentials

**Celery tasks not executing:**
- Ensure Redis is running
- Check Celery worker logs
- Verify REDIS_URL configuration

## Contributing

Contributions are welcome. Please follow the existing code style and include tests for new features.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- Multi-tenant support
- Workflow templates marketplace
- Advanced scheduling options
- Cloud provider integrations (AWS, GCP, Azure)
- Mobile application
- Workflow versioning and rollback
- Advanced analytics dashboard
- Custom agent development SDK

---

Built with modern technologies for scalable AI automation.
