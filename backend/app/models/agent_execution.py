from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class AgentExecution(Base):
    """Track all agent executions with detailed metrics."""

    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_type = Column(String(50), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)

    # Input/Output
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=True)

    # Metrics
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=False)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Quality metrics
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agent_executions")


class DocumentStore(Base):
    """Store documents for RAG-based agents."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(100), nullable=True)

    # Vector database references
    collection_name = Column(String(255), nullable=False)
    chunk_count = Column(Integer, default=0)

    # Metadata
    file_size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")


class AgentMetrics(Base):
    """Aggregate metrics per agent type."""

    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False, unique=True, index=True)

    # Aggregate stats
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)

    # Performance metrics
    avg_response_time_ms = Column(Float, default=0.0)
    total_tokens_used = Column(Integer, default=0)

    # Quality metrics
    avg_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)

    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
