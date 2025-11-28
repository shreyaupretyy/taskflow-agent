"""Custom exception classes for the application."""


class TaskFlowException(Exception):
    """Base exception for TaskFlow application."""

    pass


class WorkflowNotFoundException(TaskFlowException):
    """Raised when a workflow is not found."""

    pass


class WorkflowExecutionException(TaskFlowException):
    """Raised when workflow execution fails."""

    pass


class NodeExecutionException(TaskFlowException):
    """Raised when a node execution fails."""

    pass


class ValidationException(TaskFlowException):
    """Raised when validation fails."""

    pass


class AuthenticationException(TaskFlowException):
    """Raised when authentication fails."""

    pass


class AuthorizationException(TaskFlowException):
    """Raised when authorization fails."""

    pass


class RateLimitException(TaskFlowException):
    """Raised when rate limit is exceeded."""

    pass


class ConfigurationException(TaskFlowException):
    """Raised when configuration is invalid."""

    pass


class DatabaseException(TaskFlowException):
    """Raised when database operation fails."""

    pass


class ExternalServiceException(TaskFlowException):
    """Raised when external service call fails."""

    pass
