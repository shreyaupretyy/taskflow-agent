"""Test configuration and fixtures."""
import pytest
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import User

# Set testing environment
os.environ["TESTING"] = "1"

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_ollama():
    """Mock Ollama for testing without actual LLM calls."""
    def mock_invoke(prompt):
        """Mock invoke that returns based on prompt."""
        if "email" in prompt.lower():
            return """EMAIL ANALYSIS REPORT

SUMMARY
Test email summary

SENDER: test@example.com
SUBJECT: Test Subject
PRIORITY: Medium

ACTION ITEMS
• Review the document

KEY POINTS
• Important update"""
        elif "code" in prompt.lower():
            return """CODE REVIEW

SUMMARY
Fixed syntax issues

CORRECTED CODE
def calculate(x, y):
    result = x + y
    return result

CHANGES MADE
• Fixed formatting"""
        else:
            return """REPORT
Test response from mocked LLM"""
    
    mock = MagicMock()
    mock.invoke = MagicMock(side_effect=mock_invoke)
    return mock


@pytest.fixture(autouse=True)
def mock_agent_llm(monkeypatch, mock_ollama):
    """Automatically mock LLM in all agent tests."""
    def mock_init(self, name: str, model: str = None):
        """Mock agent initialization."""
        self.name = name
        self.model = model or "test-model"
        self.llm = mock_ollama
        self.memory = MagicMock()
    
    from app.agents.base_agent import BaseAgent
    monkeypatch.setattr(BaseAgent, "__init__", mock_init)
