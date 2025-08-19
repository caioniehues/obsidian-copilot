"""
Custom exception classes for Obsidian Copilot.
Provides specific error types for better error handling and debugging.
"""

from typing import Optional, Any, Dict


class CopilotError(Exception):
    """Base exception class for Obsidian Copilot errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ServiceUnavailableError(CopilotError):
    """Raised when external services are unavailable."""
    pass


class OpenSearchError(ServiceUnavailableError):
    """Raised when OpenSearch operations fail."""
    pass


class RedisError(ServiceUnavailableError):
    """Raised when Redis operations fail."""
    pass


class DataValidationError(CopilotError):
    """Raised when data validation fails."""
    pass


class FileNotFoundError(CopilotError):
    """Raised when required files are missing."""
    pass


class ModelLoadError(CopilotError):
    """Raised when ML models fail to load."""
    pass


class AgentExecutionError(CopilotError):
    """Raised when agent execution fails."""
    pass


class ConfigurationError(CopilotError):
    """Raised when configuration is invalid."""
    pass


class TimeoutError(CopilotError):
    """Raised when operations timeout."""
    pass


class APIClientError(CopilotError):
    """Raised when API client operations fail."""
    pass