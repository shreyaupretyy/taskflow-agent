"""Monitoring and metrics for the application."""
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps


# Define metrics
workflow_executions_total = Counter(
    'workflow_executions_total',
    'Total number of workflow executions',
    ['status']
)

workflow_execution_duration = Histogram(
    'workflow_execution_duration_seconds',
    'Workflow execution duration in seconds'
)

active_workflows = Gauge(
    'active_workflows',
    'Number of currently active workflows'
)

node_executions_total = Counter(
    'node_executions_total',
    'Total number of node executions',
    ['node_type', 'status']
)

api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)


def track_workflow_execution(func):
    """Decorator to track workflow execution metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status = 'failed'
        
        try:
            result = await func(*args, **kwargs)
            status = 'completed'
            return result
        except Exception as e:
            status = 'failed'
            raise e
        finally:
            duration = time.time() - start_time
            workflow_executions_total.labels(status=status).inc()
            workflow_execution_duration.observe(duration)
    
    return wrapper


def track_api_request(method: str, endpoint: str):
    """Decorator to track API request metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                raise e
            finally:
                duration = time.time() - start_time
                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator
