"""Node execution utilities."""
from typing import Dict, Any
import asyncio
import httpx


async def execute_http_request(config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute HTTP request node."""
    method = config.get('method', 'GET').upper()
    url = config.get('url')
    headers = config.get('headers', {})
    body = config.get('body')
    timeout = config.get('timeout', 30)
    
    if not url:
        raise ValueError("URL is required for HTTP request")
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        if method == 'GET':
            response = await client.get(url, headers=headers)
        elif method == 'POST':
            response = await client.post(url, headers=headers, json=body)
        elif method == 'PUT':
            response = await client.put(url, headers=headers, json=body)
        elif method == 'DELETE':
            response = await client.delete(url, headers=headers)
        elif method == 'PATCH':
            response = await client.patch(url, headers=headers, json=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    return {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'body': response.text,
        'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
    }


async def execute_delay(config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute delay node."""
    duration = config.get('duration', 0)
    unit = config.get('unit', 'seconds')
    
    # Convert to seconds
    multipliers = {
        'seconds': 1,
        'minutes': 60,
        'hours': 3600
    }
    
    delay_seconds = duration * multipliers.get(unit, 1)
    await asyncio.sleep(delay_seconds)
    
    return {
        'delayed': delay_seconds,
        'unit': 'seconds'
    }


def evaluate_condition(config: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Evaluate condition node."""
    left = resolve_value(config.get('left'), context)
    right = resolve_value(config.get('right'), context)
    operator = config.get('operator')
    
    operators = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '>=': lambda a, b: a >= b,
        '<': lambda a, b: a < b,
        '<=': lambda a, b: a <= b,
        'contains': lambda a, b: b in str(a),
        'starts_with': lambda a, b: str(a).startswith(str(b)),
        'ends_with': lambda a, b: str(a).endswith(str(b))
    }
    
    if operator not in operators:
        raise ValueError(f"Unknown operator: {operator}")
    
    return operators[operator](left, right)


def resolve_value(value: Any, context: Dict[str, Any]) -> Any:
    """Resolve variable references in values."""
    if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
        var_name = value[2:-2].strip()
        return context.get(var_name, value)
    return value
