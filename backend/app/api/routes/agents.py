import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.base_agent import create_agent
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.metrics_service import MetricsService
from app.utils.token_utils import estimate_tokens

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentExecuteRequest(BaseModel):
    agent_id: str
    input_text: str
    model: Optional[str] = None  # Allow model selection


class RatingRequest(BaseModel):
    execution_id: int
    rating: int  # 1-5
    feedback: Optional[str] = None


class ModelCompareRequest(BaseModel):
    agent_id: str
    input_text: str
    models: List[str]  # List of models to compare


@router.post("/execute")
async def execute_agent(
    request: AgentExecuteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute an AI agent with given input and track metrics."""
    start_time = time.time()

    try:
        # Map agent IDs to agent types
        agent_type_map = {
            "email-summarizer": "extractor",
            "content-generator": "writer",
            "data-analyzer": "analyzer",
            "customer-support": "writer",
            "code-reviewer": "analyzer",
            "meeting-notes": "extractor",
        }

        agent_type = agent_type_map.get(request.agent_id)
        if not agent_type:
            raise HTTPException(status_code=400, detail="Invalid agent ID")

        # Create agent with optional model selection
        agent = create_agent(agent_type)
        if request.model:
            agent.model = request.model
            agent.llm.model = request.model

        # Execute agent
        result = await agent.execute(
            {
                "text": request.input_text,
                "query": request.input_text,
                "task": request.input_text,
                "data": request.input_text,
            }
        )

        # Calculate metrics
        response_time_ms = (time.time() - start_time) * 1000
        output_text = str(result.get("report", ""))

        # Estimate tokens used
        tokens_used = estimate_tokens(request.input_text) + estimate_tokens(output_text)

        # Record execution in database
        execution = MetricsService.record_execution(
            db=db,
            user_id=current_user.id,
            agent_type=agent_type,
            model_name=request.model or settings.DEFAULT_MODEL,
            input_text=request.input_text[:1000],  # Truncate for storage
            output_text=output_text[:2000],
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            success=True,
        )

        return {
            "status": "success",
            "agent_id": request.agent_id,
            "output": result,
            "demo_mode": False,
            "execution_id": execution.id,
            "response_time_ms": round(response_time_ms, 2),
            "tokens_used": tokens_used,
            "model_used": request.model or settings.DEFAULT_MODEL,
        }
    except Exception as e:
        # Record failed execution
        response_time_ms = (time.time() - start_time) * 1000
        try:
            MetricsService.record_execution(
                db=db,
                user_id=current_user.id,
                agent_type=agent_type_map.get(request.agent_id, "unknown"),
                model_name=request.model or settings.DEFAULT_MODEL,
                input_text=request.input_text[:1000],
                output_text="",
                response_time_ms=response_time_ms,
                success=False,
                error_message=str(e),
            )
        except:
            pass  # Don't fail if metrics recording fails

        # Log the error for debugging
        print(f"❌ Agent execution error: {type(e).__name__}: {str(e)}")

        # Fallback to demo results if Ollama not available
        error_msg = str(e).lower()
        if (
            "connection" in error_msg
            or "refused" in error_msg
            or "ollama" in error_msg
            or "could not connect" in error_msg
        ):
            demo_result = generate_demo_agent_result(request.agent_id, request.input_text)
            return {
                "status": "success",
                "agent_id": request.agent_id,
                "output": demo_result,
                "demo_mode": True,
                "message": "⚠️ Using demo mode - Ollama not connected. Install from https://ollama.ai and run 'ollama serve'",
            }
        raise HTTPException(status_code=500, detail=str(e))


def generate_demo_agent_result(agent_id: str, input_text: str) -> Dict[str, Any]:
    """Generate demo results when Ollama is not available."""
    results = {
        "email-summarizer": {
            "agent": "Extractor",
            "status": "success",
            "data": {
                "summary": "📧 Email Summary: High priority message requiring action. Key points extracted and categorized.",
                "extracted_data": {
                    "sender": "demo@example.com",
                    "priority": "High",
                    "category": "Action Required",
                    "sentiment": "Positive",
                    "action_items": ["Review documents", "Provide feedback", "Approve next steps"],
                    "key_points": [
                        "Project update provided",
                        "Approval needed",
                        "Timeline discussed",
                    ],
                },
            },
        },
        "content-generator": {
            "agent": "Writer",
            "status": "success",
            "data": {
                "title": "Generated Content Based on Your Input",
                "content": "This is a professionally generated article that addresses your topic. In a real scenario with Ollama running, this would be a comprehensive, well-researched piece tailored to your specific requirements. The AI would analyze your input, research the topic, and create engaging content with proper structure, introduction, body paragraphs, and conclusion.",
                "word_count": 250,
                "summary": "Professional content addressing your specified topic and requirements",
            },
        },
        "data-analyzer": {
            "agent": "Analyzer",
            "status": "success",
            "data": {
                "summary": "Analysis complete with positive trends and actionable insights identified",
                "insights": [
                    "Strong performance indicators across all metrics",
                    "Growth trajectory shows positive momentum",
                    "Key success factors identified and validated",
                ],
                "patterns": [
                    "Consistent upward trend in primary metrics",
                    "Seasonal variations within normal range",
                ],
                "recommendations": [
                    "Continue current strategy with minor optimizations",
                    "Monitor key performance indicators weekly",
                    "Scale successful initiatives to maximize ROI",
                ],
                "confidence": 0.87,
            },
        },
        "customer-support": {
            "agent": "Writer",
            "status": "success",
            "data": {
                "response": """Thank you for reaching out to us. I understand your concern and sincerely apologize for any inconvenience this has caused.

I've reviewed your inquiry and here's how we can help:

1. **Immediate Action**: [Specific solution based on the issue]
2. **Alternative Options**: [Backup solutions if needed]
3. **Follow-up**: We'll monitor this to ensure resolution

Your satisfaction is our priority, and we're committed to resolving this promptly. Please let me know if you have any questions or need further assistance.

Best regards,
Customer Support Team""",
                "analysis": {
                    "issue_type": "General Inquiry",
                    "priority": "Medium",
                    "sentiment": "Neutral",
                    "estimated_resolution": "15-30 minutes",
                },
            },
        },
        "code-reviewer": {
            "agent": "Analyzer",
            "status": "success",
            "data": {
                "overall_assessment": "Code quality: Good | Security: Review needed | Performance: Acceptable",
                "findings": [
                    {
                        "severity": "High",
                        "category": "Security",
                        "issue": "Input validation required",
                        "recommendation": "Implement proper input sanitization and validation",
                    },
                    {
                        "severity": "Medium",
                        "category": "Performance",
                        "issue": "Optimization opportunity identified",
                        "recommendation": "Consider caching or algorithm optimization",
                    },
                    {
                        "severity": "Low",
                        "category": "Best Practices",
                        "issue": "Code documentation could be improved",
                        "recommendation": "Add docstrings and inline comments",
                    },
                ],
                "positive_aspects": [
                    "Clean code structure and organization",
                    "Good variable naming conventions",
                    "Proper error handling in most sections",
                ],
                "suggestions": [
                    "Add comprehensive unit tests",
                    "Implement type hints for better maintainability",
                    "Consider design patterns for scalability",
                ],
            },
        },
        "meeting-notes": {
            "agent": "Extractor",
            "status": "success",
            "data": {
                "summary": "Meeting focused on planning, resource allocation, and strategic decisions",
                "attendees": ["Team Member 1", "Team Member 2", "Team Member 3"],
                "date": "November 27, 2025",
                "decisions_made": [
                    "Approved proposed budget allocation",
                    "Selected priority projects for next quarter",
                    "Agreed on hiring timeline and requirements",
                ],
                "action_items": [
                    {
                        "task": "Finalize budget breakdown and documentation",
                        "owner": "Finance Team",
                        "deadline": "End of week",
                        "status": "Pending",
                    },
                    {
                        "task": "Create project kickoff presentation",
                        "owner": "Project Lead",
                        "deadline": "Next Monday",
                        "status": "Pending",
                    },
                    {
                        "task": "Schedule follow-up review meeting",
                        "owner": "Team Lead",
                        "deadline": "Within 2 weeks",
                        "status": "Pending",
                    },
                ],
                "key_discussion_points": [
                    "Performance review exceeded expectations",
                    "Resource allocation optimized for efficiency",
                    "Timeline adjustments discussed and approved",
                    "Risk mitigation strategies identified",
                ],
                "next_meeting": "Two weeks from today",
            },
        },
    }

    return results.get(
        agent_id,
        {
            "agent": "Unknown",
            "status": "success",
            "data": {"result": "Demo output generated successfully"},
        },
    )


@router.post("/rate")
async def rate_execution(
    request: RatingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Rate an agent execution."""
    try:
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        execution = MetricsService.add_user_rating(
            db=db,
            execution_id=request.execution_id,
            rating=request.rating,
            feedback=request.feedback,
        )

        return {
            "status": "success",
            "message": "Rating submitted successfully",
            "execution_id": execution.id,
            "rating": execution.user_rating,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(
    agent_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get agent performance metrics."""
    try:
        metrics = MetricsService.get_agent_metrics(db, agent_type)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-stats")
async def get_user_stats(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user's usage statistics."""
    try:
        stats = MetricsService.get_user_stats(db, current_user.id, days)
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_executions(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user's recent executions."""
    try:
        executions = MetricsService.get_recent_executions(db, current_user.id, limit)
        return {"status": "success", "executions": executions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-models")
async def compare_models(
    request: ModelCompareRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Compare responses from different models."""
    try:
        agent_type_map = {
            "email-summarizer": "extractor",
            "content-generator": "writer",
            "data-analyzer": "analyzer",
            "customer-support": "writer",
            "code-reviewer": "analyzer",
            "meeting-notes": "extractor",
        }

        agent_type = agent_type_map.get(request.agent_id)
        if not agent_type:
            raise HTTPException(status_code=400, detail="Invalid agent ID")

        results = []

        for model in request.models:
            start_time = time.time()
            try:
                agent = create_agent(agent_type)
                agent.model = model
                agent.llm.model = model

                result = await agent.execute(
                    {
                        "text": request.input_text,
                        "query": request.input_text,
                        "task": request.input_text,
                        "data": request.input_text,
                    }
                )

                response_time_ms = (time.time() - start_time) * 1000

                # Record execution
                execution = MetricsService.record_execution(
                    db=db,
                    user_id=current_user.id,
                    agent_type=agent_type,
                    model_name=model,
                    input_text=request.input_text[:1000],
                    output_text=str(result.get("report", ""))[:2000],
                    response_time_ms=response_time_ms,
                    success=True,
                )

                results.append(
                    {
                        "model": model,
                        "output": result,
                        "response_time_ms": round(response_time_ms, 2),
                        "execution_id": execution.id,
                        "success": True,
                    }
                )
            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000
                results.append(
                    {
                        "model": model,
                        "error": str(e),
                        "response_time_ms": round(response_time_ms, 2),
                        "success": False,
                    }
                )

        return {"status": "success", "comparisons": results, "models_compared": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
