"""Test workflow execution."""
import pytest
from app.agents.orchestrator import WorkflowOrchestrator


@pytest.mark.asyncio
async def test_simple_workflow():
    """Test simple workflow execution."""
    workflow_data = {
        "nodes": [
            {
                "id": "trigger",
                "type": "trigger",
                "data": {"config": {}}
            },
            {
                "id": "delay",
                "type": "delay",
                "data": {
                    "config": {
                        "duration": 1,
                        "unit": "seconds"
                    }
                }
            }
        ],
        "edges": [
            {
                "source": "trigger",
                "target": "delay"
            }
        ]
    }
    
    orchestrator = WorkflowOrchestrator(
        workflow_id="test",
        workflow_data=workflow_data,
        execution_id="test-exec"
    )
    
    result = await orchestrator.execute()
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_conditional_workflow():
    """Test workflow with conditional logic."""
    workflow_data = {
        "nodes": [
            {
                "id": "trigger",
                "type": "trigger",
                "data": {"config": {}}
            },
            {
                "id": "condition",
                "type": "condition",
                "data": {
                    "config": {
                        "left": "{{test_value}}",
                        "operator": ">",
                        "right": 5
                    }
                }
            },
            {
                "id": "high",
                "type": "delay",
                "data": {
                    "config": {
                        "duration": 1,
                        "unit": "seconds"
                    }
                }
            },
            {
                "id": "low",
                "type": "delay",
                "data": {
                    "config": {
                        "duration": 1,
                        "unit": "seconds"
                    }
                }
            }
        ],
        "edges": [
            {"source": "trigger", "target": "condition"},
            {"source": "condition", "target": "high", "sourceHandle": "true"},
            {"source": "condition", "target": "low", "sourceHandle": "false"}
        ]
    }
    
    orchestrator = WorkflowOrchestrator(
        workflow_id="test",
        workflow_data=workflow_data,
        execution_id="test-exec",
        initial_context={"test_value": 10}
    )
    
    result = await orchestrator.execute()
    assert result["status"] == "completed"
