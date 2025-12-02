"""
Logging configuration for Transport Management System

Provides comprehensive logging with:
- File rotation
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Structured logging
- Performance logging

Requirements: 17.2
"""

import logging
import sys
import time
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import contextmanager

import config


# ============================================================================
# Structured Logging Formatter
# ============================================================================

class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs structured log data in JSON format.
    Useful for log aggregation and analysis tools.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON structure"""
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


# ============================================================================
# Performance Logging
# ============================================================================

class PerformanceLogger:
    """
    Logger for tracking performance metrics.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log performance metrics for an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            details: Additional details about the operation
        """
        message = f"Performance: {operation} took {duration:.4f}s"
        
        extra_data = {
            'operation': operation,
            'duration_seconds': duration,
            'duration_ms': duration * 1000
        }
        
        if details:
            extra_data.update(details)
        
        # Log as INFO if fast, WARNING if slow
        if duration > 1.0:
            self.logger.warning(message, extra={'extra_data': extra_data})
        else:
            self.logger.info(message, extra={'extra_data': extra_data})
    
    def log_query(
        self,
        query: str,
        duration: float,
        row_count: Optional[int] = None
    ):
        """
        Log database query performance.
        
        Args:
            query: SQL query (truncated for logging)
            duration: Query duration in seconds
            row_count: Number of rows returned/affected
        """
        # Truncate long queries
        query_preview = query[:100] + "..." if len(query) > 100 else query
        
        details = {
            'query_preview': query_preview,
            'row_count': row_count
        }
        
        self.log_operation(f"Query: {query_preview}", duration, details)
    
    def log_ui_operation(
        self,
        widget: str,
        action: str,
        duration: float
    ):
        """
        Log UI operation performance.
        
        Args:
            widget: Widget name
            action: Action performed
            duration: Duration in seconds
        """
        details = {
            'widget': widget,
            'action': action
        }
        
        self.log_operation(f"UI: {widget}.{action}", duration, details)


# ============================================================================
# Setup Functions
# ============================================================================

def setup_logging(
    enable_structured: bool = False,
    enable_performance: bool = True
):
    """
    Setup logging configuration with file rotation and console output.
    
    Supports multiple log levels:
    - DEBUG: Detailed information for debugging
    - INFO: General informational messages
    - WARNING: Warning messages for potential issues
    - ERROR: Error messages for failures
    
    Args:
        enable_structured: Enable JSON structured logging
        enable_performance: Enable performance logging
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("TransportApp")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    if enable_structured:
        file_formatter = StructuredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_formatter = logging.Formatter(
        "%(levelname)s - %(message)s"
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup
    logger.info("=" * 80)
    logger.info(f"Transport Management System - Logging initialized")
    logger.info(f"Log level: {config.LOG_LEVEL}")
    logger.info(f"Log file: {config.LOG_FILE}")
    logger.info(f"Structured logging: {enable_structured}")
    logger.info(f"Performance logging: {enable_performance}")
    logger.info("=" * 80)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (optional)
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"TransportApp.{name}")
    return logging.getLogger("TransportApp")


def get_performance_logger(name: str = None) -> PerformanceLogger:
    """
    Get a performance logger instance.
    
    Args:
        name: Logger name (optional)
    
    Returns:
        PerformanceLogger instance
    """
    logger = get_logger(name)
    return PerformanceLogger(logger)


# ============================================================================
# Decorators for Logging
# ============================================================================

def log_function_call(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function calls with arguments and return values.
    
    Args:
        logger: Logger instance (optional, will use default if not provided)
    
    Example:
        @log_function_call()
        def my_function(arg1, arg2):
            return arg1 + arg2
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            
            # Log function call
            log.debug(
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            
            try:
                result = func(*args, **kwargs)
                log.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                log.error(
                    f"{func.__name__} raised {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_performance(
    operation_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to log function execution time.
    
    Args:
        operation_name: Name for the operation (defaults to function name)
        logger: Logger instance (optional)
    
    Example:
        @log_performance("Database query")
        def query_database():
            # ... query code
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            perf_logger = PerformanceLogger(log)
            
            op_name = operation_name or func.__name__
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                perf_logger.log_operation(op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log.error(
                    f"{op_name} failed after {duration:.4f}s: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


@contextmanager
def log_context(
    operation: str,
    logger: Optional[logging.Logger] = None,
    log_performance: bool = True
):
    """
    Context manager for logging operations with automatic timing.
    
    Args:
        operation: Name of the operation
        logger: Logger instance (optional)
        log_performance: Whether to log performance metrics
    
    Example:
        with log_context("Loading data"):
            data = load_data()
    """
    log = logger or get_logger()
    
    log.info(f"Starting: {operation}")
    start_time = time.time()
    
    try:
        yield
        duration = time.time() - start_time
        
        if log_performance:
            perf_logger = PerformanceLogger(log)
            perf_logger.log_operation(operation, duration)
        else:
            log.info(f"Completed: {operation} ({duration:.4f}s)")
    
    except Exception as e:
        duration = time.time() - start_time
        log.error(
            f"Failed: {operation} after {duration:.4f}s - {str(e)}",
            exc_info=True
        )
        raise


# ============================================================================
# Utility Functions
# ============================================================================

def log_system_info(logger: Optional[logging.Logger] = None):
    """
    Log system information for debugging purposes.
    
    Args:
        logger: Logger instance (optional)
    """
    import platform
    import sys
    
    log = logger or get_logger()
    
    log.info("System Information:")
    log.info(f"  Platform: {platform.platform()}")
    log.info(f"  Python: {sys.version}")
    log.info(f"  Architecture: {platform.machine()}")
    log.info(f"  Processor: {platform.processor()}")


def set_log_level(level: str, logger: Optional[logging.Logger] = None):
    """
    Change log level at runtime.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        logger: Logger instance (optional)
    """
    log = logger or get_logger()
    log.setLevel(getattr(logging, level.upper()))
    log.info(f"Log level changed to: {level.upper()}")
