# Technical Documentation - Transport Management System

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [API Documentation](#api-documentation)
5. [Design Decisions](#design-decisions)
6. [Developer Setup Guide](#developer-setup-guide)
7. [Code Structure](#code-structure)
8. [Testing Strategy](#testing-strategy)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)
11. [Deployment Guide](#deployment-guide)
12. [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

### System Architecture

The Transport Management System follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                        (PyQt6 GUI)                           │
│  - Widgets: Input forms, tables, dialogs                    │
│  - Event handling and user interactions                     │
│  - Data binding and validation                              │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│                        (Services)                            │
│  - TripService: CRUD operations for trips                   │
│  - FormulaEngine: Formula parsing and evaluation            │
│  - WorkflowService: Automation and push operations          │
│  - FieldConfigService: Dynamic form management              │
│  - ExcelService: Import/Export operations                   │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│                    (SQLite Database)                         │
│  - EnhancedDatabaseManager: Connection pooling              │
│  - MigrationRunner: Schema versioning                       │
│  - Models: Pydantic data validation                         │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

1. **Model-View-Controller (MVC)**: Separation of data, presentation, and logic
2. **Repository Pattern**: Data access abstraction
3. **Factory Pattern**: Widget creation in FormBuilder
4. **Observer Pattern**: Signal/slot mechanism in PyQt6
5. **Singleton Pattern**: Database connection pool
6. **Strategy Pattern**: Validation rules
7. **Command Pattern**: Undo/redo operations (future)

---

## Technology Stack

### Core Technologies

- **Python**: 3.9+
- **PyQt6**: 6.0+ (GUI framework)
- **SQLite3**: Database engine
- **Pydantic**: 2.0+ (Data validation)

### Data Processing

- **pandas**: 2.0+ (Data manipulation)
- **openpyxl**: 3.1+ (Excel operations)

### Testing

- **pytest**: 7.0+ (Unit testing)
- **pytest-qt**: 4.0+ (GUI testing)
- **pytest-cov**: Coverage reporting

### Development Tools

- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **PyInstaller**: Application packaging

---

## Database Schema

### Core Tables

#### trips
```sql
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_chuyen VARCHAR(10) UNIQUE NOT NULL,
    khach_hang VARCHAR(255) NOT NULL,
    diem_di VARCHAR(255),
    diem_den VARCHAR(255),
    gia_ca INTEGER NOT NULL,
    khoan_luong INTEGER DEFAULT 0,
    chi_phi_khac INTEGER DEFAULT 0,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trips_khach_hang ON trips(khach_hang);
CREATE INDEX idx_trips_diem ON trips(diem_di, diem_den);
```

#### company_prices
```sql
CREATE TABLE company_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(100) NOT NULL,
    khach_hang VARCHAR(255) NOT NULL,
    diem_di VARCHAR(255) NOT NULL,
    diem_den VARCHAR(255) NOT NULL,
    gia_ca INTEGER NOT NULL,
    khoan_luong INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_company_prices_route 
ON company_prices(company_name, diem_di, diem_den);
```

### Enhancement Tables

#### departments
```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### employees
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    department_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

#### field_configurations

```sql
CREATE TABLE field_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    widget_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT 0,
    validation_rules TEXT,
    default_value TEXT,
    options TEXT,
    display_order INTEGER DEFAULT 0,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    UNIQUE(department_id, field_name)
);

CREATE INDEX idx_field_configs_dept 
ON field_configurations(department_id, is_active);
```

#### formulas
```sql
CREATE TABLE formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    target_field VARCHAR(100) NOT NULL,
    formula_expression TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE INDEX idx_formulas_dept 
ON formulas(department_id, is_active);
```

#### push_conditions
```sql
CREATE TABLE push_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_department_id INTEGER NOT NULL,
    target_department_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    value TEXT,
    logic_operator VARCHAR(10) DEFAULT 'AND',
    condition_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_department_id) REFERENCES departments(id),
    FOREIGN KEY (target_department_id) REFERENCES departments(id)
);

CREATE INDEX idx_push_conditions_dept 
ON push_conditions(source_department_id, target_department_id);
```

#### workflow_history
```sql
CREATE TABLE workflow_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    source_department_id INTEGER NOT NULL,
    target_department_id INTEGER NOT NULL,
    pushed_by INTEGER,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_department_id) REFERENCES departments(id),
    FOREIGN KEY (target_department_id) REFERENCES departments(id),
    FOREIGN KEY (pushed_by) REFERENCES employees(id)
);

CREATE INDEX idx_workflow_history_record 
ON workflow_history(record_id, created_at);
```

#### employee_workspaces
```sql
CREATE TABLE employee_workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    workspace_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    configuration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE(employee_id, workspace_name)
);
```

#### business_records
```sql
CREATE TABLE business_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    workspace_id INTEGER,
    record_data TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (workspace_id) REFERENCES employee_workspaces(id)
);

CREATE INDEX idx_business_records_dept 
ON business_records(department_id, status);
```

### Database Migrations

Migrations are managed by `MigrationRunner` class:

```python
from src.database.migration_runner import MigrationRunner

# Run migrations
runner = MigrationRunner("data/transport.db")
runner.run_migrations()

# Rollback migration
runner.rollback_migration("V001")
```

---

## API Documentation

### TripService

```python
class TripService:
    """Service for managing trip records"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """Initialize with database manager"""
        
    def create_trip(self, trip: Trip) -> int:
        """
        Create a new trip record
        
        Args:
            trip: Trip model instance
            
        Returns:
            int: ID of created trip
            
        Raises:
            ValidationError: If trip data is invalid
            DatabaseError: If database operation fails
        """
        
    def get_trip(self, trip_id: int) -> Optional[Trip]:
        """
        Get trip by ID
        
        Args:
            trip_id: Trip ID
            
        Returns:
            Trip instance or None if not found
        """
        
    def update_trip(self, trip_id: int, trip: Trip) -> bool:
        """
        Update existing trip
        
        Args:
            trip_id: Trip ID
            trip: Updated trip data
            
        Returns:
            bool: True if successful
        """
        
    def delete_trip(self, trip_id: int) -> bool:
        """
        Delete trip by ID
        
        Args:
            trip_id: Trip ID
            
        Returns:
            bool: True if successful
        """
        
    def list_trips(
        self, 
        filters: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Trip]:
        """
        List trips with optional filtering and pagination
        
        Args:
            filters: Dictionary of filter conditions
            page: Page number (1-indexed)
            page_size: Number of records per page
            
        Returns:
            List of Trip instances
        """
        
    def generate_ma_chuyen(self) -> str:
        """
        Generate next trip code (C001, C002, ...)
        
        Returns:
            str: Generated trip code
        """
```

### FormulaEngine

```python
class FormulaEngine:
    """Engine for parsing and evaluating formulas"""
    
    def parse_formula(self, formula: str) -> AST:
        """
        Parse formula expression into AST
        
        Args:
            formula: Formula string (e.g., "[A] + [B] * 2")
            
        Returns:
            AST: Abstract syntax tree
            
        Raises:
            FormulaError: If syntax is invalid
        """
        
    def validate_formula(
        self, 
        formula: str, 
        available_fields: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate formula syntax and field references
        
        Args:
            formula: Formula string
            available_fields: List of valid field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        
    def evaluate_formula(
        self, 
        formula: str, 
        field_values: Dict[str, Any]
    ) -> float:
        """
        Evaluate formula with given field values
        
        Args:
            formula: Formula string
            field_values: Dictionary mapping field names to values
            
        Returns:
            float: Calculated result
            
        Raises:
            FormulaError: If evaluation fails
        """
        
    def get_dependent_fields(self, formula: str) -> List[str]:
        """
        Extract field names referenced in formula
        
        Args:
            formula: Formula string
            
        Returns:
            List of field names
        """
```

### WorkflowService

```python
class WorkflowService:
    """Service for workflow automation"""
    
    def evaluate_conditions(
        self, 
        record: Dict, 
        conditions: List[PushCondition]
    ) -> bool:
        """
        Evaluate if record meets push conditions
        
        Args:
            record: Record data dictionary
            conditions: List of push conditions
            
        Returns:
            bool: True if all conditions met
        """
        
    def push_record(
        self,
        record_id: int,
        source_dept_id: int,
        target_dept_id: int,
        pushed_by: Optional[int] = None
    ) -> bool:
        """
        Push record from source to target department
        
        Args:
            record_id: Record ID
            source_dept_id: Source department ID
            target_dept_id: Target department ID
            pushed_by: Employee ID who initiated push
            
        Returns:
            bool: True if successful
            
        Raises:
            WorkflowError: If push fails
        """
        
    def transform_data(
        self,
        record: Dict,
        field_mapping: Dict[str, str]
    ) -> Dict:
        """
        Transform record data according to field mapping
        
        Args:
            record: Source record data
            field_mapping: Mapping of source to target fields
            
        Returns:
            Transformed record data
        """
        
    def log_workflow(
        self,
        record_id: int,
        source_dept_id: int,
        target_dept_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> int:
        """
        Log workflow operation to history
        
        Args:
            record_id: Record ID
            source_dept_id: Source department ID
            target_dept_id: Target department ID
            status: Operation status
            error_message: Error message if failed
            
        Returns:
            int: History entry ID
        """
```

### FieldConfigService

```python
class FieldConfigService:
    """Service for managing field configurations"""
    
    def create_field_config(
        self, 
        config: FieldConfiguration
    ) -> int:
        """
        Create new field configuration
        
        Args:
            config: FieldConfiguration instance
            
        Returns:
            int: Configuration ID
        """
        
    def get_field_configs(
        self, 
        department_id: int
    ) -> List[FieldConfiguration]:
        """
        Get all field configurations for department
        
        Args:
            department_id: Department ID
            
        Returns:
            List of FieldConfiguration instances
        """
        
    def update_field_config(
        self,
        config_id: int,
        config: FieldConfiguration
    ) -> bool:
        """
        Update field configuration
        
        Args:
            config_id: Configuration ID
            config: Updated configuration
            
        Returns:
            bool: True if successful
        """
        
    def delete_field_config(self, config_id: int) -> bool:
        """
        Delete field configuration
        
        Args:
            config_id: Configuration ID
            
        Returns:
            bool: True if successful
        """
        
    def reorder_fields(
        self,
        department_id: int,
        field_order: List[int]
    ) -> bool:
        """
        Reorder fields for department
        
        Args:
            department_id: Department ID
            field_order: List of config IDs in desired order
            
        Returns:
            bool: True if successful
        """
```

### ExcelService

```python
class ExcelService:
    """Service for Excel import/export operations"""
    
    def import_from_excel(
        self,
        file_path: str,
        duplicate_handling: str = "skip",
        progress_callback: Optional[Callable] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Import data from Excel file
        
        Args:
            file_path: Path to Excel file
            duplicate_handling: "skip", "overwrite", or "create_new"
            progress_callback: Callback for progress updates
            
        Returns:
            Tuple of (success_count, error_count, error_messages)
            
        Raises:
            ValidationError: If data validation fails
        """
        
    def export_to_excel(
        self,
        file_path: str,
        records: List[Dict],
        columns: Optional[List[str]] = None,
        formatting: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Export data to Excel file
        
        Args:
            file_path: Output file path
            records: List of record dictionaries
            columns: Columns to export (None = all)
            formatting: Apply formatting
            progress_callback: Callback for progress updates
            
        Returns:
            bool: True if successful
        """
        
    def preview_import(
        self,
        file_path: str,
        max_rows: int = 100
    ) -> Tuple[List[Dict], List[str]]:
        """
        Preview Excel import data
        
        Args:
            file_path: Path to Excel file
            max_rows: Maximum rows to preview
            
        Returns:
            Tuple of (preview_data, validation_errors)
        """
```

---

## Design Decisions

### Why PyQt6?

**Pros**:
- Native look and feel on all platforms
- Rich widget library
- Excellent performance
- Strong signal/slot mechanism
- Good documentation

**Cons**:
- Steeper learning curve than web frameworks
- GPL/Commercial licensing

**Decision**: PyQt6 chosen for desktop-first approach with native performance

### Why SQLite?

**Pros**:
- Zero configuration
- Serverless
- Single file database
- ACID compliant
- Good performance for < 1M records

**Cons**:
- Limited concurrent writes
- No built-in replication

**Decision**: SQLite perfect for single-user desktop application

### Why Pydantic?

**Pros**:
- Runtime type checking
- Data validation
- JSON serialization
- IDE support

**Cons**:
- Performance overhead
- Learning curve

**Decision**: Pydantic ensures data integrity and reduces bugs

### Formula Engine Design

**Options Considered**:
1. eval() - Security risk
2. Third-party library - Dependency
3. Custom parser - Full control

**Decision**: Custom AST-based parser for security and flexibility

### Connection Pooling

**Why**: Improve database performance by reusing connections

**Implementation**: Queue-based pool with configurable size

**Trade-offs**: Memory vs. performance

---

## Developer Setup Guide

### Prerequisites

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **pip** (Python package manager)
   ```bash
   pip --version
   ```

3. **Git**
   ```bash
   git --version
   ```

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd transport-management-system
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Initialize Database**
   ```bash
   python test_database_setup.py
   ```

6. **Run Tests**
   ```bash
   pytest
   ```

7. **Run Application**
   ```bash
   python main.py
   ```

### Development Tools Setup

**Code Formatting**:
```bash
black src/ tests/
```

**Linting**:
```bash
flake8 src/ tests/
```

**Type Checking**:
```bash
mypy src/
```

**Coverage Report**:
```bash
pytest --cov=src --cov-report=html
```

### IDE Configuration

**VS Code** (recommended):
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

**PyCharm**:
- Enable pytest as test runner
- Configure black as formatter
- Enable flake8 inspections

---

## Code Structure

### Directory Layout

```
transport-management-system/
├── src/
│   ├── database/
│   │   ├── connection_pool.py
│   │   ├── enhanced_db_manager.py
│   │   ├── migration_runner.py
│   │   ├── query_optimizer.py
│   │   └── migrations/
│   ├── models/
│   │   ├── trip.py
│   │   ├── company_price.py
│   │   ├── department.py
│   │   ├── employee.py
│   │   ├── field_configuration.py
│   │   ├── formula.py
│   │   ├── push_condition.py
│   │   ├── workflow_history.py
│   │   └── employee_workspace.py
│   ├── services/
│   │   ├── trip_service.py
│   │   ├── company_price_service.py
│   │   ├── field_config_service.py
│   │   ├── formula_engine.py
│   │   ├── workflow_service.py
│   │   ├── workspace_service.py
│   │   ├── excel_service.py
│   │   ├── filtering_service.py
│   │   └── autocomplete_service.py
│   ├── gui/
│   │   ├── integrated_main_window.py
│   │   ├── ui_optimizer.py
│   │   ├── widgets/
│   │   │   ├── input_form_widget.py
│   │   │   ├── main_table_widget.py
│   │   │   ├── suggestion_tab_widget.py
│   │   │   ├── employee_tab_widget.py
│   │   │   ├── pagination_widget.py
│   │   │   ├── dynamic_form_widget.py
│   │   │   ├── form_builder.py
│   │   │   ├── form_validator.py
│   │   │   ├── field_widgets.py
│   │   │   ├── excel_like_table.py
│   │   │   ├── excel_header_view.py
│   │   │   ├── excel_filter_dialog.py
│   │   │   ├── copy_paste_handler.py
│   │   │   ├── column_visibility_dialog.py
│   │   │   ├── autocomplete_combobox.py
│   │   │   └── autocomplete_integration.py
│   │   └── dialogs/
│   │       ├── field_manager_dialog.py
│   │       ├── formula_builder_dialog.py
│   │       ├── push_conditions_dialog.py
│   │       ├── workspace_manager_dialog.py
│   │       ├── field_preset_dialog.py
│   │       ├── workflow_history_dialog.py
│   │       ├── statistics_dialog.py
│   │       ├── excel_import_dialog.py
│   │       └── excel_export_dialog.py
│   └── utils/
│       ├── datetime_utils.py
│       ├── number_utils.py
│       ├── text_utils.py
│       ├── error_handler.py
│       ├── logger.py
│       ├── validation.py
│       ├── performance_optimizer.py
│       ├── memory_manager.py
│       └── __init__.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── manual/
├── data/
│   └── transport.db
├── logs/
│   └── transportapp.log
├── backups/
├── docs/
├── examples/
├── main.py
├── config.py
├── requirements.txt
└── README.md
```

### Coding Standards

**Naming Conventions**:
- Classes: PascalCase (e.g., `TripService`)
- Functions: snake_case (e.g., `create_trip`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_PAGE_SIZE`)
- Private methods: _leading_underscore (e.g., `_validate_data`)

**Docstrings**:
```python
def function_name(arg1: str, arg2: int) -> bool:
    """
    Brief description of function
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
```

**Type Hints**:
```python
from typing import List, Dict, Optional, Tuple

def process_data(
    data: List[Dict[str, Any]],
    options: Optional[Dict] = None
) -> Tuple[int, List[str]]:
    pass
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   Manual    │  10%
        │   Testing   │
        ├─────────────┤
        │ Integration │  20%
        │    Tests    │
        ├─────────────┤
        │    Unit     │  70%
        │    Tests    │
        └─────────────┘
```

### Unit Tests

**Location**: `tests/unit/`

**Coverage Target**: 80%+

**Example**:
```python
import pytest
from src.services.trip_service import TripService
from src.models.trip import Trip

def test_create_trip(db_manager):
    service = TripService(db_manager)
    trip = Trip(
        ma_chuyen="C001",
        khach_hang="Test Customer",
        gia_ca=1000000
    )
    trip_id = service.create_trip(trip)
    assert trip_id > 0
    
def test_generate_ma_chuyen(db_manager):
    service = TripService(db_manager)
    ma_chuyen = service.generate_ma_chuyen()
    assert ma_chuyen.startswith("C")
    assert len(ma_chuyen) == 4
```

### Integration Tests

**Location**: `tests/integration/`

**Purpose**: Test component interactions

**Example**:
```python
def test_form_to_database_workflow(qtbot, main_window):
    # Fill form
    main_window.input_form.khach_hang_field.setText("Test")
    main_window.input_form.gia_ca_field.setValue(1000000)
    
    # Submit
    qtbot.mouseClick(
        main_window.input_form.submit_button,
        Qt.LeftButton
    )
    
    # Verify in database
    trips = main_window.trip_service.list_trips()
    assert len(trips) > 0
    assert trips[-1].khach_hang == "Test"
```

### Performance Tests

**Location**: `tests/performance/`

**Metrics**:
- Query time < 100ms
- UI response < 50ms
- Memory usage < 500MB

**Example**:
```python
def test_load_10000_records(benchmark):
    def load_records():
        service.list_trips(page_size=10000)
    
    result = benchmark(load_records)
    assert result < 1.0  # < 1 second
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_trip_service.py

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test
pytest tests/unit/test_trip_service.py::test_create_trip
```

---

## Performance Optimization

### Database Optimization

**Indexes**:
```sql
CREATE INDEX idx_trips_khach_hang ON trips(khach_hang);
CREATE INDEX idx_trips_diem ON trips(diem_di, diem_den);
```

**Connection Pooling**:
```python
pool = ConnectionPool("data/transport.db", pool_size=5)
```

**Prepared Statements**:
```python
cursor.execute(
    "SELECT * FROM trips WHERE khach_hang = ?",
    (khach_hang,)
)
```

### UI Optimization

**Debouncing**:
```python
from PyQt6.QtCore import QTimer

self.filter_timer = QTimer()
self.filter_timer.setSingleShot(True)
self.filter_timer.timeout.connect(self.apply_filter)

def on_text_changed(self):
    self.filter_timer.start(300)  # 300ms debounce
```

**Lazy Loading**:
```python
def load_autocomplete_data(self):
    if not self.cache:
        self.cache = self.service.get_unique_values()
    return self.cache
```

**Virtual Scrolling**:
```python
# For tables > 1000 rows
table.setRowCount(visible_rows_only)
table.verticalScrollBar().valueChanged.connect(
    self.load_visible_rows
)
```

### Memory Management

**Clear Unused Data**:
```python
def closeEvent(self, event):
    self.table.clear()
    self.cache.clear()
    gc.collect()
```

**Limit Cache Size**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_autocomplete_data(field):
    return load_data(field)
```

---

## Security Considerations

### SQL Injection Prevention

**Always use parameterized queries**:
```python
# ✅ Good
cursor.execute(
    "SELECT * FROM trips WHERE id = ?",
    (trip_id,)
)

# ❌ Bad
cursor.execute(
    f"SELECT * FROM trips WHERE id = {trip_id}"
)
```

### Input Validation

**Validate all user inputs**:
```python
from pydantic import BaseModel, validator

class Trip(BaseModel):
    khach_hang: str
    gia_ca: int
    
    @validator('gia_ca')
    def validate_gia_ca(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v
```

### Formula Security

**Never use eval()**:
```python
# ✅ Good - AST-based parser
result = formula_engine.evaluate(formula, values)

# ❌ Bad - Security risk
result = eval(formula)
```

### Data Isolation

**Department-level isolation**:
```python
def get_trips(self, department_id: int):
    return self.db.execute(
        "SELECT * FROM trips WHERE department_id = ?",
        (department_id,)
    )
```

---

## Deployment Guide

### Building Executable

**PyInstaller Configuration**:
```python
# build.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='TransportApp',
    icon='icon.ico',
    console=False,
)
```

**Build Command**:
```bash
pyinstaller build.spec
```

### Distribution

**Windows**:
```bash
# Create installer with Inno Setup
iscc installer.iss
```

**macOS**:
```bash
# Create DMG
hdiutil create -volname "Transport App" -srcfolder dist/TransportApp.app -ov -format UDZO TransportApp.dmg
```

**Linux**:
```bash
# Create AppImage
appimagetool dist/TransportApp
```

### Database Backup

**Automatic Backup**:
```python
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/transport_{timestamp}.db"
    shutil.copy("data/transport.db", backup_path)
```

**Scheduled Backup** (Windows Task Scheduler, cron):
```bash
# Daily at 2 AM
0 2 * * * python backup_script.py
```

---

## Contributing Guidelines

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. **Push Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Describe changes
   - Link related issues
   - Request review

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

**Example**:
```
feat(trip-service): add pagination support

- Implement page-based pagination
- Add page size configuration
- Update tests

Closes #123
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance considered
- [ ] Security reviewed

---

**Version**: 1.0  
**Last Updated**: 2024  
**Maintainers**: Transport Management System Team
