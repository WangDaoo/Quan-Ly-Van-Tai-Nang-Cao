"""
Unit tests for Error Handling and Logging

Tests for Task 15: Implement Error Handling và Logging
"""

import pytest
import logging
from pathlib import Path
from src.utils.logger import setup_logging, get_logger, get_performance_logger, log_context
from src.utils.error_handler import (
    ErrorHandler,
    ValidationError,
    DatabaseError,
    FormulaError,
    handle_errors,
    ErrorRecovery
)
from src.utils.validation import (
    Validator,
    validate_required,
    validate_number,
    validate_email,
    validate_phone,
    validate_trip_data,
    validate_formula_syntax,
    validate_excel_file
)


class TestLoggingSystem:
    """Test logging system setup and functionality"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging()
        assert logger is not None
        assert logger.name == "TransportApp"
        assert len(logger.handlers) > 0
    
    def test_get_logger(self):
        """Test getting logger instance"""
        logger = get_logger("test_module")
        assert logger is not None
        assert "test_module" in logger.name
    
    def test_get_performance_logger(self):
        """Test getting performance logger"""
        perf_logger = get_performance_logger("test_perf")
        assert perf_logger is not None
    
    def test_log_context(self):
        """Test log context manager"""
        with log_context("Test operation"):
            pass  # Should log start and completion


class TestErrorHandlers:
    """Test error handling functionality"""
    
    def test_validation_error(self):
        """Test ValidationError exception"""
        error = ValidationError("Test validation error", field="test_field")
        assert str(error) == "Test validation error"
        assert error.field == "test_field"
    
    def test_database_error(self):
        """Test DatabaseError exception"""
        error = DatabaseError("Test database error", query="SELECT * FROM test")
        assert str(error) == "Test database error"
        assert error.query == "SELECT * FROM test"
    
    def test_formula_error(self):
        """Test FormulaError exception"""
        error = FormulaError("Test formula error", formula="[A] + [B]")
        assert str(error) == "Test formula error"
        assert error.formula == "[A] + [B]"
    
    def test_error_handler_handle_error(self):
        """Test ErrorHandler.handle_error"""
        error = ValueError("Test error")
        message = ErrorHandler.handle_error(error, "Test context", show_dialog=False)
        assert message is not None
        assert "Test context" in message
    
    def test_error_handler_handle_validation_error(self):
        """Test ErrorHandler.handle_validation_error"""
        errors = ["Error 1", "Error 2"]
        message = ErrorHandler.handle_validation_error(errors, show_dialog=False)
        assert "Error 1" in message
        assert "Error 2" in message
    
    def test_handle_errors_decorator(self):
        """Test handle_errors decorator"""
        @handle_errors(context="Test function", default_return="default")
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result == "default"
    
    def test_error_recovery_retry(self):
        """Test ErrorRecovery.retry_on_error"""
        call_count = [0]
        
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Test error")
            return "success"
        
        result = ErrorRecovery.retry_on_error(
            failing_function,
            max_retries=3,
            delay=0.01
        )
        assert result == "success"
        assert call_count[0] == 3


class TestValidation:
    """Test validation functionality"""
    
    def test_validate_required(self):
        """Test required validation"""
        is_valid, error = validate_required("test", "Test Field")
        assert is_valid is True
        assert error is None
        
        is_valid, error = validate_required("", "Test Field")
        assert is_valid is False
        assert error is not None
    
    def test_validate_number(self):
        """Test number validation"""
        is_valid, error = validate_number(123, "Test Number")
        assert is_valid is True
        
        is_valid, error = validate_number("123.45", "Test Number")
        assert is_valid is True
        
        is_valid, error = validate_number("abc", "Test Number")
        assert is_valid is False
    
    def test_validate_email(self):
        """Test email validation"""
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        
        is_valid, error = validate_email("invalid-email")
        assert is_valid is False
    
    def test_validate_phone(self):
        """Test phone validation"""
        is_valid, error = validate_phone("0123456789")
        assert is_valid is True
        
        is_valid, error = validate_phone("+84 123 456 789")
        assert is_valid is True
    
    def test_validate_trip_data(self):
        """Test trip data validation"""
        valid_data = {
            'khach_hang': 'Test Customer',
            'gia_ca': 1000000,
            'khoan_luong': 500000,
            'chi_phi_khac': 100000
        }
        is_valid, errors = validate_trip_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        invalid_data = {
            'khach_hang': '',  # Empty required field
            'gia_ca': -1000,  # Negative price
        }
        is_valid, errors = validate_trip_data(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_formula_syntax(self):
        """Test formula syntax validation"""
        is_valid, error = validate_formula_syntax("[A] + [B] * 2")
        assert is_valid is True
        
        is_valid, error = validate_formula_syntax("[A] + + [B]")
        assert is_valid is False
        
        is_valid, error = validate_formula_syntax("[A] + [B")
        assert is_valid is False
    
    def test_validator_class(self):
        """Test Validator class"""
        rules = [
            {'type': 'required'},
            {'type': 'number'},
            {'type': 'positive', 'allow_zero': False}
        ]
        
        is_valid, errors = Validator.validate(1000, rules, "Test Field")
        assert is_valid is True
        assert len(errors) == 0
        
        is_valid, errors = Validator.validate(-100, rules, "Test Field")
        assert is_valid is False
        assert len(errors) > 0


class TestIntegration:
    """Integration tests for error handling and logging"""
    
    def test_logging_with_error_handling(self):
        """Test logging integration with error handling"""
        logger = get_logger("test_integration")
        
        @handle_errors(context="Integration test")
        def test_function():
            logger.info("Starting test function")
            raise ValueError("Test error")
        
        result = test_function()
        # Should handle error gracefully
    
    def test_validation_with_error_handling(self):
        """Test validation integration with error handling"""
        trip_data = {
            'khach_hang': '',
            'gia_ca': 'invalid'
        }
        
        is_valid, errors = validate_trip_data(trip_data)
        assert is_valid is False
        
        if not is_valid:
            message = ErrorHandler.handle_validation_error(errors, show_dialog=False)
            assert message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
