# Error Handler Module

Centralized error handling system for the Transport Management Application.

## Overview

The Error Handler module provides:
- **Custom Exceptions**: Domain-specific exception classes
- **Centralized Error Handling**: Consistent error handling across the application
- **User-Friendly Messages**: Vietnamese error messages for end users
- **Error Recovery Mechanisms**: Retry, fallback, and transaction rollback
- **Decorators**: Easy-to-use decorators for error handling
- **Logging Integration**: Automatic error logging with full tracebacks

## Requirements

Implements requirements:
- **17.1**: User-friendly error messages
- **17.3**: Error recovery mechanisms
- **17.4**: Input validation

## Custom Exceptions

### ValidationError
For data validation errors.

```python
from src.utils.error_handler import ValidationError

raise ValidationError("Khách hàng là bắt buộc", field="khach_hang")
```

### DatabaseError
For database operation errors.

```python
from src.utils.error_handler import DatabaseError

raise DatabaseError("Connection failed", query="SELECT * FROM trips")
```

### FormulaError
For formula calculation errors.

```python
from src.utils.error_handler import FormulaError

raise FormulaError("Division by zero", formula="[A] / [B]")
```

### WorkflowError
For workflow automation errors.

```python
from src.utils.error_handler import WorkflowError

raise WorkflowError("Push failed", workflow_id=123)
```

### ConfigurationError
For configuration errors.

```python
from src.utils.error_handler import ConfigurationError

raise ConfigurationError("Missing value", config_key="database.path")
```

### ImportExportError
For import/export errors.

```python
from src.utils.error_handler import ImportExportError

raise ImportExportError("File not found", file_path="/path/to/file.xlsx")
```

### TransportConnectionError
For connection errors.

```python
from src.utils.error_handler import TransportConnectionError

raise TransportConnectionError("Connection timeout", resource="database")
```

## ErrorHandler Class

### Basic Error Handling

```python
from src.utils.error_handler import ErrorHandler, ValidationError

try:
    # Some operation that might fail
    raise ValidationError("Invalid data")
except ValidationError as e:
    message = ErrorHandler.handle_error(e, "Data processing")
    print(message)
```

### Handling Multiple Validation Errors

```python
from src.utils.error_handler import ErrorHandler

errors = [
    "Khách hàng là bắt buộc",
    "Giá cả phải lớn hơn 0",
    "Điểm đi không được để trống"
]

message = ErrorHandler.handle_validation_error(errors, show_dialog=True)
```

### Safe Execution

```python
from src.utils.error_handler import ErrorHandler

def risky_operation(x, y):
    return x / y

result = ErrorHandler.safe_execute(
    risky_operation,
    10, 0,
    default_return=0,
    context="Division operation"
)
# Returns 0 if error occurs
```

## Decorators

### @handle_errors

Automatically handle errors in functions.

```python
from src.utils.error_handler import handle_errors

@handle_errors(context="Calculate total", default_return=0)
def calculate_total(gia_ca, khoan_luong, chi_phi_khac):
    if gia_ca < 0:
        raise ValueError("Giá cả không thể âm")
    return gia_ca + khoan_luong + chi_phi_khac

# Errors are automatically handled and logged
total = calculate_total(-1000000, 200000, 50000)  # Returns 0
```

### @validate_input

Validate function inputs before execution.

```python
from src.utils.error_handler import validate_input, ValidationError

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

# Raises ValidationError if validation fails
create_trip({'khach_hang': 'Công ty ABC', 'gia_ca': 1000000})
```

## Error Recovery

### Retry Mechanism

Retry operations with exponential backoff.

```python
from src.utils.error_handler import ErrorRecovery

def unstable_operation():
    # Operation that might fail
    return fetch_data_from_api()

result = ErrorRecovery.retry_on_error(
    unstable_operation,
    max_retries=3,
    delay=1.0
)
```

### Fallback Mechanism

Use fallback when primary operation fails.

```python
from src.utils.error_handler import ErrorRecovery

def primary_database_query():
    return query_database()

def fallback_cache_query():
    return query_cache()

result = ErrorRecovery.with_fallback(
    primary_database_query,
    fallback_cache_query
)
```

### Transaction Rollback

Automatic rollback on database errors.

```python
from src.utils.error_handler import ErrorRecovery, DatabaseError

def update_records(connection):
    # Database operations
    connection.execute("UPDATE trips SET ...")
    connection.execute("INSERT INTO workflow_history ...")

try:
    result = ErrorRecovery.with_transaction_rollback(
        update_records,
        connection
    )
except DatabaseError as e:
    print(f"Transaction failed and rolled back: {e}")
```

## Utility Functions

### get_error_details

Extract detailed information from exceptions.

```python
from src.utils.error_handler import get_error_details

try:
    # Some operation
    raise ValueError("Test error")
except Exception as e:
    details = get_error_details(e)
    print(details['type'])       # 'ValueError'
    print(details['message'])    # 'Test error'
    print(details['traceback'])  # Full traceback
```

### format_error_for_user

Format exceptions into user-friendly messages.

```python
from src.utils.error_handler import format_error_for_user, ValidationError

error = ValidationError("Invalid data")
message = format_error_for_user(error)
# Returns: "Dữ liệu không hợp lệ: Invalid data"
```

## Integration with PyQt6

The error handler can show GUI dialogs when PyQt6 is available.

```python
from src.utils.error_handler import ErrorHandler, ValidationError

try:
    raise ValidationError("Invalid input")
except ValidationError as e:
    # Shows QMessageBox.critical dialog
    ErrorHandler.handle_error(e, "Input validation", show_dialog=True)
```

## Best Practices

1. **Use Specific Exceptions**: Use domain-specific exceptions instead of generic ones
   ```python
   # Good
   raise ValidationError("Khách hàng là bắt buộc", field="khach_hang")
   
   # Avoid
   raise Exception("Khách hàng là bắt buộc")
   ```

2. **Provide Context**: Always provide context when handling errors
   ```python
   ErrorHandler.handle_error(error, "Creating trip record")
   ```

3. **Use Decorators**: Use decorators for cleaner code
   ```python
   @handle_errors(context="Data processing", default_return=None)
   def process_data(data):
       # Processing logic
       pass
   ```

4. **Validate Early**: Validate inputs before processing
   ```python
   @validate_input(validate_trip_data)
   def create_trip(trip_data):
       # Create trip logic
       pass
   ```

5. **Log Everything**: All errors are automatically logged with full tracebacks

6. **Use Recovery Mechanisms**: Use retry and fallback for resilient operations
   ```python
   result = ErrorRecovery.retry_on_error(fetch_data, max_retries=3)
   ```

## Error Message Templates

The error handler provides Vietnamese error messages:

- `ValidationError`: "Dữ liệu không hợp lệ"
- `DatabaseError`: "Lỗi cơ sở dữ liệu"
- `FormulaError`: "Lỗi công thức tính toán"
- `WorkflowError`: "Lỗi quy trình làm việc"
- `ConfigurationError`: "Lỗi cấu hình hệ thống"
- `ImportExportError`: "Lỗi import/export dữ liệu"
- `TransportConnectionError`: "Lỗi kết nối"
- `Exception`: "Lỗi không xác định"

## Testing

Run the unit tests:

```bash
python -m pytest tests/unit/test_error_handler.py -v
```

Run the demo:

```bash
python examples/error_handler_demo.py
```

## Examples

See `examples/error_handler_demo.py` for comprehensive usage examples.
