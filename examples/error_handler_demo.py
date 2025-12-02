"""
Error Handler Demo

Demonstrates usage of the error handler module with various scenarios.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.error_handler import (
    ValidationError,
    DatabaseError,
    FormulaError,
    TransportConnectionError,
    ErrorHandler,
    ErrorRecovery,
    handle_errors,
    validate_input
)


def demo_basic_error_handling():
    """Demo basic error handling"""
    print("=" * 60)
    print("Demo 1: Basic Error Handling")
    print("=" * 60)
    
    try:
        raise ValidationError("Khách hàng là bắt buộc", field="khach_hang")
    except ValidationError as e:
        message = ErrorHandler.handle_error(e, "Nhập liệu chuyến xe")
        print(f"Error handled: {message}\n")


def demo_validation_errors():
    """Demo handling multiple validation errors"""
    print("=" * 60)
    print("Demo 2: Multiple Validation Errors")
    print("=" * 60)
    
    errors = [
        "Khách hàng là bắt buộc",
        "Giá cả phải lớn hơn 0",
        "Điểm đi không được để trống"
    ]
    
    message = ErrorHandler.handle_validation_error(errors)
    print(f"Validation errors:\n{message}\n")


def demo_safe_execute():
    """Demo safe execution with error recovery"""
    print("=" * 60)
    print("Demo 3: Safe Execute with Error Recovery")
    print("=" * 60)
    
    def risky_operation(x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
    
    # Success case
    result = ErrorHandler.safe_execute(
        risky_operation,
        10, 2,
        default_return=0,
        context="Division operation"
    )
    print(f"Success: 10 / 2 = {result}")
    
    # Error case
    result = ErrorHandler.safe_execute(
        risky_operation,
        10, 0,
        default_return=0,
        context="Division operation"
    )
    print(f"Error handled, returned default: {result}\n")


def demo_decorator():
    """Demo error handling decorator"""
    print("=" * 60)
    print("Demo 4: Error Handling Decorator")
    print("=" * 60)
    
    @handle_errors(context="Calculate total", default_return=0)
    def calculate_total(gia_ca, khoan_luong, chi_phi_khac):
        if gia_ca < 0:
            raise ValueError("Giá cả không thể âm")
        return gia_ca + khoan_luong + chi_phi_khac
    
    # Success case
    total = calculate_total(1000000, 200000, 50000)
    print(f"Total calculated: {total:,} VND")
    
    # Error case
    total = calculate_total(-1000000, 200000, 50000)
    print(f"Error handled, returned default: {total}\n")


def demo_validation_decorator():
    """Demo validation decorator"""
    print("=" * 60)
    print("Demo 5: Validation Decorator")
    print("=" * 60)
    
    def validate_trip_data(trip_data):
        errors = []
        if not trip_data.get('khach_hang'):
            errors.append("Khách hàng là bắt buộc")
        if not trip_data.get('gia_ca') or trip_data.get('gia_ca') <= 0:
            errors.append("Giá cả phải lớn hơn 0")
        return len(errors) == 0, errors
    
    @validate_input(validate_trip_data)
    def create_trip(trip_data):
        return f"Created trip for {trip_data['khach_hang']}"
    
    # Valid data
    try:
        result = create_trip({
            'khach_hang': 'Công ty ABC',
            'gia_ca': 1000000
        })
        print(f"Success: {result}")
    except ValidationError as e:
        print(f"Validation failed: {e}")
    
    # Invalid data
    try:
        result = create_trip({
            'gia_ca': 0
        })
        print(f"Success: {result}")
    except ValidationError as e:
        print(f"Validation failed: {e}\n")


def demo_retry_mechanism():
    """Demo retry mechanism"""
    print("=" * 60)
    print("Demo 6: Retry Mechanism")
    print("=" * 60)
    
    attempt_count = [0]
    
    def unstable_operation():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise TransportConnectionError("Connection timeout", resource="database")
        return "Success after retries"
    
    try:
        result = ErrorRecovery.retry_on_error(
            unstable_operation,
            max_retries=5,
            delay=0.1
        )
        print(f"Result: {result}")
        print(f"Succeeded after {attempt_count[0]} attempts\n")
    except Exception as e:
        print(f"Failed after all retries: {e}\n")


def demo_fallback_mechanism():
    """Demo fallback mechanism"""
    print("=" * 60)
    print("Demo 7: Fallback Mechanism")
    print("=" * 60)
    
    def primary_database_query():
        raise DatabaseError("Primary database unavailable")
    
    def fallback_cache_query():
        return "Data from cache"
    
    result = ErrorRecovery.with_fallback(
        primary_database_query,
        fallback_cache_query
    )
    print(f"Result: {result}\n")


def demo_transaction_rollback():
    """Demo transaction rollback"""
    print("=" * 60)
    print("Demo 8: Transaction Rollback")
    print("=" * 60)
    
    class MockConnection:
        def __init__(self):
            self.committed = False
            self.rolled_back = False
        
        def commit(self):
            self.committed = True
            print("Transaction committed")
        
        def rollback(self):
            self.rolled_back = True
            print("Transaction rolled back")
    
    # Success case
    conn = MockConnection()
    try:
        result = ErrorRecovery.with_transaction_rollback(
            lambda: "Operation successful",
            conn
        )
        print(f"Result: {result}")
        print(f"Committed: {conn.committed}, Rolled back: {conn.rolled_back}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Failure case
    conn = MockConnection()
    try:
        result = ErrorRecovery.with_transaction_rollback(
            lambda: 1/0,  # This will raise ZeroDivisionError
            conn
        )
        print(f"Result: {result}")
    except DatabaseError as e:
        print(f"Error caught: {e}")
        print(f"Committed: {conn.committed}, Rolled back: {conn.rolled_back}\n")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "ERROR HANDLER DEMO" + " " * 25 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    demo_basic_error_handling()
    demo_validation_errors()
    demo_safe_execute()
    demo_decorator()
    demo_validation_decorator()
    demo_retry_mechanism()
    demo_fallback_mechanism()
    demo_transaction_rollback()
    
    print("=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
