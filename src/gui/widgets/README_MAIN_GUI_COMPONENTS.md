# Main GUI Components

This document describes the main GUI components for the Transportation Management System.

## Overview

The main GUI components provide a complete interface for managing trip data with the following features:
- Dynamic form-based data entry
- Excel-like table for viewing and editing
- Suggestion tabs for price lookup
- Multi-department support
- Pagination for large datasets

## Components

### 1. InputFormWidget

Specialized form widget for trip data input with dynamic form integration.

**Features:**
- Dynamic form based on field configurations
- Form submission with validation
- Auto-focus and tab navigation
- Form reset after successful submit
- Integration with TripService
- Edit mode support

**Usage:**
```python
from src.gui.widgets import InputFormWidget
from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService

# Create widget
input_form = InputFormWidget(
    trip_service=trip_service,
    field_config_service=field_config_service,
    department_id=1
)

# Connect signals
input_form.tripCreated.connect(on_trip_created)
input_form.tripUpdated.connect(on_trip_updated)
input_form.formCleared.connect(on_form_cleared)

# Load trip data for editing
input_form.load_trip_data(trip_data)

# Get form data
data = input_form.get_form_data()

# Set field value
input_form.set_field_value('khach_hang', 'Customer Name')
```

**Signals:**
- `tripCreated(dict)` - Emitted when trip is created successfully
- `tripUpdated(dict)` - Emitted when trip is updated successfully
- `formCleared()` - Emitted when form is cleared
- `validationFailed(dict)` - Emitted when validation fails

### 2. MainTableWidget

Table widget for displaying and editing trip data with Excel-like features.

**Features:**
- Data loading from database
- Auto-save on edit
- Row selection and multi-select
- Alternating row colors
- Integration with TripService
- Context menu operations

**Usage:**
```python
from src.gui.widgets import MainTableWidget
from src.services.trip_service import TripService

# Create widget
main_table = MainTableWidget(trip_service=trip_service)

# Connect signals
main_table.rowSelected.connect(on_row_selected)
main_table.dataChanged.connect(on_data_changed)
main_table.dataLoaded.connect(on_data_loaded)

# Load data
main_table.load_data(page=1, page_size=100)

# Refresh data
main_table.refresh_data()

# Get selected trip data
selected_data = main_table.get_selected_trip_data()

# Get all selected trips
selected_trips = main_table.get_selected_trips_data()
```

**Signals:**
- `rowSelected(dict)` - Emitted when a row is selected
- `rowsSelected(list)` - Emitted when multiple rows are selected
- `dataChanged(int, dict)` - Emitted when data is changed (trip_id, data)
- `dataLoaded(int)` - Emitted when data is loaded (row count)
- `tripDeleted(int)` - Emitted when trip is deleted (trip_id)

### 3. SuggestionTabWidget

Tab widget for displaying filtered results and company price suggestions.

**Features:**
- 4 tabs: Filtered results, Company A, Company B, Company C
- Read-only tables
- Click to fill form functionality
- Synchronized filtering with input form
- Real-time updates

**Usage:**
```python
from src.gui.widgets import SuggestionTabWidget
from src.services.trip_service import TripService
from src.services.company_price_service import CompanyPriceService

# Create widget
suggestion_tabs = SuggestionTabWidget(
    trip_service=trip_service,
    company_price_service=company_price_service
)

# Connect signals
suggestion_tabs.suggestionSelected.connect(on_suggestion_selected)

# Update filtered results
filters = {
    'khach_hang': 'Customer Name',
    'diem_di': 'Location A',
    'diem_den': 'Location B'
}
suggestion_tabs.update_filtered_results(filters)

# Update company prices
suggestion_tabs.update_company_prices('Company A', filters)

# Load all company prices
suggestion_tabs.load_all_company_prices()
```

**Signals:**
- `suggestionSelected(dict)` - Emitted when a suggestion is clicked

### 4. EmployeeTabWidget

Tab widget for multi-department support with independent forms and tables.

**Features:**
- Tab per department
- Independent form and table for each tab
- Tab switching with data persistence
- Department-specific field configurations
- Integrated form, table, and suggestions per department

**Usage:**
```python
from src.gui.widgets import EmployeeTabWidget
from src.models.department import Department

# Create departments
departments = [
    Department(id=1, name="sales", display_name="Phòng Kinh Doanh", is_active=True),
    Department(id=2, name="processing", display_name="Phòng Xử Lý", is_active=True),
    Department(id=3, name="accounting", display_name="Phòng Kế Toán", is_active=True),
]

# Create widget
employee_tabs = EmployeeTabWidget(
    departments=departments,
    trip_service=trip_service,
    field_config_service=field_config_service,
    company_price_service=company_price_service
)

# Connect signals
employee_tabs.departmentChanged.connect(on_department_changed)
employee_tabs.tripCreated.connect(on_trip_created)
employee_tabs.tripUpdated.connect(on_trip_updated)

# Switch to department
employee_tabs.switch_to_department(department_id=2)

# Get current department
dept_id = employee_tabs.get_current_department_id()

# Refresh current department
employee_tabs.refresh_current_department()

# Refresh all departments
employee_tabs.refresh_all_departments()
```

**Signals:**
- `departmentChanged(int)` - Emitted when department tab changes
- `tripCreated(int, dict)` - Emitted when trip is created (dept_id, data)
- `tripUpdated(int, dict)` - Emitted when trip is updated (dept_id, data)

### 5. PaginationWidget

Widget for page navigation with page size selection and jump to page functionality.

**Features:**
- Page navigation (first, previous, next, last)
- Page size selection
- Total records display
- Jump to page functionality
- Current page indicator

**Usage:**
```python
from src.gui.widgets import PaginationWidget

# Create widget
pagination = PaginationWidget(
    page_sizes=[50, 100, 200, 500],
    default_page_size=100
)

# Connect signals
pagination.pageChanged.connect(on_page_changed)
pagination.pageSizeChanged.connect(on_page_size_changed)

# Set total records
pagination.set_total_records(1500)

# Set current page
pagination.set_current_page(3)

# Get current page
page = pagination.get_current_page()

# Get page size
page_size = pagination.get_page_size()

# Get page range
start, end = pagination.get_page_range()

# Get page info text
info = pagination.get_page_info_text()  # "Hiển thị 201-300 / 1,500 bản ghi"
```

**Signals:**
- `pageChanged(int)` - Emitted when page changes (new page number)
- `pageSizeChanged(int)` - Emitted when page size changes

## Integration Example

Here's how to integrate all components together:

```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.trip_service = TripService(db_manager)
        self.field_config_service = FieldConfigService(db_manager)
        self.company_price_service = CompanyPriceService(db_manager)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Input Form
        self.input_form = InputFormWidget(
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            department_id=1
        )
        splitter.addWidget(self.input_form)
        
        # Right: Table and suggestions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.main_table = MainTableWidget(trip_service=self.trip_service)
        right_layout.addWidget(self.main_table, stretch=2)
        
        self.pagination = PaginationWidget()
        right_layout.addWidget(self.pagination)
        
        self.suggestion_tabs = SuggestionTabWidget(
            trip_service=self.trip_service,
            company_price_service=self.company_price_service
        )
        right_layout.addWidget(self.suggestion_tabs, stretch=1)
        
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)
        
        # Setup connections
        self.input_form.tripCreated.connect(self.on_trip_created)
        self.input_form.formDataChanged.connect(self.on_form_data_changed)
        self.main_table.rowSelected.connect(self.on_row_selected)
        self.main_table.dataLoaded.connect(self.on_data_loaded)
        self.pagination.pageChanged.connect(self.on_page_changed)
        self.pagination.pageSizeChanged.connect(self.on_page_size_changed)
        self.suggestion_tabs.suggestionSelected.connect(self.on_suggestion_selected)
        
        # Load initial data
        self.main_table.load_data(page=1, page_size=100)
        self.suggestion_tabs.load_all_company_prices()
    
    def on_trip_created(self, trip_data):
        self.main_table.refresh_data()
        self.update_pagination()
    
    def on_form_data_changed(self, data):
        filters = {k: v for k, v in data.items() if v and k in ['khach_hang', 'diem_di', 'diem_den']}
        if filters:
            self.suggestion_tabs.update_filtered_results(filters)
    
    def on_row_selected(self, row_data):
        self.input_form.load_trip_data(row_data)
    
    def on_data_loaded(self, row_count):
        self.update_pagination()
    
    def on_page_changed(self, page):
        page_size = self.pagination.get_page_size()
        self.main_table.load_data(page=page, page_size=page_size)
    
    def on_page_size_changed(self, page_size):
        self.main_table.load_data(page=1, page_size=page_size)
    
    def on_suggestion_selected(self, suggestion_data):
        for field_name, value in suggestion_data.items():
            self.input_form.set_field_value(field_name, value)
    
    def update_pagination(self):
        total_records = self.main_table.get_total_records()
        self.pagination.set_total_records(total_records)
```

## Demo

Run the demo script to see all components in action:

```bash
python examples/main_gui_components_demo.py
```

## Requirements Validation

These components satisfy the following requirements:

### InputFormWidget
- **Requirement 1.1**: Form nhập liệu với các trường cơ bản
- **Requirement 1.3**: Validation dữ liệu
- **Requirement 1.4**: Form reset after submit

### MainTableWidget
- **Requirement 1.4**: Bảng dữ liệu với khả năng chỉnh sửa
- **Requirement 1.5**: Auto-save khi thay đổi

### SuggestionTabWidget
- **Requirement 2.5**: Click vào gợi ý để điền form
- **Requirement 14.1**: Bảng giá của 3 công ty
- **Requirement 14.3**: Click để điền thông tin
- **Requirement 14.4**: Read-only mode
- **Requirement 14.5**: Đồng bộ filter

### EmployeeTabWidget
- **Requirement 8.1**: Nhiều phòng ban với tab riêng
- **Requirement 8.2**: Form và table độc lập
- **Requirement 8.3**: Cấu hình field riêng

### PaginationWidget
- **Requirement 16.3**: Pagination cho bảng lớn

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EmployeeTabWidget                         │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ Department 1 │ Department 2 │ Department 3 │            │
│  └──────────────┴──────────────┴──────────────┘            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DepartmentWidget                        │  │
│  │  ┌──────────────┬────────────────────────────────┐  │  │
│  │  │              │                                │  │  │
│  │  │ InputForm    │     MainTableWidget            │  │  │
│  │  │ Widget       │                                │  │  │
│  │  │              │     PaginationWidget           │  │  │
│  │  │              │                                │  │  │
│  │  │              │     SuggestionTabWidget        │  │  │
│  │  └──────────────┴────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Notes

- All widgets are designed to work independently or together
- Signals and slots provide loose coupling between components
- Each widget handles its own data loading and state management
- Department-specific configurations are supported through FieldConfigService
- All components support Vietnamese language labels
