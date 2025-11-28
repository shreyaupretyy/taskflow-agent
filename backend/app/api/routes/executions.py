from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workflow import ExecutionLog, WorkflowExecution
from app.schemas.workflow import ExecutionLogResponse, WorkflowExecutionDetailResponse

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("/{execution_id}", response_model=WorkflowExecutionDetailResponse)
async def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get execution details with logs."""
    execution = (
        db.query(WorkflowExecution)
        .filter(WorkflowExecution.id == execution_id, WorkflowExecution.user_id == current_user.id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")

    # Get logs
    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.timestamp.asc())
        .all()
    )

    return {**execution.__dict__, "logs": logs}


@router.get("/{execution_id}/logs", response_model=List[ExecutionLogResponse])
async def get_execution_logs(
    execution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get logs for an execution."""
    execution = (
        db.query(WorkflowExecution)
        .filter(WorkflowExecution.id == execution_id, WorkflowExecution.user_id == current_user.id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")

    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.timestamp.asc())
        .all()
    )

    return logs


@router.websocket("/ws/{execution_id}")
async def websocket_execution_logs(websocket: WebSocket, execution_id: int):
    """WebSocket endpoint for real-time execution logs."""
    await websocket.accept()

    db = next(get_db())

    try:
        # Verify execution exists
        execution = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()

        if not execution:
            await websocket.send_json({"error": "Execution not found"})
            await websocket.close()
            return

        # Send initial logs
        logs = (
            db.query(ExecutionLog)
            .filter(ExecutionLog.execution_id == execution_id)
            .order_by(ExecutionLog.timestamp.asc())
            .all()
        )

        for log in logs:
            await websocket.send_json(
                {
                    "id": log.id,
                    "node_id": log.node_id,
                    "node_type": log.node_type,
                    "level": log.level,
                    "message": log.message,
                    "data": log.data,
                    "timestamp": log.timestamp.isoformat(),
                }
            )

        # Keep connection alive and send new logs
        last_log_id = logs[-1].id if logs else 0

        while True:
            # Check for new logs
            new_logs = (
                db.query(ExecutionLog)
                .filter(ExecutionLog.execution_id == execution_id, ExecutionLog.id > last_log_id)
                .order_by(ExecutionLog.timestamp.asc())
                .all()
            )

            for log in new_logs:
                await websocket.send_json(
                    {
                        "id": log.id,
                        "node_id": log.node_id,
                        "node_type": log.node_type,
                        "level": log.level,
                        "message": log.message,
                        "data": log.data,
                        "timestamp": log.timestamp.isoformat(),
                    }
                )
                last_log_id = log.id

            # Check if execution is complete
            db.refresh(execution)
            if execution.status in ["completed", "failed"]:
                await websocket.send_json(
                    {"type": "execution_complete", "status": execution.status}
                )
                break

            # Wait before checking again
            import asyncio

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        db.close()
