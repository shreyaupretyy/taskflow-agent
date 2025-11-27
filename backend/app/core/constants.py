"""Constants used throughout the application."""

# Workflow execution statuses
WORKFLOW_STATUS_PENDING = "pending"
WORKFLOW_STATUS_RUNNING = "running"
WORKFLOW_STATUS_COMPLETED = "completed"
WORKFLOW_STATUS_FAILED = "failed"
WORKFLOW_STATUS_CANCELLED = "cancelled"

WORKFLOW_STATUSES = [
    WORKFLOW_STATUS_PENDING,
    WORKFLOW_STATUS_RUNNING,
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_CANCELLED,
]

# Node execution statuses
NODE_STATUS_SUCCESS = "success"
NODE_STATUS_ERROR = "error"
NODE_STATUS_RUNNING = "running"

# Trigger types
TRIGGER_MANUAL = "manual"
TRIGGER_SCHEDULE = "schedule"
TRIGGER_WEBHOOK = "webhook"

TRIGGER_TYPES = [
    TRIGGER_MANUAL,
    TRIGGER_SCHEDULE,
    TRIGGER_WEBHOOK,
]

# User roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_SUPERUSER = "superuser"

USER_ROLES = [
    ROLE_USER,
    ROLE_ADMIN,
    ROLE_SUPERUSER,
]

# Log levels
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"

LOG_LEVELS = [
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
]

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache TTL (seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# File upload limits
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = ['.json', '.csv', '.txt', '.pdf']

# API versioning
API_VERSION = "v1"
