"""Environment configuration validation."""
from typing import Optional
import os


class ConfigValidator:
    """Validate environment configuration."""
    
    REQUIRED_VARS = [
        'DATABASE_URL',
        'SECRET_KEY',
        'REDIS_URL'
    ]
    
    OPTIONAL_VARS = {
        'ENVIRONMENT': 'development',
        'DEBUG': 'false',
        'CORS_ORIGINS': '*',
        'SMTP_HOST': '',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': '',
        'SMTP_PASSWORD': '',
        'OLLAMA_BASE_URL': 'http://localhost:11434',
        'CHROMA_PERSIST_DIR': './chroma_db'
    }
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate environment configuration.
        
        Returns:
            Tuple of (is_valid, missing_vars)
        """
        missing = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        return len(missing) == 0, missing
    
    @classmethod
    def get_config(cls) -> dict:
        """Get all configuration values."""
        config = {}
        
        # Required variables
        for var in cls.REQUIRED_VARS:
            config[var] = os.getenv(var)
        
        # Optional variables with defaults
        for var, default in cls.OPTIONAL_VARS.items():
            config[var] = os.getenv(var, default)
        
        return config
    
    @classmethod
    def validate_database_url(cls, url: str) -> bool:
        """Validate database URL format."""
        if not url:
            return False
        
        valid_schemes = ['postgresql://', 'postgresql+psycopg2://', 'sqlite:///']
        return any(url.startswith(scheme) for scheme in valid_schemes)
    
    @classmethod
    def validate_redis_url(cls, url: str) -> bool:
        """Validate Redis URL format."""
        if not url:
            return False
        
        return url.startswith('redis://') or url.startswith('rediss://')
