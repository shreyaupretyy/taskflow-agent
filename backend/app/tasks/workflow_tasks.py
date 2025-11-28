import asyncio
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.agents.orchestrator import MultiAgentOrchestrator
from app.core.database import SessionLocal
from app.models.workflow import ExecutionLog, WorkflowExecution
from app.tasks.celery_app import celery_app


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def log_execution(
    db: Session,
    execution_id: int,
    node_id: str,
    node_type: str,
    level: str,
    message: str,
    data: Dict[str, Any] = None,
):
    """Log workflow execution step."""
    log = ExecutionLog(
        execution_id=execution_id,
        node_id=node_id,
        node_type=node_type,
        level=level,
        message=message,
        data=data,
    )
    db.add(log)
    db.commit()


@celery_app.task(bind=True, name="execute_workflow")
def execute_workflow_task(
    self,
    workflow_id: int,
    execution_id: int,
    workflow_data: Dict[str, Any],
    input_data: Dict[str, Any] = None,
):
    """Execute a workflow as a Celery task."""
    db = get_db()

    try:
        # Update execution status
        execution = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if not execution:
            return {"error": "Execution not found"}

        execution.status = "running"
        execution.started_at = datetime.utcnow()
        db.commit()

        # Log start
        log_execution(
            db,
            execution_id,
            "workflow",
            "workflow",
            "info",
            f"Starting workflow execution {execution_id}",
        )

        # Execute workflow
        orchestrator = MultiAgentOrchestrator()

        # Run async workflow in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.execute_workflow(workflow_data, input_data))
        loop.close()

        # Log each node execution
        for node_result in result.get("results", []):
            log_execution(
                db,
                execution_id,
                node_result["node_id"],
                node_result["node_type"],
                "error" if node_result["status"] == "error" else "info",
                f"Node {node_result['node_id']} {node_result['status']}",
                node_result,
            )

        # Update execution with results
        execution.status = result["status"]
        execution.output_data = result.get("final_state", {})
        execution.completed_at = datetime.utcnow()

        if result.get("errors"):
            execution.error_message = str(result["errors"])

        db.commit()

        # Log completion
        log_execution(
            db,
            execution_id,
            "workflow",
            "workflow",
            "info",
            f"Workflow execution {execution_id} {result['status']}",
        )

        return {
            "execution_id": execution_id,
            "status": result["status"],
            "results": result.get("final_state", {}),
        }

    except Exception as e:
        # Handle errors
        execution = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if execution:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()

        log_execution(
            db,
            execution_id,
            "workflow",
            "workflow",
            "error",
            f"Workflow execution failed: {str(e)}",
        )

        return {"execution_id": execution_id, "status": "failed", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="scrape_website")
def scrape_website_task(url: str, config: Dict[str, Any] = None):
    """Scrape a website as a background task."""
    from app.services.scraper import WebScraper

    scraper = WebScraper()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(scraper.scrape_url(url, config))
    loop.close()

    return result


@celery_app.task(name="monitor_website")
def monitor_website_task(url: str, selector: str, interval: int = 300):
    """Monitor a website for changes."""
    from app.services.scraper import WebScraper

    scraper = WebScraper()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(scraper.monitor_changes(url, selector, interval))
    loop.close()

    return result


@celery_app.task(name="cleanup_old_executions")
def cleanup_old_executions_task():
    """Clean up old workflow executions."""
    from datetime import timedelta

    db = get_db()

    try:
        # Delete executions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        deleted = (
            db.query(WorkflowExecution)
            .filter(
                WorkflowExecution.created_at < cutoff_date,
                WorkflowExecution.status.in_(["completed", "failed"]),
            )
            .delete()
        )

        db.commit()

        return {"deleted": deleted}

    finally:
        db.close()
