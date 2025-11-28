"""
Model comparison endpoint for A/B testing different LLMs.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.agent_execution import AgentExecution
from app.models.user import User

router = APIRouter(prefix="/models", tags=["models"])


class ModelPerformance(BaseModel):
    model_name: str
    total_executions: int
    successful_executions: int
    success_rate: float
    avg_response_time_ms: float
    avg_tokens: float


class ModelComparisonResponse(BaseModel):
    models: List[ModelPerformance]
    winner: str
    reason: str


@router.get("/compare", response_model=ModelComparisonResponse)
async def compare_models(
    agent_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Compare performance of different models.
    Returns aggregated metrics for each model over the specified time period.
    """
    try:
        # Calculate date threshold
        since_date = datetime.utcnow() - timedelta(days=days)

        # Build query
        query = db.query(
            AgentExecution.model_name,
            func.count(AgentExecution.id).label("total_executions"),
            func.sum(func.cast(AgentExecution.success, int)).label("successful_executions"),
            func.avg(AgentExecution.response_time_ms).label("avg_response_time_ms"),
            func.avg(AgentExecution.tokens_used).label("avg_tokens"),
        ).filter(AgentExecution.user_id == current_user.id, AgentExecution.created_at >= since_date)

        # Filter by agent type if specified
        if agent_type:
            query = query.filter(AgentExecution.agent_type == agent_type)

        # Group by model and get results
        results = query.group_by(AgentExecution.model_name).all()

        if not results:
            return ModelComparisonResponse(
                models=[], winner="N/A", reason="No execution data available for comparison"
            )

        # Process results
        models = []
        for result in results:
            success_rate = (
                (result.successful_executions / result.total_executions * 100)
                if result.total_executions > 0
                else 0
            )

            models.append(
                ModelPerformance(
                    model_name=result.model_name,
                    total_executions=result.total_executions,
                    successful_executions=result.successful_executions,
                    success_rate=success_rate,
                    avg_response_time_ms=result.avg_response_time_ms or 0,
                    avg_tokens=result.avg_tokens or 0,
                )
            )

        # Determine winner (weighted score: 60% success rate, 40% speed)
        best_model = None
        best_score = 0

        for model in models:
            # Normalize response time (lower is better, inverse for scoring)
            max_time = max(m.avg_response_time_ms for m in models)
            speed_score = (max_time - model.avg_response_time_ms) / max_time if max_time > 0 else 0

            # Calculate weighted score
            score = (model.success_rate / 100 * 0.6) + (speed_score * 0.4)

            if score > best_score:
                best_score = score
                best_model = model

        winner_reason = (
            f"Best balance of reliability ({best_model.success_rate:.1f}% success) "
            f"and speed ({best_model.avg_response_time_ms:.0f}ms avg)"
        )

        return ModelComparisonResponse(
            models=sorted(models, key=lambda x: x.success_rate, reverse=True),
            winner=best_model.model_name,
            reason=winner_reason,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{model_name}")
async def get_model_metrics(
    model_name: str,
    agent_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get detailed metrics for a specific model."""
    try:
        since_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(AgentExecution).filter(
            AgentExecution.user_id == current_user.id,
            AgentExecution.model_name == model_name,
            AgentExecution.created_at >= since_date,
        )

        if agent_type:
            query = query.filter(AgentExecution.agent_type == agent_type)

        executions = query.all()

        if not executions:
            return {
                "model_name": model_name,
                "total_executions": 0,
                "message": "No execution data found",
            }

        total = len(executions)
        successful = sum(1 for e in executions if e.success)
        total_time = sum(e.response_time_ms for e in executions)
        total_tokens = sum(e.tokens_used for e in executions if e.tokens_used)

        # User ratings
        rated_executions = [e for e in executions if e.user_rating is not None]
        avg_rating = (
            sum(e.user_rating for e in rated_executions) / len(rated_executions)
            if rated_executions
            else None
        )

        return {
            "model_name": model_name,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate_percent": (successful / total * 100) if total > 0 else 0,
            "avg_response_time_ms": total_time / total if total > 0 else 0,
            "total_tokens_used": total_tokens,
            "avg_tokens_per_execution": total_tokens / total if total > 0 else 0,
            "user_rating": {"average": avg_rating, "total_ratings": len(rated_executions)},
            "time_period_days": days,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available")
async def get_available_models(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get list of all models that have been used."""
    try:
        models = (
            db.query(AgentExecution.model_name)
            .filter(AgentExecution.user_id == current_user.id)
            .distinct()
            .all()
        )

        return {"models": [model[0] for model in models], "total_count": len(models)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
