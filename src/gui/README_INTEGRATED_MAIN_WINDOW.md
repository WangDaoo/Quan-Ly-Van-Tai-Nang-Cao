# Integrated Main Window

## Overview

The `IntegratedMainWindow` is the main application window that brings together all components of the Transport Management System. It provides a complete, production-ready interface with menu bar, toolbar, status bar, and multi-department support.

## Features

### 1. Menu Bar

#### File Menu
- **New**: Create a new record (Ctrl+N)
- **Import Excel**: Import data from Excel file (Ctrl+I)
- **Export Excel**: Export data to Excel file (Ctrl+E)
- **Exit**: Close the application (Ctrl+Q)

#### Edit Menu
- **Copy**: Copy selected cells (Ctrl+C)
- **Paste**: Paste cells (Ctrl+V)
- **Delete**: Delete selected rows (Delete)

#### View Menu
- **Column Visibility**: Show/hide table columns
- **Filters**: Toggle filter panel
- **Refresh**: Refresh current data (F5)

#### Tools Menu
- **Field Manager**: Manage field configurations
- **Formula Builder**: Build and test formulas
- **Push Conditions**: Configure workflow automation
- **Workspace Manager**: Manage employee workspaces
- **Statistics**: View system statistics
- **Workflow History**: View workflow execution history

#### Department Menu
- Quick switch between departments
- Department settings

#### Help Menu
- **User Manual**: Open user documentation (F1)
- **About**: About the application

### 2. Toolbar

Quick access buttons for common actions:
- New record
- Import/Export
- Filter toggle
- Settings
- Refresh

### 3. Status Bar

Displays:
- Total record count
- Current department
- Operation status messages

### 4. Multi-Department Support

- Tab-based interface for multiple departments
- Each department has:
  - Independent input form
  - Separate data table
  - Department-specific field configurations
  - Suggestion tabs with company prices

### 5. Window State Persistence

- Automatically saves and restores:
  - Window size and position
  - Last active department
  - Column widths and visibility
  - Splitter positions

## Architecture

```
IntegratedMainWindow
├── Menu Bar
│   ├── File Menu
│   ├── Edit Menu
│   ├── View Menu
│   ├── Tools Menu
│   ├── Department Menu
│   └── Help Menu
├── Toolbar
│   └── Quick Action Buttons
├── Central Widget
│   └── EmployeeTabWidget (Multi-Department)
│       ├── Department Tab 1
│       │   ├── Input Form Widget
│       │   ├── Main Table Widget
│       │   └── Suggestion Tab Widget
│       ├── Department Tab 2
│       └── Department Tab 3
├── Pagination Widget
└── Status Bar
    ├── Record Count
    └── Department Label
```

## Usage

### Basic Usage

```python
from PyQt6.QtWidgets import QApplication
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.gui.integrated_main_window import IntegratedMainWindow
from config import DATABASE_PATH

app = QApplication([])

# Initialize database
db_manager = EnhancedDatabaseManager(DATABASE_PATH)

# Create main window
window = IntegratedMainWindow(db_manager)
window.show()

app.exec()
```

### Accessing Current Department

```python
# Get current department ID
dept_id = window.employee_tabs.get_current_department_id()

# Get current department widget
dept_widget = window.employee_tabs.get_current_department_widget()

# Access form, table, or suggestions
if dept_widget:
    form = dept_widget.input_form
    table = dept_widget.main_table
    suggestions = dept_widget.suggestion_tabs
```

### Switching Departments

```python
# Switch to specific department
window.employee_tabs.switch_to_department(department_id)

# Or use menu action
window._on_switch_department(department_id)
```

### Refreshing Data

```python
# Refresh current department
window.employee_tabs.refresh_current_department()

# Refresh all departments
window.employee_tabs.refresh_all_departments()

# Update record count
window._update_record_count()
```

## Signals

The window emits the following signals:

- `windowClosing`: Emitted when window is closing
- Department-related signals are forwarded from `EmployeeTabWidget`:
  - `departmentChanged(int)`: Department tab changed
  - `tripCreated(int, dict)`: Trip created in department
  - `tripUpdated(int, dict)`: Trip updated in department

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New record |
| Ctrl+I | Import Excel |
| Ctrl+E | Export Excel |
| Ctrl+Q | Exit application |
| Ctrl+C | Copy cells |
| Ctrl+V | Paste cells |
| Delete | Delete rows |
| F5 | Refresh data |
| F1 | User manual |

## Configuration

### Window Settings

Settings are stored using `QSettings` with:
- Organization: "TransportApp"
- Application: "MainWindow"

Stored settings:
- `geometry`: Window size and position
- `windowState`: Toolbar and dock positions
- `lastDepartmentId`: Last active department

### Customization

```python
# Change window title
window.setWindowTitle("Custom Title")

# Change minimum size
window.setMinimumSize(1400, 900)

# Add custom menu items
custom_menu = window.menuBar().addMenu("Custom")
custom_action = QAction("Custom Action", window)
custom_menu.addAction(custom_action)

# Add custom toolbar buttons
custom_button = QAction("Custom", window)
window.toolbar.addAction(custom_button)
```

## Integration with Dialogs

The main window integrates with all dialog components:

```python
# Field Manager Dialog
from src.gui.dialogs.field_manager_dialog import FieldManagerDialog
dialog = FieldManagerDialog(field_config_service, dept_id, window)
dialog.exec()

# Formula Builder Dialog
from src.gui.dialogs.formula_builder_dialog import FormulaBuilderDialog
dialog = FormulaBuilderDialog(db_manager, dept_id, window)
dialog.exec()

# Push Conditions Dialog
from src.gui.dialogs.push_conditions_dialog import PushConditionsDialog
dialog = PushConditionsDialog(db_manager, dept_id, window)
dialog.exec()

# Workspace Manager Dialog
from src.gui.dialogs.workspace_manager_dialog import WorkspaceManagerDialog
dialog = WorkspaceManagerDialog(db_manager, window)
dialog.exec()

# Statistics Dialog
from src.gui.dialogs.statistics_dialog import StatisticsDialog
dialog = StatisticsDialog(db_manager, window)
dialog.exec()

# Workflow History Dialog
from src.gui.dialogs.workflow_history_dialog import WorkflowHistoryDialog
dialog = WorkflowHistoryDialog(db_manager, window)
dialog.exec()
```

## Best Practices

1. **Always use the database manager**: Pass the same `db_manager` instance to all services
2. **Handle errors gracefully**: Use try-except blocks and show user-friendly messages
3. **Update status bar**: Provide feedback for all operations
4. **Save window state**: Call `_save_window_state()` before closing
5. **Refresh data after changes**: Update tables and counts after CRUD operations

## Example: Complete Application

```python
"""
Complete Transport Management Application
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.gui.integrated_main_window import IntegratedMainWindow
from src.utils.logger import setup_logging
from config import DATABASE_PATH, APP_NAME, APP_VERSION


def main():
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    try:
        # Initialize database
        db_manager = EnhancedDatabaseManager(DATABASE_PATH)
        logger.info("Database initialized")
        
        # Create main window
        window = IntegratedMainWindow(db_manager)
        window.show()
        logger.info("Main window displayed")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Troubleshooting

### Window doesn't show
- Check if database is initialized correctly
- Verify all required services are available
- Check logs for errors

### Menu actions don't work
- Ensure signals are connected in `_setup_connections()`
- Check if current department widget is available
- Verify dialog imports are correct

### Data doesn't refresh
- Call `_update_record_count()` after data changes
- Use `refresh_current_department()` to reload data
- Check if pagination is updated

### Window state not saved
- Ensure `_save_window_state()` is called in `closeEvent()`
- Check QSettings organization and application names
- Verify write permissions for settings file

## Future Enhancements

- [ ] Add undo/redo functionality
- [ ] Implement advanced search dialog
- [ ] Add keyboard shortcut customization
- [ ] Implement theme/style switching
- [ ] Add window layout presets
- [ ] Implement multi-window support
- [ ] Add drag-and-drop file import
- [ ] Implement auto-save functionality
