"""
Initialize database with all tables.
This script creates all tables defined in models without using Alembic.
"""
from app.core.database import Base, engine
from app.models import User, Workflow, WorkflowExecution, ExecutionLog, APIKey, AgentExecution, DocumentStore, AgentMetrics


def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Print all tables created
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    init_db()
