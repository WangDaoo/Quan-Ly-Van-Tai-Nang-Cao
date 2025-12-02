# Autocomplete System Documentation

## Overview

The Autocomplete System provides intelligent autocomplete functionality with fuzzy search, debouncing, caching, and keyboard navigation for form fields. It's designed to enhance user experience by providing real-time suggestions as users type.

## Components

### 1. AutocompleteComboBox

A custom QComboBox widget with enhanced autocomplete features.

**Features:**
- Fuzzy search in dropdown
- Keyboard navigation (Arrow keys, Enter, Escape)
- Debounced search (300ms default)
- Caching for performance
- Dynamic data loading from callbacks

**Usage:**

```python
from src.gui.widgets import AutocompleteComboBox

# Create widget
combo = AutocompleteComboBox()

# Set items directly
combo.set_items(['Option 1', 'Option 2', 'Option 3'])

# Or use a data loader callback
combo.set_data_loader(lambda: get_data_from_database())
combo.load_data()

# Configure debounce delay
combo.set_debounce_delay(300)  # milliseconds

# Enable/disable caching
combo.set_cache_enabled(True)

# Connect signals
combo.textChanged.connect(on_text_changed)
combo.itemSelected.connect(on_item_selected)
```

### 2. FuzzyFilterProxyModel

A QSortFilterProxyModel that implements fuzzy search filtering.

**Features:**
- Matches items that contain all filter characters in order
- Case-insensitive matching
- Works with QStringListModel

**Usage:**

```python
from PyQt6.QtCore import QStringListModel
from src.gui.widgets import FuzzyFilterProxyModel

# Create models
source_model = QStringListModel(['Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng'])
proxy_model = FuzzyFilterProxyModel()
proxy_model.setSourceModel(source_model)

# Set filter
proxy_model.setFilterFixedString('hn')  # Will match 'Hà Nội'
```

### 3. AutocompleteService

Service for managing autocomplete data with database integration.

**Features:**
- Load unique customers from database
- Load departure/destination locations
- Caching for performance
- Data loader factory

**Usage:**

```python
from src.services import AutocompleteService
from src.database.enhanced_db_manager import EnhancedDatabaseManager

# Initialize
db_manager = EnhancedDatabaseManager('database.db')
service = AutocompleteService(db_manager)

# Get customers
customers = service.get_customers()

# Get locations
departure_locations = service.get_departure_locations()
destination_locations = service.get_destination_locations()
all_locations = service.get_all_locations()

# Create data loader for a field type
loader = service.create_data_loader('customer')
data = loader()

# Clear cache when data changes
service.clear_cache()
```

### 4. AutocompleteIntegration

Helper class to integrate autocomplete into forms.

**Features:**
- Automatic field detection
- Replace standard ComboBox with AutocompleteComboBox
- Field mapping for common fields (khách hàng, điểm đi, điểm đến)

**Usage:**

```python
from src.gui.widgets import AutocompleteIntegration
from src.services import AutocompleteService

# Initialize
integration = AutocompleteIntegration(autocomplete_service)

# Integrate with form builder
integration.integrate_with_form_builder(form_builder, form_widget)

# Get autocomplete widget for a field
customer_widget = integration.get_autocomplete_widget('khach_hang')

# Refresh all data
integration.refresh_all_data()

# Clear all caches
integration.clear_all_caches()
```

## Field Mappings

The system automatically recognizes these field names for autocomplete:

| Field Name | Type | Data Source |
|------------|------|-------------|
| khach_hang, khách hàng, customer | Customer | trips.khach_hang |
| diem_di, điểm đi, departure | Departure Location | trips.diem_di + company_prices.diem_di |
| diem_den, điểm đến, destination | Destination Location | trips.diem_den + company_prices.diem_den |

## Keyboard Shortcuts

- **Arrow Up/Down**: Navigate through suggestions
- **Enter/Return**: Select current suggestion
- **Escape**: Close dropdown and clear selection
- **Tab**: Move to next field (standard behavior)

## Requirements Validation

This implementation satisfies the following requirements:

### Requirement 2.1
✅ WHEN Người_Dùng gõ vào trường khách hàng, THE Hệ_Thống SHALL hiển thị dropdown gợi ý các khách hàng đã có

### Requirement 2.2
✅ WHEN Người_Dùng gõ vào trường điểm đi hoặc điểm đến, THE Hệ_Thống SHALL hiển thị dropdown gợi ý các địa điểm đã có

### Requirement 2.3
✅ THE Hệ_Thống SHALL hỗ trợ fuzzy search trong dropdown gợi ý

### Requirement 2.4
✅ THE Hệ_Thống SHALL cập nhật gợi ý theo thời gian thực với debounce 300ms

### Requirement 2.5
✅ WHEN Người_Dùng click vào gợi ý, THE Hệ_Thống SHALL điền thông tin vào form nhập liệu

### Requirement 16.4
✅ THE Hệ_Thống SHALL sử dụng lazy loading cho autocomplete suggestions

## Example: Complete Integration

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services import AutocompleteService
from src.gui.widgets import AutocompleteComboBox

class MyForm(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.db_manager = EnhancedDatabaseManager('database.db')
        self.autocomplete_service = AutocompleteService(self.db_manager)
        
        # Create form
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        form_layout = QFormLayout()
        
        # Customer field with autocomplete
        self.customer_combo = AutocompleteComboBox()
        self.customer_combo.set_data_loader(
            self.autocomplete_service.get_customers
        )
        self.customer_combo.set_debounce_delay(300)
        self.customer_combo.itemSelected.connect(self.on_customer_selected)
        form_layout.addRow("Khách hàng:", self.customer_combo)
        
        # Departure location with autocomplete
        self.departure_combo = AutocompleteComboBox()
        self.departure_combo.set_data_loader(
            self.autocomplete_service.get_departure_locations
        )
        self.departure_combo.set_debounce_delay(300)
        form_layout.addRow("Điểm đi:", self.departure_combo)
        
        # Destination location with autocomplete
        self.destination_combo = AutocompleteComboBox()
        self.destination_combo.set_data_loader(
            self.autocomplete_service.get_destination_locations
        )
        self.destination_combo.set_debounce_delay(300)
        form_layout.addRow("Điểm đến:", self.destination_combo)
        
        layout.addLayout(form_layout)
    
    def on_customer_selected(self, customer: str):
        print(f"Selected customer: {customer}")

if __name__ == '__main__':
    app = QApplication([])
    window = MyForm()
    window.show()
    app.exec()
```

## Testing

Run the unit tests:

```bash
python -m pytest tests/unit/test_autocomplete.py -v
```

Run the demo:

```bash
python examples/autocomplete_demo.py
```

## Performance Considerations

1. **Caching**: Data is cached after first load to avoid repeated database queries
2. **Debouncing**: 300ms delay prevents excessive filtering during typing
3. **Lazy Loading**: Data is loaded only when widget receives focus or dropdown is opened
4. **Fuzzy Search**: Efficient character-by-character matching algorithm

## Troubleshooting

### Autocomplete not showing suggestions

1. Check if data loader is set: `combo.set_data_loader(loader_func)`
2. Verify data is loaded: `combo.load_data()`
3. Check if cache is populated: `combo.get_cached_items()`

### Slow performance

1. Enable caching: `combo.set_cache_enabled(True)`
2. Increase debounce delay: `combo.set_debounce_delay(500)`
3. Check database indexes on queried columns

### Fuzzy search not working

1. Verify FuzzyFilterProxyModel is being used
2. Check filter pattern is set correctly
3. Ensure source model has data

## Future Enhancements

- [ ] Support for multi-column autocomplete
- [ ] Highlight matching characters in suggestions
- [ ] Custom scoring algorithm for fuzzy matching
- [ ] Support for remote data sources (API)
- [ ] Configurable maximum suggestions count
- [ ] Recent selections history
