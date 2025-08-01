"""Custom exception classes for MetaClaude with enhanced error handling.

This module provides a comprehensive hierarchy of custom exceptions for different
failure scenarios in the MetaClaude system, with helpful error messages and recovery hints.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(Enum):
    """Categories of MetaClaude errors for better classification."""
    DOCKER = "docker"
    TEMPLATE = "template"
    AGENT = "agent"
    CONFIGURATION = "configuration"
    EXECUTION = "execution"
    TIMEOUT = "timeout"
    NETWORK = "network"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RESOURCE = "resource"


class MetaClaudeError(Exception):
    """Base exception for all MetaClaude errors with enhanced context."""
    
    def __init__(
        self,
        message: str,
        category: Optional[ErrorCategory] = None,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize MetaClaude error with enhanced information.
        
        Args:
            message: Primary error message
            category: Error category for classification
            recovery_hint: Suggestion for resolving the error
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.category = category
        self.recovery_hint = recovery_hint
        self.context = context or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [super().__str__()]
        
        if self.recovery_hint:
            parts.append(f"💡 Suggestion: {self.recovery_hint}")
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "type": self.__class__.__name__,
            "message": str(super()),
            "category": self.category.value if self.category else None,
            "recovery_hint": self.recovery_hint,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class MetaClaudeDockerError(MetaClaudeError):
    """Exception for Docker-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Ensure Docker is running and accessible. "
                "Check Docker daemon status with 'docker info'."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.DOCKER,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeTemplateError(MetaClaudeError):
    """Exception for template-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check template syntax and ensure all required variables are defined. "
                "Use 'metaclaude validate' to check template integrity."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.TEMPLATE,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeAgentError(MetaClaudeError):
    """Exception for agent-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check agent configuration and ensure all required agents are available. "
                "Use 'metaclaude agents' to list available agents."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.AGENT,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeConfigError(MetaClaudeError):
    """Exception for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check configuration file syntax and ensure all required settings are present. "
                "See documentation for configuration examples."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeExecutionError(MetaClaudeError):
    """Exception for execution-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check system resources and ensure all dependencies are available. "
                "Try running with --verbose for detailed execution logs."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.EXECUTION,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeTimeoutError(MetaClaudeError):
    """Exception for timeout-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Increase timeout with --timeout flag or use 'unlimited' for complex projects. "
                "Consider simplifying the project scope for faster generation."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeNetworkError(MetaClaudeError):
    """Exception for network-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check internet connection and proxy settings. "
                "Ensure Claude API endpoints are accessible."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeValidationError(MetaClaudeError):
    """Exception for validation-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check input parameters and ensure they meet the required format. "
                "Use --help for parameter documentation."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeAuthenticationError(MetaClaudeError):
    """Exception for authentication-related errors."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Check ANTHROPIC_API_KEY environment variable is set correctly. "
                "Verify API key has sufficient permissions."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


class MetaClaudeResourceError(MetaClaudeError):
    """Exception for resource-related errors (disk, memory, etc.)."""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if not recovery_hint:
            recovery_hint = (
                "Free up system resources (disk space, memory) and try again. "
                "Consider using a smaller project scope or cloud environment."
            )
        
        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            recovery_hint=recovery_hint,
            context=context,
            cause=cause,
        )


def handle_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    operation: Optional[str] = None,
) -> MetaClaudeError:
    """Convert generic exceptions to MetaClaude errors with context.
    
    Args:
        exc: Original exception
        context: Additional context information
        operation: Description of operation that failed
        
    Returns:
        Appropriate MetaClaude error with enhanced information
    """
    if isinstance(exc, MetaClaudeError):
        return exc
    
    # Map common exception types to MetaClaude errors
    error_mapping = {
        ConnectionError: MetaClaudeNetworkError,
        TimeoutError: MetaClaudeTimeoutError,
        PermissionError: MetaClaudeResourceError,
        FileNotFoundError: MetaClaudeConfigError,
        ValueError: MetaClaudeValidationError,
    }
    
    error_class = error_mapping.get(type(exc), MetaClaudeExecutionError)
    
    message = f"{operation}: {exc}" if operation else str(exc)
    
    return error_class(
        message=message,
        context=context,
        cause=exc,
    )