# Excel-Like Table Widget

A comprehensive Excel-like table widget for PyQt6 with advanced features including editable cells, copy/paste, filtering, keyboard shortcuts, and column management.

## Features

### 1. Excel Header View (`ExcelHeaderView`)

Custom header with Excel-like functionality:

- **Column Resizing**: Interactive column width adjustment
- **Drag & Drop Reordering**: Rearrange columns by dragging
- **Column Freezing**: Freeze columns for easier viewing
- **Filter Buttons**: Per-column filter buttons in header

```python
from src.gui.widgets import ExcelLikeTable

table = ExcelLikeTable()
header = table.horizontalHeader()

# Freeze a column
header.freezeColumn(0)

# Check if frozen
if header.isFrozen(0):
    print("Column 0 is frozen")

# Unfreeze
header.unfreezeColumn(0)
```

### 2. Excel-Like Table (`ExcelLikeTable`)

Main table widget with editable cells and formatting:

```python
from src.gui.widgets import ExcelLikeTable

table = ExcelLikeTable()

# Load data
data = [
    {"Name": "John", "Age": 30, "Salary": 50000},
    {"Name": "Jane", "Age": 25, "Salary": 45000},
]
columns = ["Name", "Age", "Salary"]
table.loadData(data, columns)

# Set column as read-only
table.setColumnReadOnly(0, True)

# Set number formatting
table.setColumnDelegate(1, 'number')

# Set currency formatting
table.setColumnDelegate(2, 'currency', currency_symbol='USD')

# Enable/disable auto-save
table.setAutoSaveEnabled(True)
table.setAutoSaveDelay(500)  # 500ms delay

# Connect signals
table.cellEdited.connect(on_cell_edited)
table.autoSaveTriggered.connect(on_auto_save)
```

### 3. Copy/Paste Functionality

Excel-compatible copy/paste with keyboard shortcuts:

**Keyboard Shortcuts:**
- `Ctrl+C`: Copy selected cells
- `Ctrl+V`: Paste into selected cells
- `Ctrl+Shift+V`: Paste as new rows

```python
# Programmatic copy/paste
table.copyCells()
table.pasteCells(overwrite=True)
table.pasteAsNewRows()
```

**Features:**
- Multi-cell selection support
- Tab-separated format (Excel compatible)
- Respects read-only columns
- Automatic row creation when pasting

### 4. Context Menu

Right-click context menu with row and column operations:

**Row Operations:**
- Insert Row Above
- Insert Row Below
- Duplicate Row
- Delete Row(s)
- Clear Content

**Copy/Paste Operations:**
- Copy
- Paste
- Paste as New Rows

**Column Operations:**
- Hide Column
- Show All Columns
- Auto-Resize Column
- Auto-Resize All Columns

```python
# Programmatic row operations
table.insertRowAbove(row)
table.insertRowBelow(row)
table.duplicateRow(row)
table.deleteSelectedRows()
table.clearSelectedCells()
```

### 5. Advanced Filtering

Excel-style filtering with checkbox dialog:

```python
# Filtering is triggered by clicking filter buttons in header
# Or programmatically:

# Clear specific column filter
table.clearColumnFilter(column_index)

# Clear all filters
table.clearAllFilters()

# Check if filters are active
if table.hasActiveFilters():
    print("Filters are active")

# Get active filters
filters = table.getActiveFilters()
```

**Filter Dialog Features:**
- Checkbox list of unique values
- Search box to filter the list
- Select/Deselect all buttons
- Multi-column filtering support
- Filter persistence

### 6. Keyboard Shortcuts

Excel-like keyboard navigation and operations:

| Shortcut | Action |
|----------|--------|
| `F2` | Edit current cell |
| `Enter` | Move down after edit |
| `Tab` | Move right |
| `Shift+Tab` | Move left |
| `Ctrl+C` | Copy selected cells |
| `Ctrl+V` | Paste cells |
| `Ctrl+Shift+V` | Paste as new rows |
| `Ctrl+D` | Duplicate current row |
| `Delete` | Delete selected rows or clear cell |
| `Ctrl++` | Insert row below |
| `Ctrl+Shift++` | Insert row above |

### 7. Column Management

Dialog for managing column visibility and width:

```python
# Show column management dialog
table.showColumnManagementDialog()

# Get current column states
states = table.getColumnStates()

# Save column states for persistence
saved_states = table.saveColumnStates()

# Load saved column states
table.loadColumnStates(saved_states)
```

**Column Management Features:**
- Show/hide columns
- Set custom column width
- Auto-resize columns
- Reset to defaults
- State persistence

## Complete Example

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from src.gui.widgets import ExcelLikeTable

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create table
        self.table = ExcelLikeTable()
        
        # Load data
        data = [
            {"ID": "C001", "Customer": "Company A", "Amount": 5000000},
            {"ID": "C002", "Customer": "Company B", "Amount": 3000000},
        ]
        columns = ["ID", "Customer", "Amount"]
        self.table.loadData(data, columns)
        
        # Configure columns
        self.table.setColumnReadOnly(0, True)  # ID is read-only
        self.table.setColumnDelegate(2, 'currency')  # Amount as currency
        
        # Connect signals
        self.table.cellEdited.connect(self.on_cell_edited)
        self.table.autoSaveTriggered.connect(self.on_auto_save)
        
        # Setup UI
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.table)
        self.setCentralWidget(central_widget)
        
    def on_cell_edited(self, row, col, old_value, new_value):
        print(f"Cell edited: ({row}, {col}) {old_value} -> {new_value}")
        
    def on_auto_save(self, row, col, value):
        print(f"Auto-save: ({row}, {col}) = {value}")
        # Save to database here

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
```

## API Reference

### ExcelLikeTable

#### Data Management
- `loadData(data: List[Dict], columns: List[str])` - Load data into table
- `getRowData(row: int) -> Dict` - Get data for a specific row
- `getAllData() -> List[Dict]` - Get all table data
- `setItemValue(row, col, value, store_original=True)` - Set cell value
- `getItemValue(row, col) -> Any` - Get cell value

#### Column Configuration
- `setColumnDelegate(column, delegate_type, **kwargs)` - Set column formatter
- `setColumnReadOnly(column, readonly=True)` - Set column as read-only
- `isColumnReadOnly(column) -> bool` - Check if column is read-only

#### Auto-Save
- `setAutoSaveEnabled(enabled: bool)` - Enable/disable auto-save
- `setAutoSaveDelay(delay_ms: int)` - Set auto-save delay

#### Copy/Paste
- `copyCells() -> str` - Copy selected cells
- `pasteCells(overwrite=True) -> bool` - Paste cells
- `pasteAsNewRows() -> bool` - Paste as new rows

#### Row Operations
- `insertRowAbove(row: int)` - Insert row above
- `insertRowBelow(row: int)` - Insert row below
- `duplicateRow(row: int)` - Duplicate row
- `deleteSelectedRows()` - Delete selected rows
- `clearSelectedCells()` - Clear selected cells

#### Filtering
- `clearColumnFilter(column: int)` - Clear column filter
- `clearAllFilters()` - Clear all filters
- `hasActiveFilters() -> bool` - Check if filters are active
- `getActiveFilters() -> Dict` - Get active filters

#### Column Management
- `showColumnManagementDialog()` - Show column management dialog
- `getColumnStates() -> Dict` - Get column states
- `saveColumnStates() -> Dict` - Save column states
- `loadColumnStates(states: Dict)` - Load column states

#### Visual
- `highlightRow(row: int, color: QColor)` - Highlight row
- `clearHighlight(row: int)` - Clear row highlight

### Signals

- `cellEdited(int, int, object, object)` - Emitted when cell is edited (row, col, old_value, new_value)
- `autoSaveTriggered(int, int, object)` - Emitted when auto-save is triggered (row, col, new_value)

## Requirements

- PyQt6 >= 6.0
- Python >= 3.8

## Demo

Run the demo to see all features in action:

```bash
python examples/excel_table_demo.py
```

## Notes

- The table uses debounced auto-save (default 500ms) to avoid excessive saves
- Copy/paste uses tab-separated format compatible with Excel
- Filters are applied in real-time and support multi-column filtering
- Column states can be persisted to maintain user preferences
- All keyboard shortcuts follow Excel conventions
