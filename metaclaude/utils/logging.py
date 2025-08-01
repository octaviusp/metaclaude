"""Logging configuration for MetaClaude."""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

console = Console()

# Configure logging levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Global logger configuration
_loggers = {}
_log_file: Optional[Path] = None
_log_level = logging.INFO


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    verbose: bool = False,
) -> None:
    """Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        verbose: Enable verbose logging
    """
    global _log_level, _log_file
    
    _log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    _log_file = log_file
    
    if verbose:
        _log_level = logging.DEBUG
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(_log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add rich console handler
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(_log_level)
    
    console_format = logging.Formatter(
        fmt="%(message)s",
        datefmt="[%X]",
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(_log_level)
        
        file_format = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        logger.setLevel(_log_level)
        _loggers[name] = logger
    
    return _loggers[name]


def log_execution_start(operation: str, details: dict = None) -> None:
    """Log the start of an operation.
    
    Args:
        operation: Operation name
        details: Optional operation details
    """
    logger = get_logger("metaclaude.execution")
    details_str = f" ({details})" if details else ""
    logger.info(f"🚀 Starting {operation}{details_str}")


def log_execution_complete(operation: str, duration: float = None, details: dict = None) -> None:
    """Log the completion of an operation.
    
    Args:
        operation: Operation name
        duration: Optional operation duration in seconds
        details: Optional operation details
    """
    logger = get_logger("metaclaude.execution")
    duration_str = f" in {duration:.2f}s" if duration else ""
    details_str = f" ({details})" if details else ""
    logger.info(f"✅ Completed {operation}{duration_str}{details_str}")


def log_execution_error(operation: str, error: Exception, details: dict = None) -> None:
    """Log an execution error.
    
    Args:
        operation: Operation name
        error: The error that occurred
        details: Optional operation details
    """
    logger = get_logger("metaclaude.execution")
    details_str = f" ({details})" if details else ""
    logger.error(f"❌ Failed {operation}{details_str}: {error}")


def log_docker_event(event: str, container_id: str = None, details: dict = None) -> None:
    """Log Docker-related events.
    
    Args:
        event: Event description
        container_id: Optional container ID
        details: Optional event details
    """
    logger = get_logger("metaclaude.docker")
    container_str = f" [{container_id[:12]}]" if container_id else ""
    details_str = f" - {details}" if details else ""
    logger.info(f"🐳 {event}{container_str}{details_str}")


def log_agent_event(agent_name: str, event: str, details: dict = None) -> None:
    """Log agent-related events.
    
    Args:
        agent_name: Agent name
        event: Event description
        details: Optional event details
    """
    logger = get_logger("metaclaude.agents")
    details_str = f" - {details}" if details else ""
    logger.info(f"🤖 [{agent_name}] {event}{details_str}")


def log_template_event(template_name: str, event: str, details: dict = None) -> None:
    """Log template-related events.
    
    Args:
        template_name: Template name
        event: Event description
        details: Optional event details
    """
    logger = get_logger("metaclaude.templates")
    details_str = f" - {details}" if details else ""
    logger.info(f"📋 [{template_name}] {event}{details_str}")


def log_cost_info(tokens_used: int, estimated_cost: float, model: str) -> None:
    """Log token usage and cost information.
    
    Args:
        tokens_used: Number of tokens used
        estimated_cost: Estimated cost in USD
        model: Model name
    """
    logger = get_logger("metaclaude.cost")
    logger.info(f"💰 {model}: {tokens_used:,} tokens, ~${estimated_cost:.4f}")


def log_progress(current: int, total: int, operation: str) -> None:
    """Log progress information.
    
    Args:
        current: Current progress
        total: Total items
        operation: Operation description
    """
    logger = get_logger("metaclaude.progress")
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f"⏳ {operation}: {current}/{total} ({percentage:.1f}%)")


# Initialize with default settings
setup_logging()