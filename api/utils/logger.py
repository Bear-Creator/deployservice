"""Logging utilities for the DeployService API."""

import sys
from typing import Any, Callable, Dict, List, Union

import structlog
from structlog.types import Processor

from api.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Define processors for structured logging
    processors: List[Union[Processor, Callable[..., Any]]] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    import logging

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger


def log_request(
    logger: structlog.stdlib.BoundLogger, request_data: Dict[str, Any]
) -> None:
    """Log incoming request data."""
    logger.info(
        "Incoming request",
        endpoint=request_data.get("endpoint"),
        server_ip=request_data.get("server_ip"),
        operation=request_data.get("operation"),
    )


def log_response(
    logger: structlog.stdlib.BoundLogger, response_data: Dict[str, Any]
) -> None:
    """Log response data."""
    logger.info(
        "Response sent",
        status=response_data.get("status"),
        server_ip=response_data.get("server_ip"),
        operation=response_data.get("operation"),
    )


def log_error(
    logger: structlog.stdlib.BoundLogger, error: Exception, context: Dict[str, Any]
) -> None:
    """Log error with context."""
    logger.error(
        "Operation failed",
        error=str(error),
        error_type=type(error).__name__,
        **context,
        exc_info=True,
    )
