from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of workflow nodes."""

    TRIGGER = "trigger"
    RESEARCHER = "researcher"
    EXTRACTOR = "extractor"
    WRITER = "writer"
    ANALYZER = "analyzer"
    HTTP_REQUEST = "http_request"
    DATABASE = "database"
    EMAIL = "email"
    CONDITION = "condition"
    TRANSFORM = "transform"
    LOOP = "loop"
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"


class NodeConfig(BaseModel):
    """Base configuration for workflow nodes."""

    label: str
    type: NodeType
    config: Dict[str, Any] = Field(default_factory=dict)


class ResearcherConfig(NodeConfig):
    """Configuration for researcher agent node."""

    type: NodeType = NodeType.RESEARCHER
    config: Dict[str, Any] = Field(
        default_factory=lambda: {"query": "", "context": "", "model": "llama3"}
    )


class ExtractorConfig(NodeConfig):
    """Configuration for extractor agent node."""

    type: NodeType = NodeType.EXTRACTOR
    config: Dict[str, Any] = Field(default_factory=lambda: {"text": "", "fields": [], "schema": {}})


class WriterConfig(NodeConfig):
    """Configuration for writer agent node."""

    type: NodeType = NodeType.WRITER
    config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "task": "",
            "content_type": "article",
            "tone": "professional",
            "length": "medium",
        }
    )


class HTTPRequestConfig(NodeConfig):
    """Configuration for HTTP request node."""

    type: NodeType = NodeType.HTTP_REQUEST
    config: Dict[str, Any] = Field(
        default_factory=lambda: {"method": "GET", "url": "", "headers": {}, "body": None}
    )


class EmailConfig(NodeConfig):
    """Configuration for email node."""

    type: NodeType = NodeType.EMAIL
    config: Dict[str, Any] = Field(default_factory=lambda: {"to": [], "subject": "", "body": ""})


class ConditionConfig(NodeConfig):
    """Configuration for condition node."""

    type: NodeType = NodeType.CONDITION
    config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "type": "equals",  # equals, not_equals, greater_than, less_than, contains
            "left": "",
            "right": "",
        }
    )


# Node type definitions for frontend
NODE_DEFINITIONS = {
    "trigger": {
        "label": "Trigger",
        "category": "inputs",
        "description": "Start the workflow",
        "icon": "play",
        "inputs": 0,
        "outputs": 1,
    },
    "researcher": {
        "label": "Researcher Agent",
        "category": "agents",
        "description": "Research and gather information",
        "icon": "search",
        "inputs": 1,
        "outputs": 1,
    },
    "extractor": {
        "label": "Extractor Agent",
        "category": "agents",
        "description": "Extract structured data",
        "icon": "filter",
        "inputs": 1,
        "outputs": 1,
    },
    "writer": {
        "label": "Writer Agent",
        "category": "agents",
        "description": "Generate written content",
        "icon": "edit",
        "inputs": 1,
        "outputs": 1,
    },
    "analyzer": {
        "label": "Analyzer Agent",
        "category": "agents",
        "description": "Analyze data and provide insights",
        "icon": "chart",
        "inputs": 1,
        "outputs": 1,
    },
    "http_request": {
        "label": "HTTP Request",
        "category": "actions",
        "description": "Make HTTP API calls",
        "icon": "globe",
        "inputs": 1,
        "outputs": 1,
    },
    "email": {
        "label": "Send Email",
        "category": "actions",
        "description": "Send email notifications",
        "icon": "mail",
        "inputs": 1,
        "outputs": 1,
    },
    "database": {
        "label": "Database",
        "category": "actions",
        "description": "Query or update database",
        "icon": "database",
        "inputs": 1,
        "outputs": 1,
    },
    "condition": {
        "label": "Condition",
        "category": "logic",
        "description": "Conditional branching",
        "icon": "split",
        "inputs": 1,
        "outputs": 2,
    },
    "transform": {
        "label": "Transform",
        "category": "logic",
        "description": "Transform data",
        "icon": "transform",
        "inputs": 1,
        "outputs": 1,
    },
    "loop": {
        "label": "Loop",
        "category": "logic",
        "description": "Iterate over items",
        "icon": "repeat",
        "inputs": 1,
        "outputs": 1,
    },
}
