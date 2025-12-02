"""
Unit tests for Error Handler module

Tests custom exceptions, error handling, and recovery mechanisms.
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
import time

from src.utils.error_handler import (
    ValidationError,
    DatabaseError,
    FormulaError,
    WorkflowError,
    ConfigurationError,
    ImportExportError,
    TransportConnectionError,
    ErrorHandler,
    ErrorRecovery,
    handle_errors,
    validate_input,
    get_error_details,
    format_error_for_user
)


# ============================================================================
# Test Custom Exceptions
# ============================================================================

class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_validation_error_basic(self):
        """Test ValidationError with message only"""
        error = ValidationError("Invalid data")
        assert str(error) == "Invalid data"
        assert error.field is None
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field information"""
        error = ValidationError("Invalid email", field="email")
        assert str(error) == "Invalid email"
        assert error.field == "email"
    
    def test_database_error_basic(self):
        """Test DatabaseError with message only"""
        error = DatabaseError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.query is None
    
    def test_database_error_with_query(self):
        """Test DatabaseError with query information"""
        query = "SELECT * FROM trips"
        error = DatabaseError("Query failed", query=query)
        assert str(error) == "Query failed"
        assert error.query == query
    
    def test_formula_error_basic(self):
        """Test FormulaError with message only"""
        error = FormulaError("Division by zero")
        assert str(error) == "Division by zero"
        assert error.formula is None
    
    def test_formula_error_with_formula(self):
        """Test FormulaError with formula information"""
        formula = "[A] / [B]"
        error = FormulaError("Invalid operation", formula=formula)
        assert str(error) == "Invalid operation"
        assert error.formula == formula
    
    def test_workflow_error_basic(self):
        """Test WorkflowError with message only"""
        error = WorkflowError("Workflow failed")
        assert str(error) == "Workflow failed"
        assert error.workflow_id is None
    
    def test_workflow_error_with_id(self):
        """Test WorkflowError with workflow ID"""
        error = WorkflowError("Push failed", workflow_id=123)
        assert str(error) == "Push failed"
        assert error.workflow_id == 123
    
    def test_configuration_error_basic(self):
        """Test ConfigurationError with message only"""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert error.config_key is None
    
    def test_configuration_error_with_key(self):
        """Test ConfigurationError with config key"""
        error = ConfigurationError("Missing value", config_key="database.path")
        assert str(error) == "Missing value"
        assert error.config_key == "database.path"
    
    def test_import_export_error_basic(self):
        """Test ImportExportError with message only"""
        error = ImportExportError("Import failed")
        assert str(error) == "Import failed"
        assert error.file_path is None
    
    def test_import_export_error_with_path(self):
        """Test ImportExportError with file path"""
        error = ImportExportError("File not found", file_path="/path/to/file.xlsx")
        assert str(error) == "File not found"
        assert error.file_path == "/path/to/file.xlsx"
    
    def test_connection_error_basic(self):
        """Test TransportConnectionError with message only"""
        error = TransportConnectionError("Connection timeout")
        assert str(error) == "Connection timeout"
        assert error.resource is None
    
    def test_connection_error_with_resource(self):
        """Test TransportConnectionError with resource information"""
        error = TransportConnectionError("Cannot connect", resource="database")
        assert str(error) == "Cannot connect"
        assert error.resource == "database"


# ============================================================================
# Test ErrorHandler Class
# ============================================================================

class TestErrorHandler:
    """Test ErrorHandler class methods"""
    
    def test_handle_error_basic(self, caplog):
        """Test basic error handling"""
        error = ValueError("Test error")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_error(error, "Test context")
        
        assert "Lỗi không xác định: Test error" in result
        assert "Test context" in result
        assert "Test error" in caplog.text
    
    def test_handle_error_validation(self, caplog):
        """Test handling ValidationError"""
        error = ValidationError("Invalid input")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_error(error, "Validation")
        
        assert "Dữ liệu không hợp lệ" in result
        assert "Invalid input" in result
    
    def test_handle_error_database(self, caplog):
        """Test handling DatabaseError"""
        error = DatabaseError("Query failed")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_error(error, "Database operation")
        
        assert "Lỗi cơ sở dữ liệu" in result
        assert "Query failed" in result
    
    def test_handle_error_formula(self, caplog):
        """Test handling FormulaError"""
        error = FormulaError("Invalid syntax")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_error(error, "Formula calculation")
        
        assert "Lỗi công thức tính toán" in result
        assert "Invalid syntax" in result
    
    def test_handle_error_reraise(self):
        """Test error re-raising"""
        error = ValueError("Test error")
        with pytest.raises(ValueError):
            ErrorHandler.handle_error(error, "Test", reraise=True)
    
    def test_handle_validation_error_single(self, caplog):
        """Test handling single validation error"""
        errors = ["Field is required"]
        with caplog.at_level(logging.WARNING):
            result = ErrorHandler.handle_validation_error(errors)
        
        assert "Dữ liệu không hợp lệ" in result
        assert "• Field is required" in result
    
    def test_handle_validation_error_multiple(self, caplog):
        """Test handling multiple validation errors"""
        errors = ["Field A is required", "Field B is invalid", "Field C too long"]
        with caplog.at_level(logging.WARNING):
            result = ErrorHandler.handle_validation_error(errors)
        
        assert "Dữ liệu không hợp lệ" in result
        assert "• Field A is required" in result
        assert "• Field B is invalid" in result
        assert "• Field C too long" in result
    
    def test_handle_validation_error_empty(self):
        """Test handling empty validation errors"""
        result = ErrorHandler.handle_validation_error([])
        assert result == ""
    
    def test_handle_database_error(self, caplog):
        """Test database-specific error handling"""
        error = DatabaseError("Connection lost")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_database_error(error)
        
        assert "Lỗi cơ sở dữ liệu" in result
        assert "Connection lost" in result
    
    def test_handle_database_error_with_query(self, caplog):
        """Test database error with query logging"""
        error = DatabaseError("Query failed")
        query = "SELECT * FROM trips WHERE id = ?"
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_database_error(error, query=query)
        
        assert "Lỗi cơ sở dữ liệu" in result
        assert query in caplog.text
    
    def test_handle_formula_error(self, caplog):
        """Test formula-specific error handling"""
        error = FormulaError("Division by zero")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_formula_error(error)
        
        assert "Lỗi công thức tính toán" in result
        assert "Division by zero" in result
    
    def test_handle_formula_error_with_formula(self, caplog):
        """Test formula error with formula logging"""
        error = FormulaError("Invalid syntax")
        formula = "[A] + [B"
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_formula_error(error, formula=formula)
        
        assert "Lỗi công thức tính toán" in result
        assert formula in caplog.text
    
    def test_handle_workflow_error(self, caplog):
        """Test workflow-specific error handling"""
        error = WorkflowError("Push failed")
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_workflow_error(error)
        
        assert "Lỗi quy trình làm việc" in result
        assert "Push failed" in result
    
    def test_handle_workflow_error_with_id(self, caplog):
        """Test workflow error with ID logging"""
        error = WorkflowError("Condition not met")
        workflow_id = 456
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.handle_workflow_error(error, workflow_id=workflow_id)
        
        assert "Lỗi quy trình làm việc" in result
        assert str(workflow_id) in caplog.text
    
    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""
        def successful_func(x, y):
            return x + y
        
        result = ErrorHandler.safe_execute(successful_func, 5, 10)
        assert result == 15
    
    def test_safe_execute_with_error(self, caplog):
        """Test safe_execute with failing function"""
        def failing_func():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            result = ErrorHandler.safe_execute(
                failing_func,
                default_return="default"
            )
        
        assert result == "default"
        assert "Test error" in caplog.text
    
    def test_safe_execute_with_context(self, caplog):
        """Test safe_execute with custom context"""
        def failing_func():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            ErrorHandler.safe_execute(
                failing_func,
                context="Custom context",
                default_return=None
            )
        
        assert "Custom context" in caplog.text


# ============================================================================
# Test Decorators
# ============================================================================

class TestDecorators:
    """Test error handling decorators"""
    
    def test_handle_errors_decorator_success(self):
        """Test handle_errors decorator with successful function"""
        @handle_errors(context="Test function")
        def successful_func(x):
            return x * 2
        
        result = successful_func(5)
        assert result == 10
    
    def test_handle_errors_decorator_with_error(self, caplog):
        """Test handle_errors decorator with failing function"""
        @handle_errors(context="Test function", default_return=0)
        def failing_func():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            result = failing_func()
        
        assert result == 0
        assert "Test error" in caplog.text
    
    def test_handle_errors_decorator_reraise(self):
        """Test handle_errors decorator with reraise"""
        @handle_errors(context="Test function", reraise=True)
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_func()
    
    def test_validate_input_decorator_valid(self):
        """Test validate_input decorator with valid input"""
        def validator(data):
            errors = []
            if not data.get('name'):
                errors.append("Name is required")
            return len(errors) == 0, errors
        
        @validate_input(validator)
        def process_data(data):
            return f"Processed: {data['name']}"
        
        result = process_data({'name': 'Test'})
        assert result == "Processed: Test"
    
    def test_validate_input_decorator_invalid(self):
        """Test validate_input decorator with invalid input"""
        def validator(data):
            errors = []
            if not data.get('name'):
                errors.append("Name is required")
            return len(errors) == 0, errors
        
        @validate_input(validator)
        def process_data(data):
            return f"Processed: {data['name']}"
        
        with pytest.raises(ValidationError):
            process_data({})


# ============================================================================
# Test ErrorRecovery Class
# ============================================================================

class TestErrorRecovery:
    """Test ErrorRecovery class methods"""
    
    def test_retry_on_error_success_first_try(self):
        """Test retry with success on first attempt"""
        mock_func = Mock(return_value="success")
        
        result = ErrorRecovery.retry_on_error(mock_func, max_retries=3)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_on_error_success_after_retries(self, caplog):
        """Test retry with success after failures"""
        mock_func = Mock(side_effect=[ValueError("Error 1"), ValueError("Error 2"), "success"])
        
        with caplog.at_level(logging.WARNING):
            result = ErrorRecovery.retry_on_error(
                mock_func,
                max_retries=3,
                delay=0.01
            )
        
        assert result == "success"
        assert mock_func.call_count == 3
        assert "Attempt 1/3 failed" in caplog.text
        assert "Attempt 2/3 failed" in caplog.text
    
    def test_retry_on_error_all_fail(self, caplog):
        """Test retry with all attempts failing"""
        mock_func = Mock(side_effect=ValueError("Persistent error"))
        
        with caplog.at_level(logging.WARNING):
            with pytest.raises(ValueError, match="Persistent error"):
                ErrorRecovery.retry_on_error(
                    mock_func,
                    max_retries=3,
                    delay=0.01
                )
        
        assert mock_func.call_count == 3
        assert "All 3 retry attempts failed" in caplog.text
    
    def test_with_fallback_primary_success(self):
        """Test fallback with primary function succeeding"""
        primary = Mock(return_value="primary result")
        fallback = Mock(return_value="fallback result")
        
        result = ErrorRecovery.with_fallback(primary, fallback)
        
        assert result == "primary result"
        assert primary.call_count == 1
        assert fallback.call_count == 0
    
    def test_with_fallback_primary_fails(self, caplog):
        """Test fallback with primary function failing"""
        primary = Mock(side_effect=ValueError("Primary failed"))
        fallback = Mock(return_value="fallback result")
        
        with caplog.at_level(logging.WARNING):
            result = ErrorRecovery.with_fallback(primary, fallback)
        
        assert result == "fallback result"
        assert primary.call_count == 1
        assert fallback.call_count == 1
        assert "using fallback" in caplog.text
    
    def test_with_transaction_rollback_success(self):
        """Test transaction with successful execution"""
        mock_conn = Mock()
        
        def successful_operation():
            return "success"
        
        result = ErrorRecovery.with_transaction_rollback(
            successful_operation,
            mock_conn
        )
        
        assert result == "success"
        assert mock_conn.commit.call_count == 1
        assert mock_conn.rollback.call_count == 0
    
    def test_with_transaction_rollback_failure(self, caplog):
        """Test transaction with failed execution"""
        mock_conn = Mock()
        
        def failing_operation():
            raise ValueError("Operation failed")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(DatabaseError):
                ErrorRecovery.with_transaction_rollback(
                    failing_operation,
                    mock_conn
                )
        
        assert mock_conn.commit.call_count == 0
        assert mock_conn.rollback.call_count == 1
        assert "rolling back" in caplog.text


# ============================================================================
# Test Utility Functions
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_get_error_details(self):
        """Test extracting error details"""
        error = ValueError("Test error message")
        details = get_error_details(error)
        
        assert details['type'] == 'ValueError'
        assert details['message'] == 'Test error message'
        assert 'traceback' in details
        assert details['args'] == ('Test error message',)
    
    def test_format_error_for_user_validation(self):
        """Test formatting ValidationError for user"""
        error = ValidationError("Invalid data")
        message = format_error_for_user(error)
        
        assert "Dữ liệu không hợp lệ" in message
        assert "Invalid data" in message
    
    def test_format_error_for_user_database(self):
        """Test formatting DatabaseError for user"""
        error = DatabaseError("Connection failed")
        message = format_error_for_user(error)
        
        assert "Lỗi cơ sở dữ liệu" in message
        assert "Connection failed" in message
    
    def test_format_error_for_user_generic(self):
        """Test formatting generic exception for user"""
        error = RuntimeError("Something went wrong")
        message = format_error_for_user(error)
        
        assert "Lỗi không xác định" in message
        assert "Something went wrong" in message


# ============================================================================
# Integration Tests
# ============================================================================

class TestErrorHandlerIntegration:
    """Integration tests for error handler"""
    
    def test_full_error_handling_workflow(self, caplog):
        """Test complete error handling workflow"""
        @handle_errors(context="Data processing", default_return=None)
        def process_with_validation(data):
            # Validate
            if not data:
                raise ValidationError("Data is empty")
            
            # Process
            if data.get('invalid'):
                raise ValueError("Invalid data structure")
            
            return f"Processed: {data.get('value')}"
        
        # Test success
        result = process_with_validation({'value': 'test'})
        assert result == "Processed: test"
        
        # Test validation error
        with caplog.at_level(logging.ERROR):
            result = process_with_validation({})
        assert result is None
        assert "Data is empty" in caplog.text
        
        # Test generic error
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            result = process_with_validation({'invalid': True})
        assert result is None
        assert "Invalid data structure" in caplog.text
    
    def test_nested_error_handling(self, caplog):
        """Test nested error handling scenarios"""
        def inner_function():
            raise DatabaseError("Database connection lost")
        
        @handle_errors(context="Outer function", default_return="recovered")
        def outer_function():
            try:
                inner_function()
            except DatabaseError as e:
                ErrorHandler.handle_database_error(e)
                raise
        
        with caplog.at_level(logging.ERROR):
            result = outer_function()
        
        assert result == "recovered"
        assert "Database connection lost" in caplog.text
