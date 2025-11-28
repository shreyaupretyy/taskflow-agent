from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecution, AgentMetrics


class MetricsService:
    """Service for tracking and analyzing agent performance metrics."""

    @staticmethod
    def record_execution(
        db: Session,
        user_id: int,
        agent_type: str,
        model_name: str,
        input_text: str,
        output_text: str,
        response_time_ms: float,
        tokens_used: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AgentExecution:
        """Record an agent execution."""
        execution = AgentExecution(
            user_id=user_id,
            agent_type=agent_type,
            model_name=model_name,
            input_text=input_text,
            output_text=output_text,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            success=success,
            error_message=error_message,
        )
        db.add(execution)

        # Update aggregate metrics
        MetricsService._update_agent_metrics(db, agent_type, response_time_ms, tokens_used, success)

        db.commit()
        db.refresh(execution)
        return execution

    @staticmethod
    def _update_agent_metrics(
        db: Session,
        agent_type: str,
        response_time_ms: float,
        tokens_used: Optional[int],
        success: bool,
    ):
        """Update aggregate metrics for an agent type."""
        metrics = db.query(AgentMetrics).filter(AgentMetrics.agent_type == agent_type).first()

        if not metrics:
            metrics = AgentMetrics(agent_type=agent_type)
            db.add(metrics)

        # Update counts
        metrics.total_executions += 1
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1

        # Update average response time
        total_time = metrics.avg_response_time_ms * (metrics.total_executions - 1)
        metrics.avg_response_time_ms = (total_time + response_time_ms) / metrics.total_executions

        # Update tokens
        if tokens_used:
            metrics.total_tokens_used += tokens_used

        metrics.last_updated = datetime.utcnow()

    @staticmethod
    def add_user_rating(
        db: Session, execution_id: int, rating: int, feedback: Optional[str] = None
    ) -> AgentExecution:
        """Add user rating to an execution."""
        execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()

        if not execution:
            raise ValueError("Execution not found")

        execution.user_rating = rating
        execution.user_feedback = feedback

        # Update aggregate metrics
        metrics = (
            db.query(AgentMetrics).filter(AgentMetrics.agent_type == execution.agent_type).first()
        )

        if metrics:
            total_rating = metrics.avg_rating * metrics.total_ratings
            metrics.total_ratings += 1
            metrics.avg_rating = (total_rating + rating) / metrics.total_ratings
            metrics.last_updated = datetime.utcnow()

        db.commit()
        db.refresh(execution)
        return execution

    @staticmethod
    def get_agent_metrics(db: Session, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for specific agent or all agents."""
        if agent_type:
            metrics = db.query(AgentMetrics).filter(AgentMetrics.agent_type == agent_type).first()

            if not metrics:
                return {
                    "agent_type": agent_type,
                    "total_executions": 0,
                    "success_rate": 0,
                    "avg_response_time_ms": 0,
                    "avg_rating": 0,
                }

            return {
                "agent_type": metrics.agent_type,
                "total_executions": metrics.total_executions,
                "successful_executions": metrics.successful_executions,
                "failed_executions": metrics.failed_executions,
                "success_rate": (
                    (metrics.successful_executions / metrics.total_executions * 100)
                    if metrics.total_executions > 0
                    else 0
                ),
                "avg_response_time_ms": round(metrics.avg_response_time_ms, 2),
                "total_tokens_used": metrics.total_tokens_used,
                "avg_rating": round(metrics.avg_rating, 2),
                "total_ratings": metrics.total_ratings,
                "last_updated": metrics.last_updated,
            }
        else:
            # Get all agent metrics
            all_metrics = db.query(AgentMetrics).all()
            return [
                {
                    "agent_type": m.agent_type,
                    "total_executions": m.total_executions,
                    "success_rate": (
                        (m.successful_executions / m.total_executions * 100)
                        if m.total_executions > 0
                        else 0
                    ),
                    "avg_response_time_ms": round(m.avg_response_time_ms, 2),
                    "avg_rating": round(m.avg_rating, 2),
                }
                for m in all_metrics
            ]

    @staticmethod
    def get_user_stats(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user's usage statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        executions = (
            db.query(AgentExecution)
            .filter(AgentExecution.user_id == user_id, AgentExecution.created_at >= cutoff_date)
            .all()
        )

        if not executions:
            return {
                "total_executions": 0,
                "agents_used": [],
                "avg_response_time": 0,
                "success_rate": 0,
            }

        successful = sum(1 for e in executions if e.success)
        total_time = sum(e.response_time_ms for e in executions)
        agents_used = list(set(e.agent_type for e in executions))

        # Executions per agent
        agent_counts = {}
        for e in executions:
            agent_counts[e.agent_type] = agent_counts.get(e.agent_type, 0) + 1

        return {
            "total_executions": len(executions),
            "successful_executions": successful,
            "failed_executions": len(executions) - successful,
            "success_rate": round(successful / len(executions) * 100, 2),
            "avg_response_time_ms": round(total_time / len(executions), 2),
            "agents_used": agents_used,
            "executions_per_agent": agent_counts,
            "period_days": days,
        }

    @staticmethod
    def get_recent_executions(db: Session, user_id: Optional[int] = None, limit: int = 10) -> list:
        """Get recent executions."""
        query = db.query(AgentExecution).order_by(AgentExecution.created_at.desc())

        if user_id:
            query = query.filter(AgentExecution.user_id == user_id)

        executions = query.limit(limit).all()

        return [
            {
                "id": e.id,
                "agent_type": e.agent_type,
                "model_name": e.model_name,
                "success": e.success,
                "response_time_ms": e.response_time_ms,
                "user_rating": e.user_rating,
                "created_at": e.created_at.isoformat(),
            }
            for e in executions
        ]
