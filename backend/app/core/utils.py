import re
from typing import Any, Dict, List


def extract_variables(text: str) -> List[str]:
    """Extract variable references from text (e.g., {{variable}})."""
    pattern = r"\{\{([^}]+)\}\}"
    return re.findall(pattern, text)


def replace_variables(text: str, variables: Dict[str, Any]) -> str:
    """Replace variable references with actual values."""
    for var_name, value in variables.items():
        placeholder = f"{{{{{var_name}}}}}"
        text = text.replace(placeholder, str(value))
    return text


def validate_workflow_data(workflow_data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate workflow data structure."""
    if not isinstance(workflow_data, dict):
        return False, "Workflow data must be a dictionary"

    if "nodes" not in workflow_data:
        return False, "Workflow must contain 'nodes'"

    if "edges" not in workflow_data:
        return False, "Workflow must contain 'edges'"

    nodes = workflow_data["nodes"]
    edges = workflow_data["edges"]

    if not isinstance(nodes, list):
        return False, "'nodes' must be a list"

    if not isinstance(edges, list):
        return False, "'edges' must be a list"

    # Check for at least one node
    if len(nodes) == 0:
        return False, "Workflow must have at least one node"

    # Validate node structure
    node_ids = set()
    for node in nodes:
        if "id" not in node:
            return False, "Each node must have an 'id'"
        if "type" not in node:
            return False, "Each node must have a 'type'"
        node_ids.add(node["id"])

    # Validate edges
    for edge in edges:
        if "source" not in edge or "target" not in edge:
            return False, "Each edge must have 'source' and 'target'"

        if edge["source"] not in node_ids:
            return False, f"Edge source '{edge['source']}' not found in nodes"

        if edge["target"] not in node_ids:
            return False, f"Edge target '{edge['target']}' not found in nodes"

    return True, "Valid"


def sanitize_node_data(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize node data for security."""
    sanitized = node_data.copy()

    # Remove any script tags
    if "config" in sanitized:
        config = sanitized["config"]
        for key, value in config.items():
            if isinstance(value, str):
                # Remove script tags and potentially dangerous HTML
                value = re.sub(
                    r"<script[^>]*>.*?</script>", "", value, flags=re.DOTALL | re.IGNORECASE
                )
                value = re.sub(r"javascript:", "", value, flags=re.IGNORECASE)
                config[key] = value

    return sanitized


def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable format."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds / 3600)
        remaining_minutes = int((seconds % 3600) / 60)
        return f"{hours}h {remaining_minutes}m"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def parse_cron_expression(expression: str) -> Dict[str, Any]:
    """Parse a cron expression into a readable format."""
    parts = expression.split()

    if len(parts) != 5:
        return {"error": "Invalid cron expression"}

    minute, hour, day, month, weekday = parts

    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "weekday": weekday,
        "description": f"Runs at {hour}:{minute}",
    }
