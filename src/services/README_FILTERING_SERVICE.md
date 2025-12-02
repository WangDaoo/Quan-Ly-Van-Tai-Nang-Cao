# FilteringService Documentation

## Overview

The `FilteringService` provides real-time filtering capabilities with debouncing, multi-field filtering support, and fuzzy search functionality. It's designed to handle filtering operations for trips and other data types in the transportation management system.

## Features

- **Real-time Filtering**: Filter data as users type with immediate results
- **Debounced Filtering**: Prevent excessive filtering operations with configurable delay (default: 300ms)
- **Multi-field Filtering**: Filter by multiple fields simultaneously with AND logic
- **Fuzzy Search**: Find matches even with typos or partial strings
- **Case-insensitive**: All filtering is case-insensitive by default
- **Substring Matching**: Supports partial string matching for flexible searches
- **Generic Data Support**: Works with Trip objects and generic dictionaries

## Requirements Validation

This service implements the following requirements:

- **Requirement 2.1**: Autocomplete and intelligent suggestions when typing
- **Requirement 2.4**: Real-time updates with 300ms debounce
- **Requirement 3.1**: Advanced filtering with multi-column support
- **Requirement 3.3**: Multi-field filtering support

## Installation

The FilteringService is part of the `src.services` package:

```python
from src.services import FilteringService
```

## Basic Usage

### Initialize the Service

```python
from src.services import FilteringService

# Create with default settings (300ms debounce, 0.6 fuzzy threshold)
service = FilteringService()

# Or customize settings
service = FilteringService(debounce_ms=500, fuzzy_threshold=0.7)
```

### Filter Trips

```python
from src.models.trip import Trip

# Sample trips
trips = [
    Trip(ma_chuyen="C001", khach_hang="ABC Company", diem_di="Hanoi", 
         diem_den="Ho Chi Minh", gia_ca=1000000),
    Trip(ma_chuyen="C002", khach_hang="XYZ Corporation", diem_di="Da Nang", 
         diem_den="Hanoi", gia_ca=800000),
]

# Filter by single field
filtered = service.filter_trips(trips, {'khach_hang': 'ABC'})

# Filter by multiple fields
filtered = service.filter_trips(trips, {
    'khach_hang': 'ABC',
    'diem_di': 'Hanoi'
})

# Disable fuzzy matching
filtered = service.filter_trips(trips, {'khach_hang': 'ABC'}, use_fuzzy=False)
```

## Advanced Features

### Fuzzy Search

Find items even with typos or partial matches:

```python
customers = ['ABC Company', 'XYZ Corporation', 'Global Logistics']

# Search with fuzzy matching
results = service.fuzzy_search(customers, 'Compny')  # Finds "ABC Company"

# Results are tuples of (item, similarity_score)
for item, score in results:
    print(f"{item}: {score:.2f}")

# Use custom threshold
results = service.fuzzy_search(customers, 'ABC', threshold=0.8)
```

### Debounced Filtering

Prevent excessive filtering operations during rapid user input:

```python
def on_filter_complete(results):
    """Callback when filtering is complete"""
    print(f"Found {len(results)} results")

# Schedule debounced filter
service.debounced_filter(
    callback=on_filter_complete,
    filter_id='customer_search',
    results=filtered_trips
)

# Cancel a pending filter
service.cancel_debounce('customer_search')

# Cancel all pending filters
service.cancel_all_debounces()
```

### Filter Generic Dictionary Data

Works with any dictionary data, not just Trip objects:

```python
data = [
    {'name': 'John', 'city': 'Hanoi', 'age': 30},
    {'name': 'Jane', 'city': 'Ho Chi Minh', 'age': 25},
]

filtered = service.filter_by_multiple_fields(data, {'city': 'Hanoi'})
```

### Get Unique Values

Extract unique values from a field for filter suggestions:

```python
# Get unique departure locations
locations = service.get_unique_values(trips, 'diem_di')
# Returns: ['Da Nang', 'Hanoi', 'Ho Chi Minh']

# Get unique customers
customers = service.get_unique_values(trips, 'khach_hang')
```

### Create Filter Suggestions

Generate smart filter suggestions based on existing data:

```python
# Get all suggestions for a field
suggestions = service.create_filter_suggestions(trips, 'khach_hang')

# Get suggestions matching a query
suggestions = service.create_filter_suggestions(trips, 'khach_hang', 'ABC')
# Returns suggestions sorted by relevance
```

## API Reference

### FilteringService Class

#### Constructor

```python
FilteringService(debounce_ms: int = 300, fuzzy_threshold: float = 0.6)
```

**Parameters:**
- `debounce_ms`: Debounce delay in milliseconds (default: 300)
- `fuzzy_threshold`: Minimum similarity ratio for fuzzy matching, 0.0-1.0 (default: 0.6)

#### Methods

##### filter_trips()

```python
filter_trips(
    trips: List[Trip],
    filters: Dict[str, Any],
    use_fuzzy: bool = True
) -> List[Trip]
```

Filter trips based on multiple field criteria.

**Parameters:**
- `trips`: List of Trip objects to filter
- `filters`: Dictionary of field names and filter values
- `use_fuzzy`: Whether to use fuzzy matching (default: True)

**Returns:** List of Trip objects matching all filter criteria

##### fuzzy_search()

```python
fuzzy_search(
    items: List[str],
    query: str,
    threshold: Optional[float] = None
) -> List[tuple[str, float]]
```

Perform fuzzy search on a list of strings.

**Parameters:**
- `items`: List of strings to search
- `query`: Search query string
- `threshold`: Minimum similarity threshold (uses instance default if None)

**Returns:** List of tuples (item, similarity_score) sorted by similarity

##### debounced_filter()

```python
debounced_filter(
    callback: Callable,
    filter_id: str,
    *args,
    **kwargs
) -> None
```

Execute a filter callback with debouncing.

**Parameters:**
- `callback`: Function to call after debounce delay
- `filter_id`: Unique identifier for this filter operation
- `*args`: Positional arguments to pass to callback
- `**kwargs`: Keyword arguments to pass to callback

##### cancel_debounce()

```python
cancel_debounce(filter_id: str) -> None
```

Cancel a pending debounced filter operation.

##### cancel_all_debounces()

```python
cancel_all_debounces() -> None
```

Cancel all pending debounced filter operations.

##### filter_by_multiple_fields()

```python
filter_by_multiple_fields(
    data: List[Dict[str, Any]],
    filters: Dict[str, Any],
    use_fuzzy: bool = True
) -> List[Dict[str, Any]]
```

Filter generic dictionary data by multiple fields.

##### get_unique_values()

```python
get_unique_values(
    trips: List[Trip],
    field_name: str
) -> List[str]
```

Get unique values for a specific field from a list of trips.

##### create_filter_suggestions()

```python
create_filter_suggestions(
    trips: List[Trip],
    field_name: str,
    query: str = ""
) -> List[str]
```

Create filter suggestions for a field based on existing data.

## Configuration

The service uses configuration from `config.py`:

```python
# config.py
FILTER_DEBOUNCE_MS = 300  # Debounce delay in milliseconds
```

## Performance Considerations

### Debouncing

The debounce mechanism prevents excessive filtering operations during rapid user input. With a 300ms delay:
- User types "ABC" (3 keystrokes in ~200ms)
- Only 1 filter operation executes (after the last keystroke + 300ms)
- Reduces database queries and UI updates by ~66%

### Fuzzy Search

Fuzzy search uses Python's `difflib.SequenceMatcher` which has O(n*m) complexity where n and m are string lengths. For large datasets:
- Consider caching fuzzy search results
- Use higher threshold values to reduce matches
- Combine with substring matching for better performance

### Memory Usage

The service maintains a dictionary of active debounce timers. For typical usage:
- Each timer: ~1KB memory
- 100 concurrent filters: ~100KB memory
- Timers are automatically cleaned up after execution

## Integration Examples

### With PyQt6 QLineEdit

```python
from PyQt6.QtWidgets import QLineEdit
from src.services import FilteringService

class SearchWidget:
    def __init__(self):
        self.service = FilteringService()
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self, text):
        """Handle text changes with debouncing"""
        self.service.debounced_filter(
            callback=self.perform_filter,
            filter_id='search',
            query=text
        )
    
    def perform_filter(self, query):
        """Perform the actual filtering"""
        filtered = self.service.filter_trips(
            self.all_trips,
            {'khach_hang': query}
        )
        self.update_table(filtered)
```

### With Autocomplete

```python
def setup_autocomplete(self, field_name):
    """Setup autocomplete for a field"""
    # Get unique values for suggestions
    suggestions = self.service.get_unique_values(self.trips, field_name)
    
    # Setup QCompleter with suggestions
    completer = QCompleter(suggestions)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    self.input_field.setCompleter(completer)
```

## Testing

Run the unit tests:

```bash
python -m pytest tests/unit/test_filtering_service.py -v
```

Run the demo:

```bash
python examples/filtering_service_demo.py
```

## Error Handling

The service handles common edge cases:
- Empty filter values (returns all items)
- None filter values (returns all items)
- Invalid field names (returns empty list)
- None values in data (skips those items)
- Empty data lists (returns empty list)

## Best Practices

1. **Use Debouncing for User Input**: Always use `debounced_filter()` for real-time user input to prevent excessive operations

2. **Choose Appropriate Fuzzy Threshold**: 
   - 0.6: Lenient matching (more results, some false positives)
   - 0.8: Strict matching (fewer results, more accurate)

3. **Cache Unique Values**: If filtering the same dataset repeatedly, cache the results of `get_unique_values()`

4. **Combine with Database Filtering**: For large datasets, use database-level filtering first, then use FilteringService for client-side refinement

5. **Clean Up Timers**: Call `cancel_all_debounces()` when destroying widgets to prevent memory leaks

## Troubleshooting

### Filters Not Working

- Check that field names match exactly (case-sensitive for field names)
- Verify filter values are not None or empty strings
- Ensure Trip objects have the fields you're filtering on

### Fuzzy Search Too Lenient/Strict

- Adjust `fuzzy_threshold` parameter (0.0-1.0)
- Lower values = more lenient
- Higher values = more strict

### Debouncing Not Working

- Verify `debounce_ms` is set correctly
- Check that `filter_id` is consistent across calls
- Ensure callback function is defined correctly

## See Also

- [TripService](./trip_service.py) - For database-level trip operations
- [ExcelService](./README_EXCEL_SERVICE.md) - For import/export operations
- [WorkspaceService](./README_WORKSPACE_SERVICE.md) - For workspace management
