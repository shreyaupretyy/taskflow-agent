"""Workflow validator utilities."""
from typing import Dict, List, Any, Set


class WorkflowValidator:
    """Validate workflow configuration."""
    
    VALID_NODE_TYPES = {
        'trigger', 'ai_agent', 'http_request', 
        'code_executor', 'condition', 'delay'
    }
    
    @staticmethod
    def validate_workflow(workflow_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate workflow structure and configuration.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not workflow_data.get('nodes'):
            errors.append("Workflow must contain at least one node")
            return False, errors
        
        nodes = workflow_data['nodes']
        edges = workflow_data.get('edges', [])
        
        # Validate nodes
        node_ids = set()
        for node in nodes:
            if not node.get('id'):
                errors.append("All nodes must have an ID")
                continue
            
            node_ids.add(node['id'])
            
            if node.get('type') not in WorkflowValidator.VALID_NODE_TYPES:
                errors.append(f"Invalid node type: {node.get('type')}")
            
            if not node.get('data'):
                errors.append(f"Node {node['id']} is missing data configuration")
        
        # Validate edges
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            
            if not source or not target:
                errors.append("All edges must have source and target")
                continue
            
            if source not in node_ids:
                errors.append(f"Edge references non-existent source node: {source}")
            
            if target not in node_ids:
                errors.append(f"Edge references non-existent target node: {target}")
        
        # Check for cycles
        if WorkflowValidator._has_cycle(nodes, edges):
            errors.append("Workflow contains a cycle")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _has_cycle(nodes: List[Dict], edges: List[Dict]) -> bool:
        """Check if workflow contains a cycle using DFS."""
        graph = {}
        for node in nodes:
            graph[node['id']] = []
        
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source and target:
                graph[source].append(target)
        
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node in nodes:
            node_id = node['id']
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False
