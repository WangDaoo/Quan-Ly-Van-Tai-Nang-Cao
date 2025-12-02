# Database Layer Documentation

## Overview

The database layer provides a complete data management solution for the Transport Management System with connection pooling, transaction support, migration management, and data seeding capabilities.

## Components

### 1. Enhanced Database Schema (`enhanced_schema.sql`)

Complete database schema with 10 tables:

**Core Tables:**
- `trips` - Main transport trip records
- `company_prices` - Price lists from different companies

**Organization Tables:**
- `departments` - Organization departments (Sales, Processing, Accounting)
- `employees` - System users

**Configuration Tables:**
- `field_configurations` - Dynamic form field definitions
- `formulas` - Automatic calculation formulas

**Workflow Tables:**
- `push_conditions` - Workflow automation rules
- `workflow_history` - Audit trail for workflow operations

**Workspace Tables:**
- `employee_workspaces` - Personal workspace configurations
- `business_records` - Department-specific business data

**Features:**
- Foreign key constraints for data integrity
- Check constraints for validation
- Performance indexes on frequently queried columns
- Automatic timestamp triggers

### 2. Connection Pool (`connection_pool.py`)

Thread-safe connection pooling for improved performance:

```python
from src.database import ConnectionPool

pool = ConnectionPool("data/transport.db", pool_size=5)
conn = pool.get_connection()
# Use connection
pool.return_connection(conn)
```

**Features:**
- Configurable pool size
- Automatic connection validation
- WAL mode for better concurrency
- 64MB cache for performance

### 3. Enhanced Database Manager (`enhanced_db_manager.py`)

Main database interface with CRUD operations:

```python
from src.database import EnhancedDatabaseManager

db = EnhancedDatabaseManager("data/transport.db")

# Insert trip
trip_id = db.insert_trip({
    'ma_chuyen': 'C001',
    'khach_hang': 'Customer Name',
    'gia_ca': 5000000
})

# Query trips
trips = db.get_all_trips(limit=100)

# Search with filters
results = db.search_trips({'khach_hang': 'ABC'})

# Transaction support
with db.transaction() as conn:
    conn.execute("INSERT INTO ...")
    conn.execute("UPDATE ...")
    # Auto-commit on success, rollback on error
```

**Available Operations:**
- Generic CRUD: `execute_query()`, `execute_update()`, `execute_insert()`
- Trips: `insert_trip()`, `update_trip()`, `delete_trip()`, `get_trip_by_id()`, `search_trips()`
- Company Prices: `insert_company_price()`, `get_company_prices()`
- Departments: `insert_department()`, `get_all_departments()`
- Employees: `insert_employee()`, `get_employees_by_department()`
- Field Configurations: `insert_field_configuration()`, `get_field_configurations()`
- Formulas: `insert_formula()`, `get_formulas()`
- Push Conditions: `insert_push_condition()`, `get_push_conditions()`
- Workflow History: `insert_workflow_history()`, `get_workflow_history()`
- Workspaces: `insert_workspace()`, `get_workspaces()`
- Business Records: `insert_business_record()`, `get_business_records()`

### 4. Migration System (`migration_runner.py`)

Database version management and schema migrations:

```python
from src.database import MigrationRunner, Migration

runner = MigrationRunner("data/transport.db")

# Check current version
version = runner.get_current_version()

# Get migration status
status = runner.get_migration_status()

# Apply migrations
runner.migrate_up()

# Rollback to version
runner.migrate_down(target_version=1)

# Load migrations from directory
runner.load_migrations_from_directory("src/database/migrations")
```

**Migration File Format:**
- Up migration: `V001__migration_name.sql`
- Down migration: `V001__down__migration_name.sql`

### 5. Data Seeding (`seed_data.py`)

Sample data generation for development and testing:

```python
from src.database import EnhancedDatabaseManager, seed_database

db = EnhancedDatabaseManager("data/transport.db")
seed_database(db)
```

**Seeded Data:**
- 3 departments (Sales, Processing, Accounting)
- 5 employees across departments
- 50+ trip records
- 300+ company price records (20+ routes × 3 companies × 5 customers)
- 7 employee workspaces

## Usage Examples

### Basic Setup

```python
from src.database import EnhancedDatabaseManager, seed_database

# Initialize database
db = EnhancedDatabaseManager("data/transport.db")

# Seed with sample data (first time only)
seed_database(db)

# Use database
trips = db.get_all_trips()
print(f"Total trips: {len(trips)}")
```

### CRUD Operations

```python
# Create
trip_data = {
    'ma_chuyen': 'C001',
    'khach_hang': 'Công ty ABC',
    'diem_di': 'Hà Nội',
    'diem_den': 'TP. Hồ Chí Minh',
    'gia_ca': 5000000,
    'khoan_luong': 1000000
}
trip_id = db.insert_trip(trip_data)

# Read
trip = db.get_trip_by_id(trip_id)

# Update
trip_data['gia_ca'] = 6000000
db.update_trip(trip_id, trip_data)

# Delete
db.delete_trip(trip_id)
```

### Search and Filter

```python
# Search by customer
results = db.search_trips({'khach_hang': 'ABC'})

# Search by route
results = db.search_trips({
    'diem_di': 'Hà Nội',
    'diem_den': 'TP. Hồ Chí Minh'
})

# Get company prices with filters
prices = db.get_company_prices('A', {
    'khach_hang': 'ABC',
    'diem_di': 'Hà Nội'
})
```

### Transactions

```python
# Automatic transaction management
with db.transaction() as conn:
    conn.execute("INSERT INTO trips (...) VALUES (...)")
    conn.execute("UPDATE company_prices SET ...")
    # Commits automatically on success
    # Rolls back on any exception
```

## Testing

Run the test script to verify database setup:

```bash
python test_database_setup.py
```

This will:
- Create a test database
- Verify all tables exist
- Test migration system
- Seed sample data
- Test CRUD operations
- Test transaction rollback
- Verify data integrity

## Performance Considerations

1. **Connection Pooling**: Reuses connections to reduce overhead
2. **Indexes**: Optimized indexes on frequently queried columns
3. **WAL Mode**: Write-Ahead Logging for better concurrency
4. **Prepared Statements**: All queries use parameterized statements
5. **Caching**: 64MB cache per connection
6. **Pagination**: Built-in pagination support for large datasets

## Requirements Validation

This implementation satisfies:
- **Requirement 16.1**: SQLite with connection pooling ✓
- **Requirement 16.2**: Indexes for performance optimization ✓
- **Requirement 17.5**: Transaction rollback on errors ✓
- **Requirement 1.1**: Trip management with auto-generated codes ✓
- **Requirement 14.1**: Company price management ✓

## Next Steps

The database layer is complete and ready for integration with:
1. Models Layer (Task 3) - Pydantic models for validation
2. Business Logic Layer (Task 4) - Services using database operations
3. GUI Layer (Tasks 6-11) - User interface components
