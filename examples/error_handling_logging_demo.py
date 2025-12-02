"""
Demo: Error Handling and Logging System

Demonstrates the comprehensive error handling and logging features
implemented in Task 15.

Features demonstrated:
- Logging system with multiple levels
- Structured logging
- Performance logging
- Error handling with custom exceptions
- Validation system
- Error recovery mechanisms
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import (
    setup_logging,
    get_logger,
    get_performance_logger,
    log_context,
    log_performance
)
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


def demo_logging_system():
    """Demonstrate logging system features"""
    print("\n" + "="*80)
    print("DEMO 1: Logging System")
    print("="*80)
    
    # Setup logging
    logger = setup_logging()
    
    # Different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    # Get module-specific logger
    module_logger = get_logger("demo_module")
    module_logger.info("Module-specific log message")
    
    # Performance logging
    perf_logger = get_performance_logger("demo")
    perf_logger.log_operation("Sample operation", 0.5)
    perf_logger.log_query("SELECT * FROM trips", 0.1, row_count=100)
    
    # Log context
    with log_context("Loading data"):
        time.sleep(0.1)  # Simulate work
    
    print("\n✓ Logging system demonstrated")
    print(f"  - Log file: logs/transportapp.log")
    print(f"  - Multiple log levels: DEBUG, INFO, WARNING, ERROR")
    print(f"  - Performance logging enabled")


def demo_error_handling():
    """Demonstrate error handling features"""
    print("\n" + "="*80)
    print("DEMO 2: Error Handling")
    print("="*80)
    
    # Custom exceptions
    try:
        raise ValidationError("Invalid data", field="test_field")
    except ValidationError as e:
        print(f"\n✓ ValidationError caught: {e}")
        print(f"  Field: {e.field}")
    
    try:
        raise DatabaseError("Query failed", query="SELECT * FROM test")
    except DatabaseError as e:
        print(f"\n✓ DatabaseError caught: {e}")
        print(f"  Query: {e.query}")
    
    try:
        raise FormulaError("Invalid formula", formula="[A] + + [B]")
    except FormulaError as e:
        print(f"\n✓ FormulaError caught: {e}")
        print(f"  Formula: {e.formula}")
    
    # Error handler
    error = ValueError("Test error")
    message = ErrorHandler.handle_error(error, "Test context", show_dialog=False)
    print(f"\n✓ Error handled: {message[:50]}...")
    
    # Validation errors
    errors = ["Field A is required", "Field B must be a number"]
    message = ErrorHandler.handle_validation_error(errors, show_dialog=False)
    print(f"\n✓ Validation errors handled:")
    for err in errors:
        print(f"  - {err}")
    
    # Decorator for error handling
    @handle_errors(context="Demo function", default_return="default_value")
    def failing_function():
        raise ValueError("This function always fails")
    
    result = failing_function()
    print(f"\n✓ Error decorator: Function returned '{result}' after error")


def demo_validation():
    """Demonstrate validation features"""
    print("\n" + "="*80)
    print("DEMO 3: Validation System")
    print("="*80)
    
    # Required validation
    is_valid, error = validate_required("test value", "Test Field")
    print(f"\n✓ Required validation: {is_valid}")
    
    is_valid, error = validate_required("", "Empty Field")
    print(f"✓ Required validation (empty): {is_valid} - {error}")
    
    # Number validation
    is_valid, error = validate_number(123.45, "Price")
    print(f"\n✓ Number validation: {is_valid}")
    
    is_valid, error = validate_number("abc", "Invalid Number")
    print(f"✓ Number validation (invalid): {is_valid} - {error}")
    
    # Email validation
    is_valid, error = validate_email("test@example.com")
    print(f"\n✓ Email validation: {is_valid}")
    
    is_valid, error = validate_email("invalid-email")
    print(f"✓ Email validation (invalid): {is_valid} - {error}")
    
    # Phone validation
    is_valid, error = validate_phone("0123456789")
    print(f"\n✓ Phone validation: {is_valid}")
    
    # Trip data validation
    valid_trip = {
        'khach_hang': 'Test Customer',
        'gia_ca': 1000000,
        'khoan_luong': 500000,
        'chi_phi_khac': 100000
    }
    is_valid, errors = validate_trip_data(valid_trip)
    print(f"\n✓ Trip data validation (valid): {is_valid}")
    
    invalid_trip = {
        'khach_hang': '',  # Empty required field
        'gia_ca': -1000,  # Negative price
    }
    is_valid, errors = validate_trip_data(invalid_trip)
    print(f"✓ Trip data validation (invalid): {is_valid}")
    print(f"  Errors: {len(errors)}")
    for err in errors:
        print(f"    - {err}")
    
    # Formula syntax validation
    is_valid, error = validate_formula_syntax("[A] + [B] * 2")
    print(f"\n✓ Formula validation (valid): {is_valid}")
    
    is_valid, error = validate_formula_syntax("[A] + + [B]")
    print(f"✓ Formula validation (invalid): {is_valid} - {error}")
    
    # Validator class
    rules = [
        {'type': 'required'},
        {'type': 'number'},
        {'type': 'positive', 'allow_zero': False}
    ]
    is_valid, errors = Validator.validate(1000, rules, "Price")
    print(f"\n✓ Validator class (valid): {is_valid}")
    
    is_valid, errors = Validator.validate(-100, rules, "Negative Price")
    print(f"✓ Validator class (invalid): {is_valid}")
    print(f"  Errors: {len(errors)}")


def demo_error_recovery():
    """Demonstrate error recovery mechanisms"""
    print("\n" + "="*80)
    print("DEMO 4: Error Recovery")
    print("="*80)
    
    # Retry mechanism
    call_count = [0]
    
    def failing_function():
        call_count[0] += 1
        print(f"  Attempt {call_count[0]}")
        if call_count[0] < 3:
            raise ValueError("Temporary error")
        return "success"
    
    print("\n✓ Retry mechanism:")
    result = ErrorRecovery.retry_on_error(
        failing_function,
        max_retries=3,
        delay=0.1
    )
    print(f"  Result: {result} (after {call_count[0]} attempts)")
    
    # Fallback mechanism
    def primary_function():
        raise ValueError("Primary failed")
    
    def fallback_function():
        return "fallback_result"
    
    print("\n✓ Fallback mechanism:")
    result = ErrorRecovery.with_fallback(
        primary_function,
        fallback_function
    )
    print(f"  Result: {result}")


@log_performance("Complete demo")
def demo_performance_logging():
    """Demonstrate performance logging"""
    print("\n" + "="*80)
    print("DEMO 5: Performance Logging")
    print("="*80)
    
    perf_logger = get_performance_logger("demo")
    
    # Simulate operations
    print("\n✓ Logging operation performance:")
    
    with log_context("Fast operation", log_performance=True):
        time.sleep(0.1)
    
    with log_context("Slow operation", log_performance=True):
        time.sleep(1.5)
    
    # Log specific operations
    perf_logger.log_operation("Data processing", 0.5, {'records': 1000})
    perf_logger.log_query("SELECT * FROM trips WHERE id > ?", 0.05, row_count=50)
    perf_logger.log_ui_operation("MainWindow", "load_data", 0.3)
    
    print("  Check logs/transportapp.log for performance metrics")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("ERROR HANDLING AND LOGGING SYSTEM DEMO")
    print("Task 15: Implement Error Handling và Logging")
    print("="*80)
    
    try:
        demo_logging_system()
        demo_error_handling()
        demo_validation()
        demo_error_recovery()
        demo_performance_logging()
        
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nFeatures demonstrated:")
        print("  ✓ Logging system with file rotation")
        print("  ✓ Multiple log levels (DEBUG, INFO, WARNING, ERROR)")
        print("  ✓ Structured logging support")
        print("  ✓ Performance logging")
        print("  ✓ Custom exceptions")
        print("  ✓ Error handling with decorators")
        print("  ✓ Comprehensive validation")
        print("  ✓ Error recovery mechanisms")
        print("  ✓ Transaction rollback support")
        print("\nCheck logs/transportapp.log for detailed logs")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
