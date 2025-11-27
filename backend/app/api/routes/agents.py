from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.core.security import get_current_active_user
from app.models.user import User
from app.agents.base_agent import create_agent

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentExecuteRequest(BaseModel):
    agent_id: str
    input_text: str


@router.post("/execute")
async def execute_agent(
    request: AgentExecuteRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Execute an AI agent with given input."""
    try:
        # Map agent IDs to agent types
        agent_type_map = {
            "email-summarizer": "extractor",
            "content-generator": "writer",
            "data-analyzer": "analyzer",
            "customer-support": "writer",
            "code-reviewer": "analyzer",
            "meeting-notes": "extractor"
        }
        
        agent_type = agent_type_map.get(request.agent_id)
        if not agent_type:
            raise HTTPException(status_code=400, detail="Invalid agent ID")
        
        # Create and execute agent
        agent = create_agent(agent_type)
        result = await agent.execute({
            "text": request.input_text,
            "query": request.input_text,
            "task": request.input_text,
            "data": request.input_text
        })
        
        return {
            "status": "success",
            "agent_id": request.agent_id,
            "output": result,
            "demo_mode": False
        }
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Agent execution error: {type(e).__name__}: {str(e)}")
        
        # Fallback to demo results if Ollama not available
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg or "ollama" in error_msg or "could not connect" in error_msg:
            demo_result = generate_demo_agent_result(request.agent_id, request.input_text)
            return {
                "status": "success",
                "agent_id": request.agent_id,
                "output": demo_result,
                "demo_mode": True,
                "message": "⚠️ Using demo mode - Ollama not connected. Install from https://ollama.ai and run 'ollama serve'"
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
                    "key_points": ["Project update provided", "Approval needed", "Timeline discussed"]
                }
            }
        },
        "content-generator": {
            "agent": "Writer",
            "status": "success",
            "data": {
                "title": "Generated Content Based on Your Input",
                "content": "This is a professionally generated article that addresses your topic. In a real scenario with Ollama running, this would be a comprehensive, well-researched piece tailored to your specific requirements. The AI would analyze your input, research the topic, and create engaging content with proper structure, introduction, body paragraphs, and conclusion.",
                "word_count": 250,
                "summary": "Professional content addressing your specified topic and requirements"
            }
        },
        "data-analyzer": {
            "agent": "Analyzer",
            "status": "success",
            "data": {
                "summary": "Analysis complete with positive trends and actionable insights identified",
                "insights": [
                    "Strong performance indicators across all metrics",
                    "Growth trajectory shows positive momentum",
                    "Key success factors identified and validated"
                ],
                "patterns": [
                    "Consistent upward trend in primary metrics",
                    "Seasonal variations within normal range"
                ],
                "recommendations": [
                    "Continue current strategy with minor optimizations",
                    "Monitor key performance indicators weekly",
                    "Scale successful initiatives to maximize ROI"
                ],
                "confidence": 0.87
            }
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
                    "estimated_resolution": "15-30 minutes"
                }
            }
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
                        "recommendation": "Implement proper input sanitization and validation"
                    },
                    {
                        "severity": "Medium",
                        "category": "Performance",
                        "issue": "Optimization opportunity identified",
                        "recommendation": "Consider caching or algorithm optimization"
                    },
                    {
                        "severity": "Low",
                        "category": "Best Practices",
                        "issue": "Code documentation could be improved",
                        "recommendation": "Add docstrings and inline comments"
                    }
                ],
                "positive_aspects": [
                    "Clean code structure and organization",
                    "Good variable naming conventions",
                    "Proper error handling in most sections"
                ],
                "suggestions": [
                    "Add comprehensive unit tests",
                    "Implement type hints for better maintainability",
                    "Consider design patterns for scalability"
                ]
            }
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
                    "Agreed on hiring timeline and requirements"
                ],
                "action_items": [
                    {
                        "task": "Finalize budget breakdown and documentation",
                        "owner": "Finance Team",
                        "deadline": "End of week",
                        "status": "Pending"
                    },
                    {
                        "task": "Create project kickoff presentation",
                        "owner": "Project Lead",
                        "deadline": "Next Monday",
                        "status": "Pending"
                    },
                    {
                        "task": "Schedule follow-up review meeting",
                        "owner": "Team Lead",
                        "deadline": "Within 2 weeks",
                        "status": "Pending"
                    }
                ],
                "key_discussion_points": [
                    "Performance review exceeded expectations",
                    "Resource allocation optimized for efficiency",
                    "Timeline adjustments discussed and approved",
                    "Risk mitigation strategies identified"
                ],
                "next_meeting": "Two weeks from today"
            }
        }
    }
    
    return results.get(agent_id, {
        "agent": "Unknown",
        "status": "success",
        "data": {"result": "Demo output generated successfully"}
    })
