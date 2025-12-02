"""
Error Handler Module

Provides centralized error handling with custom exceptions,
user-friendly error messages, and error recovery mechanisms.

Requirements: 17.1, 17.3, 17.4
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

# Get logger
logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class ValidationError(Exception):
    """Lỗi validation dữ liệu"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message)


class DatabaseError(Exception):
    """Lỗi cơ sở dữ liệu"""
    def __init__(self, message: str, query: Optional[str] = None):
        self.query = query
        super().__init__(message)


class FormulaError(Exception):
    """Lỗi công thức"""
    def __init__(self, message: str, formula: Optional[str] = None):
        self.formula = formula
        super().__init__(message)


class WorkflowError(Exception):
    """Lỗi workflow"""
    def __init__(self, message: str, workflow_id: Optional[int] = None):
        self.workflow_id = workflow_id
        super().__init__(message)


class ConfigurationError(Exception):
    """Lỗi cấu hình"""
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.config_key = config_key
        super().__init__(message)


class ImportExportError(Exception):
    """Lỗi import/export dữ liệu"""
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message)


class TransportConnectionError(Exception):
    """Lỗi kết nối"""
    def __init__(self, message: str, resource: Optional[str] = None):
        self.resource = resource
        super().__init__(message)


# ============================================================================
# Error Handler Class
# ============================================================================

class ErrorHandler:
    """
    Centralized error handling with logging and user-friendly messages.
    
    Provides methods to handle different types of errors consistently
    across the application.
    """
    
    # Error message templates
    ERROR_MESSAGES = {
        ValidationError: "Dữ liệu không hợp lệ",
        DatabaseError: "Lỗi cơ sở dữ liệu",
        FormulaError: "Lỗi công thức tính toán",
        WorkflowError: "Lỗi quy trình làm việc",
        ConfigurationError: "Lỗi cấu hình hệ thống",
        ImportExportError: "Lỗi import/export dữ liệu",
        TransportConnectionError: "Lỗi kết nối",
        Exception: "Lỗi không xác định"
    }
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: str,
        show_dialog: bool = False,
        reraise: bool = False
    ) -> Optional[str]:
        """
        Handle error with logging and optional user notification.
        
        Args:
            error: The exception that occurred
            context: Context description where error occurred
            show_dialog: Whether to show GUI dialog (requires PyQt6)
            reraise: Whether to re-raise the exception after handling
            
        Returns:
            User-friendly error message
        """
        # Get error type and message
        error_type = type(error)
        error_message = str(error)
        
        # Get user-friendly message template
        friendly_message = ErrorHandler.ERROR_MESSAGES.get(
            error_type,
            ErrorHandler.ERROR_MESSAGES[Exception]
        )
        
        # Build full message
        full_message = f"{friendly_message}: {error_message}"
        if context:
            full_message = f"{context}\n{full_message}"
        
        # Log the error with full traceback
        logger.error(
            f"Error in {context}: {error_type.__name__}: {error_message}",
            exc_info=True
        )
        
        # Show dialog if requested
        if show_dialog:
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Lỗi", full_message)
            except ImportError:
                # PyQt6 not available, just log
                logger.warning("PyQt6 not available for error dialog")
        
        # Re-raise if requested
        if reraise:
            raise error
        
        return full_message
    
    @staticmethod
    def handle_validation_error(
        errors: list[str],
        show_dialog: bool = False
    ) -> str:
        """
        Handle validation errors with multiple error messages.
        
        Args:
            errors: List of validation error messages
            show_dialog: Whether to show GUI dialog
            
        Returns:
            Formatted error message
        """
        if not errors:
            return ""
        
        # Format error message
        message = "Dữ liệu không hợp lệ:\n" + "\n".join(f"• {e}" for e in errors)
        
        # Log validation errors
        logger.warning(f"Validation errors: {errors}")
        
        # Show dialog if requested
        if show_dialog:
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Lỗi Validation", message)
            except ImportError:
                logger.warning("PyQt6 not available for validation dialog")
        
        return message
    
    @staticmethod
    def handle_database_error(
        error: Exception,
        query: Optional[str] = None,
        show_dialog: bool = False
    ) -> str:
        """
        Handle database-specific errors.
        
        Args:
            error: The database exception
            query: Optional SQL query that caused the error
            show_dialog: Whether to show GUI dialog
            
        Returns:
            User-friendly error message
        """
        context = "Thao tác cơ sở dữ liệu"
        if query:
            logger.error(f"Database error with query: {query}")
        
        return ErrorHandler.handle_error(error, context, show_dialog)
    
    @staticmethod
    def handle_formula_error(
        error: Exception,
        formula: Optional[str] = None,
        show_dialog: bool = False
    ) -> str:
        """
        Handle formula-specific errors.
        
        Args:
            error: The formula exception
            formula: Optional formula expression that caused the error
            show_dialog: Whether to show GUI dialog
            
        Returns:
            User-friendly error message
        """
        context = "Tính toán công thức"
        if formula:
            logger.error(f"Formula error with expression: {formula}")
        
        return ErrorHandler.handle_error(error, context, show_dialog)
    
    @staticmethod
    def handle_workflow_error(
        error: Exception,
        workflow_id: Optional[int] = None,
        show_dialog: bool = False
    ) -> str:
        """
        Handle workflow-specific errors.
        
        Args:
            error: The workflow exception
            workflow_id: Optional workflow ID that caused the error
            show_dialog: Whether to show GUI dialog
            
        Returns:
            User-friendly error message
        """
        context = "Quy trình làm việc"
        if workflow_id:
            logger.error(f"Workflow error with ID: {workflow_id}")
        
        return ErrorHandler.handle_error(error, context, show_dialog)
    
    @staticmethod
    def safe_execute(
        func: Callable,
        *args,
        default_return: Any = None,
        context: str = "",
        show_dialog: bool = False,
        **kwargs
    ) -> Any:
        """
        Execute a function with error handling and recovery.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            default_return: Value to return if error occurs
            context: Context description
            show_dialog: Whether to show error dialog
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result or default_return if error occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, context or func.__name__, show_dialog)
            return default_return


# ============================================================================
# Decorators for Error Handling
# ============================================================================

def handle_errors(
    context: str = "",
    show_dialog: bool = False,
    default_return: Any = None,
    reraise: bool = False
):
    """
    Decorator to automatically handle errors in functions.
    
    Args:
        context: Context description for error messages
        show_dialog: Whether to show GUI error dialog
        default_return: Value to return if error occurs
        reraise: Whether to re-raise the exception after handling
        
    Example:
        @handle_errors(context="Loading data", show_dialog=True)
        def load_data():
            # ... code that might raise exceptions
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or f"Function: {func.__name__}"
                ErrorHandler.handle_error(e, error_context, show_dialog, reraise)
                return default_return
        return wrapper
    return decorator


def validate_input(validation_func: Callable[[Any], tuple[bool, list[str]]]):
    """
    Decorator to validate function inputs.
    
    Args:
        validation_func: Function that takes the same args as decorated function
                        and returns (is_valid, error_messages)
    
    Example:
        def validate_trip_data(trip_data):
            errors = []
            if not trip_data.get('khach_hang'):
                errors.append("Khách hàng là bắt buộc")
            return len(errors) == 0, errors
        
        @validate_input(validate_trip_data)
        def create_trip(trip_data):
            # ... create trip
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Run validation
            is_valid, errors = validation_func(*args, **kwargs)
            
            if not is_valid:
                error_msg = ErrorHandler.handle_validation_error(errors)
                raise ValidationError(error_msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Recovery Mechanisms
# ============================================================================

class ErrorRecovery:
    """
    Provides error recovery mechanisms for common failure scenarios.
    """
    
    @staticmethod
    def retry_on_error(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry a function on error with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries (seconds)
            exceptions: Tuple of exceptions to catch and retry
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        import time
        
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                )
                
                if attempt < max_retries - 1:
                    time.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff
        
        # All retries failed
        logger.error(f"All {max_retries} retry attempts failed")
        raise last_exception
    
    @staticmethod
    def with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Execute primary function, fall back to alternative on error.
        
        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            exceptions: Tuple of exceptions to catch
            
        Returns:
            Result from primary or fallback function
        """
        try:
            return primary_func()
        except exceptions as e:
            logger.warning(
                f"Primary function failed: {str(e)}, using fallback"
            )
            return fallback_func()
    
    @staticmethod
    def with_transaction_rollback(
        func: Callable,
        connection,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function within a transaction with automatic rollback on error.
        
        Args:
            func: Function to execute
            connection: Database connection object
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Exception after rollback
        """
        try:
            result = func(*args, **kwargs)
            connection.commit()
            return result
        except Exception as e:
            logger.error(f"Transaction failed, rolling back: {str(e)}")
            connection.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")


# ============================================================================
# Utility Functions
# ============================================================================

def get_error_details(error: Exception) -> dict:
    """
    Extract detailed information from an exception.
    
    Args:
        error: The exception to analyze
        
    Returns:
        Dictionary with error details
    """
    return {
        'type': type(error).__name__,
        'message': str(error),
        'traceback': traceback.format_exc(),
        'args': error.args
    }


def format_error_for_user(error: Exception) -> str:
    """
    Format an exception into a user-friendly message.
    
    Args:
        error: The exception to format
        
    Returns:
        User-friendly error message
    """
    error_type = type(error)
    template = ErrorHandler.ERROR_MESSAGES.get(
        error_type,
        ErrorHandler.ERROR_MESSAGES[Exception]
    )
    
    return f"{template}: {str(error)}"
