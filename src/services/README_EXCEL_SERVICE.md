# Excel Service Documentation

## Overview

The Excel Service provides comprehensive import/export functionality for Excel files with validation, duplicate handling, formatting preservation, and progress tracking.

## Features

- **Import with Preview**: Preview Excel files before importing with validation
- **Export with Formatting**: Export data with professional formatting (headers, colors, borders)
- **Duplicate Handling**: Three strategies - skip, overwrite, or create new
- **Progress Indicators**: Track progress for large file operations
- **Validation**: Comprehensive data validation with detailed error reporting
- **Alternative Column Names**: Support for Vietnamese and English column names
- **Filtered Export**: Export filtered or selected records

## Installation

The Excel Service requires the following dependencies:
- pandas
- openpyxl

These are already included in `requirements.txt`.

## Usage

### Basic Import

```python
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.excel_service import ExcelService, DuplicateHandling

# Initialize
db = EnhancedDatabaseManager("data/transport.db")
excel_service = ExcelService(db)

# Import with skip duplicates
result = excel_service.import_excel_file(
    "path/to/file.xlsx",
    duplicate_handling=DuplicateHandling.SKIP
)

print(f"Success: {result['success_count']}")
print(f"Skipped: {result['skipped_count']}")
print(f"Errors: {result['error_count']}")
```

### Preview Before Import

```python
# Preview file
preview = excel_service.preview_excel_file("path/to/file.xlsx", max_rows=10)

print(f"Columns: {preview['columns']}")
print(f"Total rows: {preview['total_rows']}")
print(f"Validation errors: {len(preview['validation_errors'])}")

# Show preview data
for row in preview['preview_data']:
    print(row)
```

### Import with Progress Callback

```python
def progress_callback(current, total, message):
    percentage = (current / total) * 100
    print(f"Progress: {percentage:.1f}% - {message}")

result = excel_service.import_excel_file(
    "path/to/file.xlsx",
    duplicate_handling=DuplicateHandling.OVERWRITE,
    progress_callback=progress_callback
)
```

### Export to Excel

```python
from src.services.trip_service import TripService

# Get trips to export
trip_service = TripService(db)
result = trip_service.get_all_trips(page=1, page_size=100)
trips = result['trips']

# Export with formatting
success = excel_service.export_to_excel(
    "exports/trips.xlsx",
    trips,
    include_formatting=True
)
```

### Export Filtered Trips

```python
# Export trips matching filter criteria
filters = {'khach_hang': 'Công ty A'}

success = excel_service.export_filtered_trips(
    "exports/filtered_trips.xlsx",
    filters,
    include_formatting=True
)
```

### Export Selected Trips

```python
# Export specific trips by ID
trip_ids = [1, 2, 3, 5, 8]

success = excel_service.export_selected_trips(
    "exports/selected_trips.xlsx",
    trip_ids,
    include_formatting=True
)
```

## Duplicate Handling Strategies

### 1. SKIP (Default)
Skip records with duplicate trip codes.

```python
result = excel_service.import_excel_file(
    "file.xlsx",
    duplicate_handling=DuplicateHandling.SKIP
)
```

### 2. OVERWRITE
Update existing records with new data.

```python
result = excel_service.import_excel_file(
    "file.xlsx",
    duplicate_handling=DuplicateHandling.OVERWRITE
)
```

### 3. CREATE_NEW
Create new records with auto-generated trip codes.

```python
result = excel_service.import_excel_file(
    "file.xlsx",
    duplicate_handling=DuplicateHandling.CREATE_NEW
)
```

## Excel File Format

### Required Columns

The Excel file should contain the following columns (Vietnamese or English names):

| Vietnamese | English | Required | Type |
|------------|---------|----------|------|
| Mã chuyến | Trip Code | No* | Text (C001, C002, ...) |
| Khách hàng | Customer | Yes | Text |
| Điểm đi | Departure | No | Text |
| Điểm đến | Destination | No | Text |
| Giá cả | Price | Yes | Number (>= 0) |
| Khoán lương | Salary | No | Number (>= 0) |
| Chi phí khác | Other Costs | No | Number (>= 0) |
| Ghi chú | Notes | No | Text |

*If trip code is not provided, it will be auto-generated.

### Example Excel File

```
| Mã chuyến | Khách hàng | Điểm đi | Điểm đến | Giá cả  | Khoán lương | Chi phí khác | Ghi chú |
|-----------|------------|---------|----------|---------|-------------|--------------|---------|
| C001      | Công ty A  | Hà Nội  | TP.HCM   | 5000000 | 1000000     | 500000       | Note 1  |
| C002      | Công ty B  | Đà Nẵng | Hà Nội   | 3000000 | 800000      | 200000       | Note 2  |
```

## Validation Rules

### Required Fields
- **Khách hàng (Customer)**: Cannot be empty
- **Giá cả (Price)**: Cannot be empty

### Numeric Fields
- **Giá cả (Price)**: Must be >= 0
- **Khoán lương (Salary)**: Must be >= 0
- **Chi phí khác (Other Costs)**: Must be >= 0

### Trip Code Format
- Must follow pattern: C followed by digits (e.g., C001, C002)
- Auto-generated if not provided

## Export Formatting

When `include_formatting=True`, the exported Excel file includes:

### Header Row
- Bold white text
- Blue background (#4472C4)
- Centered alignment
- Borders

### Data Rows
- Alternating row colors (white/light gray)
- Borders on all cells
- Right-aligned numbers with thousand separators
- Left-aligned text
- Auto-fit column widths

### Additional Features
- Frozen header row
- Professional appearance
- Easy to read and print

## Error Handling

### Import Errors

The service provides detailed error reporting:

```python
result = excel_service.import_excel_file("file.xlsx")

if result['error_count'] > 0:
    print("Errors occurred:")
    for error in result['errors']:
        print(f"  - {error}")
```

Error messages include:
- Row number
- Field name
- Specific error description

### Common Errors

1. **File Not Found**: `FileNotFoundError` if file doesn't exist
2. **Invalid Format**: `ValueError` if file format is invalid
3. **Validation Errors**: Detailed list in result['errors']
4. **Empty Data**: `ValueError` when exporting empty list

## Performance Considerations

### Large Files

For large Excel files (>1000 rows):
- Use progress callback to track progress
- Consider batch processing
- Monitor memory usage

### Optimization Tips

1. **Preview First**: Always preview before importing large files
2. **Validate Early**: Check validation errors in preview
3. **Progress Tracking**: Use progress callback for user feedback
4. **Batch Operations**: Process in smaller batches if needed

## Testing

Comprehensive unit tests are available in `tests/unit/test_excel_service.py`:

```bash
# Run all Excel Service tests
python -m pytest tests/unit/test_excel_service.py -v

# Run specific test
python -m pytest tests/unit/test_excel_service.py::test_import_excel_file_success -v
```

## Example Demo

A complete demo script is available at `examples/excel_service_demo.py`:

```bash
python examples/excel_service_demo.py
```

## API Reference

### ExcelService Class

#### `__init__(db_manager: EnhancedDatabaseManager)`
Initialize Excel Service with database manager.

#### `preview_excel_file(file_path: str, max_rows: int = 10) -> Dict`
Preview Excel file before import.

**Returns:**
- `columns`: List of column names
- `preview_data`: List of preview rows
- `total_rows`: Total number of rows
- `validation_errors`: List of validation errors

#### `import_excel_file(file_path: str, duplicate_handling: str, progress_callback: Optional[Callable]) -> Dict`
Import data from Excel file.

**Returns:**
- `success_count`: Number of successfully imported records
- `skipped_count`: Number of skipped records
- `error_count`: Number of failed records
- `errors`: List of error details
- `imported_trips`: List of imported Trip objects

#### `export_to_excel(file_path: str, trips: List[Trip], include_formatting: bool, progress_callback: Optional[Callable]) -> bool`
Export trips to Excel file.

**Returns:** True if successful

#### `export_filtered_trips(file_path: str, filters: Dict, include_formatting: bool, progress_callback: Optional[Callable]) -> bool`
Export filtered trips to Excel.

**Returns:** True if successful

#### `export_selected_trips(file_path: str, trip_ids: List[int], include_formatting: bool, progress_callback: Optional[Callable]) -> bool`
Export selected trips by IDs.

**Returns:** True if successful

### DuplicateHandling Enum

- `DuplicateHandling.SKIP`: Skip duplicate records
- `DuplicateHandling.OVERWRITE`: Overwrite existing records
- `DuplicateHandling.CREATE_NEW`: Create new records with new codes

## Requirements Validation

This implementation satisfies the following requirements from the specification:

### Requirement 11.1: Import with Preview
✓ Preview Excel file before import
✓ Show column names and sample data
✓ Display validation errors

### Requirement 11.2: Duplicate Handling
✓ Skip duplicates
✓ Overwrite duplicates
✓ Create new records

### Requirement 11.3: Import Validation
✓ Validate data during import
✓ Report errors with line numbers
✓ Continue processing after errors

### Requirement 11.4: Export Functionality
✓ Export all records
✓ Export filtered records
✓ Export selected records

### Requirement 11.5: Formatting Preservation
✓ Professional header formatting
✓ Alternating row colors
✓ Number formatting with thousand separators
✓ Auto-fit columns
✓ Frozen header row

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the demo script
3. Consult the main documentation

## License

Part of the Hệ Thống Quản Lý Vận Tải Toàn Diện project.
