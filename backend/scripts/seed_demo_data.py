"""
Seed the database with realistic demo data for showcasing.
Run this script to populate the database with sample executions and metrics.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.workflow import Workflow, WorkflowExecution
from app.models.agent_execution import AgentExecution, AgentMetrics
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random


# Database setup
DATABASE_URL = "sqlite:///./taskflow.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def create_demo_user(db):
    """Create a demo user."""
    demo_user = db.query(User).filter(User.email == "demo@taskflow.com").first()
    
    if not demo_user:
        demo_user = User(
            email="demo@taskflow.com",
            username="demo_user",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✓ Created demo user: {demo_user.email}")
    else:
        print(f"✓ Demo user already exists: {demo_user.email}")
    
    return demo_user


def create_demo_workflows(db, user):
    """Create sample workflows."""
    workflows_data = [
        {
            "name": "Market Research Automation",
            "description": "Automated market research and competitive analysis workflow",
            "is_active": True,
            "workflow_data": {"nodes": [], "edges": []}
        },
        {
            "name": "Content Generation Pipeline",
            "description": "AI-powered content creation and optimization workflow",
            "is_active": True,
            "workflow_data": {"nodes": [], "edges": []}
        },
        {
            "name": "Data Analysis Workflow",
            "description": "Automated data extraction, analysis, and reporting",
            "is_active": True,
            "workflow_data": {"nodes": [], "edges": []}
        },
        {
            "name": "Document Q&A System",
            "description": "RAG-based document querying and knowledge extraction",
            "is_active": True,
            "workflow_data": {"nodes": [], "edges": []}
        }
    ]
    
    workflows = []
    for wf_data in workflows_data:
        wf = db.query(Workflow).filter(
            Workflow.name == wf_data["name"],
            Workflow.owner_id == user.id
        ).first()
        
        if not wf:
            wf = Workflow(owner_id=user.id, **wf_data)
            db.add(wf)
            db.commit()
            db.refresh(wf)
        
        workflows.append(wf)
    
    print(f"✓ Created {len(workflows)} workflows")
    return workflows


def create_demo_executions(db, workflows, user):
    """Create sample workflow executions with realistic patterns."""
    execution_count = 0
    
    for workflow in workflows:
        # Create 15-25 executions per workflow over the last 30 days
        num_executions = random.randint(15, 25)
        
        for i in range(num_executions):
            days_ago = random.randint(0, 30)
            created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # 85% success rate
            status = "completed" if random.random() < 0.85 else random.choice(["failed", "cancelled"])
            
            # Execution time varies by workflow type
            if "Analysis" in workflow.name or "Q&A" in workflow.name:
                execution_time = random.uniform(5, 15)  # Longer for complex tasks
            else:
                execution_time = random.uniform(2, 8)
            
            execution = WorkflowExecution(
                workflow_id=workflow.id,
                user_id=user.id,
                status=status,
                started_at=created_at,
                completed_at=created_at + timedelta(seconds=execution_time) if status == "completed" else None,
                input_data={"task": f"Sample task {i+1}"},
                output_data={"result": "Generated output"} if status == "completed" else None,
                error_message="Simulated error" if status == "failed" else None
            )
            db.add(execution)
            execution_count += 1
    
    db.commit()
    print(f"✓ Created {execution_count} workflow executions")


def create_agent_metrics(db, user):
    """Create sample agent execution records."""
    agent_types = ["DataExtractor", "ContentWriter", "Analyzer", "DocumentQA", "RAG"]
    
    metrics_count = 0
    
    for agent_type in agent_types:
        # Create 20-30 execution records per agent type
        num_records = random.randint(20, 30)
        
        for i in range(num_records):
            days_ago = random.randint(0, 30)
            executed_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Realistic metrics based on agent type
            if agent_type in ["DocumentQA", "RAG"]:
                tokens_used = random.randint(700, 2800)
                response_time = random.uniform(3000, 12000)
            elif agent_type == "Analyzer":
                tokens_used = random.randint(450, 1500)
                response_time = random.uniform(2000, 8000)
            else:
                tokens_used = random.randint(250, 1100)
                response_time = random.uniform(1000, 5000)
            
            # 90% success rate
            success = random.random() < 0.90
            
            agent_exec = AgentExecution(
                user_id=user.id,
                agent_type=agent_type,
                model_name="llama3.2:latest",
                input_text=f"Sample query {i+1} for {agent_type}",
                output_text=f"Generated response {i+1}" if success else None,
                tokens_used=tokens_used,
                response_time_ms=response_time,
                success=success,
                error_message="Simulated error" if not success else None,
                user_rating=random.randint(4, 5) if success and random.random() < 0.3 else None,
                created_at=executed_at
            )
            db.add(agent_exec)
            metrics_count += 1
    
    db.commit()
    print(f"✓ Created {metrics_count} agent execution records")


def create_agent_comparison_data(db, user):
    """Create model comparison metrics for different models."""
    models = ["llama3.2:latest", "mistral:latest", "phi:latest"]
    agent_types = ["DataExtractor", "ContentWriter", "Analyzer"]
    
    comparison_count = 0
    
    for model in models:
        for agent_type in agent_types:
            # Create 10 executions per model-agent combination
            for i in range(10):
                days_ago = random.randint(0, 14)
                executed_at = datetime.utcnow() - timedelta(days=days_ago)
                
                # Model-specific characteristics
                if model.startswith("llama"):
                    base_time = 3500
                    base_tokens = 400
                    success_rate = 0.95
                elif model.startswith("mistral"):
                    base_time = 2800
                    base_tokens = 350
                    success_rate = 0.93
                else:  # phi
                    base_time = 2000
                    base_tokens = 300
                    success_rate = 0.88
                
                response_time = base_time + random.uniform(-500, 500)
                tokens = int(base_tokens + random.uniform(-50, 50))
                
                success = random.random() < success_rate
                
                agent_exec = AgentExecution(
                    user_id=user.id,
                    agent_type=agent_type,
                    model_name=model,
                    input_text=f"Comparison test query {i+1}",
                    output_text=f"Response from {model}" if success else None,
                    tokens_used=tokens,
                    response_time_ms=response_time,
                    success=success,
                    error_message="Simulated error" if not success else None,
                    created_at=executed_at
                )
                db.add(agent_exec)
                comparison_count += 1
    
    db.commit()
    print(f"✓ Created {comparison_count} model comparison records")


def main():
    """Main seeding function."""
    print("\n🌱 Seeding demo data...\n")
    
    db = SessionLocal()
    
    try:
        # Create demo user
        user = create_demo_user(db)
        
        # Create workflows
        workflows = create_demo_workflows(db, user)
        
        # Create executions
        create_demo_executions(db, workflows, user)
        
        # Create agent metrics
        create_agent_metrics(db, user)
        
        # Create model comparison data
        create_agent_comparison_data(db, user)
        
        print("\n✅ Demo data seeded successfully!")
        print("\nDemo credentials:")
        print("  Email: demo@taskflow.com")
        print("  Password: demo123")
        print("\nYou can now:")
        print("  1. Login with demo credentials")
        print("  2. View metrics dashboard with real data")
        print("  3. See workflow execution history")
        print("  4. Compare model performance")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
