import asyncio
from typing import Any, Dict, List, Optional

from langchain.schema import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from app.agents.base_agent import create_agent


class WorkflowState(dict):
    """State object for workflow execution."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "messages" not in self:
            self["messages"] = []
        if "results" not in self:
            self["results"] = {}
        if "errors" not in self:
            self["errors"] = []


class MultiAgentOrchestrator:
    """Orchestrates execution of multiple agents in a workflow."""

    def __init__(self):
        self.agents = {}

    def add_agent(self, agent_id: str, agent_type: str):
        """Add an agent to the orchestrator."""
        self.agents[agent_id] = create_agent(agent_type)

    async def execute_node(self, node: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute a single workflow node."""
        node_type = node.get("type")
        node_id = node.get("id")
        node_data = node.get("data", {})

        result = {
            "node_id": node_id,
            "node_type": node_type,
            "status": "success",
            "output": None,
            "error": None,
        }

        try:
            if node_type in ["researcher", "extractor", "writer", "analyzer"]:
                # AI Agent node
                agent = create_agent(node_type)

                # Get input data from node configuration or previous results
                input_data = self._prepare_agent_input(node_data, state)
                agent_result = await agent.execute(input_data)

                result["output"] = agent_result
                state["results"][node_id] = agent_result

            elif node_type == "http_request":
                # HTTP Request node
                result["output"] = await self._execute_http_request(node_data, state)
                state["results"][node_id] = result["output"]

            elif node_type == "condition":
                # Condition node
                result["output"] = self._evaluate_condition(node_data, state)
                state["results"][node_id] = result["output"]

            elif node_type == "transform":
                # Data transformation node
                result["output"] = self._transform_data(node_data, state)
                state["results"][node_id] = result["output"]

            elif node_type == "email":
                # Email sending node
                result["output"] = await self._send_email(node_data, state)
                state["results"][node_id] = result["output"]

            elif node_type == "database":
                # Database operation node
                result["output"] = await self._execute_database_operation(node_data, state)
                state["results"][node_id] = result["output"]

            else:
                result["status"] = "error"
                result["error"] = f"Unknown node type: {node_type}"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            state["errors"].append({"node_id": node_id, "error": str(e)})

        return result

    def _prepare_agent_input(
        self, node_data: Dict[str, Any], state: WorkflowState
    ) -> Dict[str, Any]:
        """Prepare input data for agent execution."""
        input_data = node_data.get("config", {}).copy()

        # Replace variable references with actual values from previous results
        for key, value in input_data.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Variable reference like {{node_id.field}}
                var_path = value[2:-2].strip()
                input_data[key] = self._resolve_variable(var_path, state)

        return input_data

    def _resolve_variable(self, var_path: str, state: WorkflowState) -> Any:
        """Resolve a variable reference from state."""
        parts = var_path.split(".")

        if parts[0] in state["results"]:
            value = state["results"][parts[0]]

            # Navigate nested structure
            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and part.isdigit():
                    value = value[int(part)]
                else:
                    return None

            return value

        return None

    async def _execute_http_request(
        self, node_data: Dict[str, Any], state: WorkflowState
    ) -> Dict[str, Any]:
        """Execute an HTTP request."""
        import httpx

        config = node_data.get("config", {})
        method = config.get("method", "GET")
        url = config.get("url", "")
        headers = config.get("headers", {})
        body = config.get("body")

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method, url=url, headers=headers, json=body if body else None
            )

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else response.text
                ),
            }

    def _evaluate_condition(
        self, node_data: Dict[str, Any], state: WorkflowState
    ) -> Dict[str, Any]:
        """Evaluate a condition."""
        config = node_data.get("config", {})
        condition_type = config.get("type", "equals")
        left = self._resolve_variable(config.get("left", ""), state)
        right = config.get("right")

        result = False

        if condition_type == "equals":
            result = left == right
        elif condition_type == "not_equals":
            result = left != right
        elif condition_type == "greater_than":
            result = left > right
        elif condition_type == "less_than":
            result = left < right
        elif condition_type == "contains":
            result = right in str(left)
        elif condition_type == "not_contains":
            result = right not in str(left)

        return {"condition": result, "left_value": left, "right_value": right}

    def _transform_data(self, node_data: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Transform data using configured rules."""
        config = node_data.get("config", {})
        input_var = config.get("input")
        transformations = config.get("transformations", [])

        data = self._resolve_variable(input_var, state)

        for transform in transformations:
            transform_type = transform.get("type")

            if transform_type == "map":
                # Map/transform each item
                field = transform.get("field")
                if isinstance(data, list):
                    data = [item.get(field) if isinstance(item, dict) else item for item in data]
            elif transform_type == "filter":
                # Filter items based on condition
                field = transform.get("field")
                value = transform.get("value")
                if isinstance(data, list):
                    data = [item for item in data if item.get(field) == value]
            elif transform_type == "aggregate":
                # Aggregate data
                operation = transform.get("operation")
                if operation == "count":
                    data = len(data) if isinstance(data, list) else 1
                elif operation == "sum":
                    data = sum(data) if isinstance(data, list) else data

        return {"transformed_data": data}

    async def _send_email(self, node_data: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Send an email."""
        # Placeholder for email sending functionality
        config = node_data.get("config", {})
        to = config.get("to")
        subject = config.get("subject")
        body = config.get("body")

        return {
            "sent": True,
            "to": to,
            "subject": subject,
            "message": "Email sending not configured",
        }

    async def _execute_database_operation(
        self, node_data: Dict[str, Any], state: WorkflowState
    ) -> Dict[str, Any]:
        """Execute a database operation."""
        config = node_data.get("config", {})
        operation = config.get("operation", "insert")

        return {"operation": operation, "success": True, "message": "Database operation executed"}

    async def execute_workflow(
        self, workflow_data: Dict[str, Any], input_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a complete workflow."""
        nodes = workflow_data.get("nodes", [])
        edges = workflow_data.get("edges", [])

        # Initialize state
        state = WorkflowState()
        if input_data:
            state["input"] = input_data

        # Build execution order based on edges
        execution_order = self._build_execution_order(nodes, edges)

        # Execute nodes in order
        results = []
        for node_id in execution_order:
            node = next((n for n in nodes if n["id"] == node_id), None)
            if node:
                result = await self.execute_node(node, state)
                results.append(result)

                # Stop execution if there's an error and no error handling
                if result["status"] == "error":
                    break

        return {
            "status": "completed" if not state["errors"] else "failed",
            "results": results,
            "errors": state["errors"],
            "final_state": state["results"],
        }

    def _build_execution_order(self, nodes: List[Dict], edges: List[Dict]) -> List[str]:
        """Build the execution order of nodes based on edges."""
        # Simple topological sort
        # Find nodes with no incoming edges (start nodes)
        node_ids = {node["id"] for node in nodes}
        has_incoming = {edge["target"] for edge in edges}
        start_nodes = node_ids - has_incoming

        # Build adjacency list
        adjacency = {node_id: [] for node_id in node_ids}
        for edge in edges:
            adjacency[edge["source"]].append(edge["target"])

        # Topological sort using DFS
        visited = set()
        order = []

        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                dfs(neighbor)
            order.append(node_id)

        for start_node in start_nodes:
            dfs(start_node)

        return list(reversed(order))
