from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workflow import Workflow, WorkflowExecution
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowExecutionCreate,
    WorkflowExecutionResponse,
    WorkflowExecutionDetailResponse
)
from app.tasks.workflow_tasks import execute_workflow_task
from app.agents.orchestrator import MultiAgentOrchestrator
from app.core.config import settings
from datetime import datetime
import asyncio

router = APIRouter(prefix="/workflows", tags=["workflows"])


def generate_demo_workflow_results(workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate demo results for workflow execution when Ollama is not available."""
    nodes = workflow_data.get("nodes", [])
    input_text = input_data.get("text", "")
    
    results = []
    node_outputs = {}
    
    for node in nodes:
        node_id = node["id"]
        node_type = node["type"]
        
        # Generate mock output based on node type
        if node_type == "extractor":
            output = {
                "extracted_data": {
                    "sender": "demo@example.com",
                    "subject": "Demo Email Subject",
                    "main_topic": "This is a demonstration of the email extraction process",
                    "key_points": [
                        "Point 1: Email processing is working",
                        "Point 2: Extraction completed successfully",
                        "Point 3: Ready for next step"
                    ],
                    "action_items": ["Review the extracted information"]
                }
            }
        elif node_type == "analyzer":
            output = {
                "analysis": {
                    "priority": "Medium",
                    "category": "Information",
                    "sentiment": "Positive",
                    "confidence": 0.85
                }
            }
        elif node_type == "writer":
            if "email" in input_text.lower() or any("email" in n.get("data", {}).get("config", {}).get("prompt", "").lower() for n in nodes):
                output = {
                    "summary": "📧 Email Summary: This is a demonstration email with medium priority. The sender has provided important information that requires review. Action: Please review the extracted data and proceed with next steps. (Demo Mode - Install Ollama for real AI)"
                }
            else:
                output = {
                    "content": "Generated content based on the input. This is a demonstration of the content generation capability. In production, this would use AI to generate comprehensive, contextual content. (Demo Mode - Install Ollama for real AI)"
                }
        elif node_type == "researcher":
            output = {
                "research_findings": {
                    "key_facts": [
                        "Fact 1: Research process initiated",
                        "Fact 2: Information gathered successfully",
                        "Fact 3: Ready for content generation"
                    ],
                    "sources": ["Demo Source 1", "Demo Source 2"]
                }
            }
        else:
            output = {"result": "Demo output for " + node_type}
        
        node_outputs[node_id] = output
        results.append({
            "node_id": node_id,
            "node_type": node_type,
            "status": "success",
            "output": output
        })
    
    return {
        "status": "completed",
        "results": results,
        "final_output": node_outputs.get(nodes[-1]["id"]) if nodes else {},
        "demo_mode": True,
        "message": "⚠️ DEMO MODE: Workflow executed with simulated results. Install and run Ollama (ollama.ai) for real AI processing."
    }


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        owner_id=current_user.id,
        workflow_data=workflow_data.workflow_data,
        trigger_type=workflow_data.trigger_type,
        schedule_config=workflow_data.schedule_config,
        is_active=True
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all workflows for the current user."""
    workflows = db.query(Workflow).filter(
        Workflow.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow."""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Update fields
    for field, value in workflow_data.dict(exclude_unset=True).items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    db.delete(workflow)
    db.commit()
    
    return None


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: int,
    execution_data: WorkflowExecutionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow."""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active"
        )
    
    # Create execution record
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        user_id=current_user.id,
        status="pending",
        trigger_type=execution_data.trigger_type,
        input_data=execution_data.input_data
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    if settings.USE_CELERY:
        # Execute workflow asynchronously with Celery (requires Redis)
        execute_workflow_task.delay(
            workflow_id=workflow_id,
            execution_id=execution.id,
            workflow_data=workflow.workflow_data,
            input_data=execution_data.input_data
        )
    else:
        # Execute workflow synchronously (no Redis required)
        try:
            execution.status = "running"
            execution.started_at = datetime.utcnow()
            db.commit()
            
            if settings.DEMO_MODE:
                # Demo mode: generate mock results when Ollama is not available
                result = generate_demo_workflow_results(
                    workflow.workflow_data,
                    execution_data.input_data
                )
                execution.status = "completed"
                execution.output_data = result
                execution.completed_at = datetime.utcnow()
            else:
                # Real execution with Ollama
                orchestrator = MultiAgentOrchestrator()
                result = await orchestrator.execute_workflow(
                    workflow.workflow_data,
                    execution_data.input_data
                )
                
                execution.status = "completed" if result["status"] == "completed" else "failed"
                execution.output_data = result
                execution.completed_at = datetime.utcnow()
                
                if result.get("errors"):
                    execution.error_message = str(result["errors"])
            
            db.commit()
            db.refresh(execution)
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(execution)
    
    return execution


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_executions(
    workflow_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List executions for a workflow."""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    executions = db.query(WorkflowExecution).filter(
        WorkflowExecution.workflow_id == workflow_id
    ).order_by(WorkflowExecution.created_at.desc()).offset(skip).limit(limit).all()
    
    return executions
