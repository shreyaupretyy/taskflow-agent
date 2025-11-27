from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None


class WorkflowCreate(WorkflowBase):
    workflow_data: Dict[str, Any] = Field(..., description="Nodes and edges configuration")


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    workflow_data: Optional[Dict[str, Any]] = None
    trigger_type: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    id: int
    owner_id: int
    is_active: bool
    workflow_data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkflowExecutionBase(BaseModel):
    trigger_type: Optional[str] = "manual"
    input_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionCreate(WorkflowExecutionBase):
    pass


class WorkflowExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    user_id: int
    status: str
    trigger_type: Optional[str]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: int
    node_id: str
    node_type: str
    level: str
    message: str
    data: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionDetailResponse(WorkflowExecutionResponse):
    logs: List[ExecutionLogResponse] = []
