"""
Excel-Like Table Widget - Table with editable cells, auto-save, and number formatting
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QStyledItemDelegate, 
    QStyleOptionViewItem, QWidget, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex, QTimer, QPoint
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from typing import Optional, Callable, Dict, Any, List, Set
from decimal import Decimal
import logging

from .excel_header_view import ExcelHeaderView
from .copy_paste_handler import CopyPasteHandler
from .excel_filter_dialog import ExcelFilterDialog
from .column_visibility_dialog import ColumnVisibilityDialog

logger = logging.getLogger(__name__)


class NumberFormatDelegate(QStyledItemDelegate):
    """
    Delegate for formatting numbers with thousand separators
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def displayText(self, value, locale):
        """
        Format numbers with thousand separators
        """
        if isinstance(value, (int, float, Decimal)):
            try:
                # Format with thousand separators
                if isinstance(value, float) or isinstance(value, Decimal):
                    return f"{value:,.2f}"
                else:
                    return f"{value:,}"
            except:
                return str(value)
        return str(value)


class CurrencyFormatDelegate(QStyledItemDelegate):
    """
    Delegate for formatting currency values
    """
    
    def __init__(self, currency_symbol: str = "VND", parent=None):
        super().__init__(parent)
        self.currency_symbol = currency_symbol
        
    def displayText(self, value, locale):
        """
        Format currency with symbol and thousand separators
        """
        if isinstance(value, (int, float, Decimal)):
            try:
                formatted = f"{int(value):,}"
                return f"{formatted} {self.currency_symbol}"
            except:
                return str(value)
        return str(value)


class ExcelLikeTable(QTableWidget):
    """
    Excel-like table widget with:
    - Editable cells with proper delegates
    - Auto-save on cell edit
    - Number formatting delegates
    - Custom header with filtering
    """
    
    # Signals
    cellEdited = pyqtSignal(int, int, object, object)  # row, col, old_value, new_value
    autoSaveTriggered = pyqtSignal(int, int, object)   # row, col, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup custom header
        self._setup_header()
        
        # Enable editing
        self.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked | 
            QTableWidget.EditTrigger.EditKeyPressed |
            QTableWidget.EditTrigger.AnyKeyPressed
        )
        
        # Visual settings
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Auto-save settings
        self._auto_save_enabled = True
        self._auto_save_delay = 500  # ms
        self._auto_save_timer = QTimer()
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.timeout.connect(self._perform_auto_save)
        self._pending_save: Optional[tuple] = None
        
        # Column delegates
        self._column_delegates: Dict[int, QStyledItemDelegate] = {}
        
        # Read-only columns
        self._readonly_columns: set = set()
        
        # Track original values for change detection
        self._original_values: Dict[tuple, Any] = {}
        
        # Copy/Paste handler
        self._copy_paste_handler = CopyPasteHandler(self)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Filtering
        self._column_filters: Dict[int, Set[str]] = {}  # Column -> selected values
        self._all_data: List[Dict[str, Any]] = []  # Store all data for filtering
        self._filtered_rows: Set[int] = set()  # Rows that pass all filters
        
        # Column management
        self._column_states: Dict[int, dict] = {}  # Column -> {visible, width}
        
        # Connect header filter signal
        h_header = self.horizontalHeader()
        if isinstance(h_header, ExcelHeaderView):
            h_header.filterClicked.connect(self._show_filter_dialog)
        
        # Connect signals
        self.itemChanged.connect(self._handle_item_changed)
        
    def _setup_header(self):
        """
        Setup custom Excel header view
        """
        # Horizontal header
        h_header = ExcelHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(h_header)
        
        # Vertical header
        v_header = self.verticalHeader()
        v_header.setDefaultSectionSize(30)
        v_header.setSectionResizeMode(v_header.ResizeMode.Fixed)
        
    def setColumnDelegate(self, column: int, delegate_type: str, **kwargs):
        """
        Set a delegate for a specific column
        
        Args:
            column: Column index
            delegate_type: 'number', 'currency', or custom
            **kwargs: Additional arguments for the delegate
        """
        if delegate_type == 'number':
            delegate = NumberFormatDelegate(self)
        elif delegate_type == 'currency':
            currency_symbol = kwargs.get('currency_symbol', 'VND')
            delegate = CurrencyFormatDelegate(currency_symbol, self)
        else:
            return
            
        self._column_delegates[column] = delegate
        self.setItemDelegateForColumn(column, delegate)
        
    def setColumnReadOnly(self, column: int, readonly: bool = True):
        """
        Set a column as read-only
        """
        if readonly:
            self._readonly_columns.add(column)
        else:
            self._readonly_columns.discard(column)
            
        # Update existing items
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item:
                if readonly:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    
    def isColumnReadOnly(self, column: int) -> bool:
        """
        Check if a column is read-only
        """
        return column in self._readonly_columns
        
    def setAutoSaveEnabled(self, enabled: bool):
        """
        Enable or disable auto-save functionality
        """
        self._auto_save_enabled = enabled
        
    def setAutoSaveDelay(self, delay_ms: int):
        """
        Set the auto-save delay in milliseconds
        """
        self._auto_save_delay = delay_ms
        
    def _handle_item_changed(self, item: QTableWidgetItem):
        """
        Handle item change - trigger auto-save if enabled
        """
        if not self._auto_save_enabled:
            return
            
        row = item.row()
        col = item.column()
        
        # Check if column is read-only
        if col in self._readonly_columns:
            return
            
        # Get old and new values
        key = (row, col)
        old_value = self._original_values.get(key)
        new_value = item.data(Qt.ItemDataRole.DisplayRole)
        
        # Only trigger if value actually changed
        if old_value != new_value:
            self.cellEdited.emit(row, col, old_value, new_value)
            
            # Schedule auto-save
            self._pending_save = (row, col, new_value)
            self._auto_save_timer.start(self._auto_save_delay)
            
            # Update original value
            self._original_values[key] = new_value
            
    def _perform_auto_save(self):
        """
        Perform the pending auto-save
        """
        if self._pending_save:
            row, col, value = self._pending_save
            self.autoSaveTriggered.emit(row, col, value)
            self._pending_save = None
            
    def setItemValue(self, row: int, col: int, value: Any, store_original: bool = True):
        """
        Set item value and optionally store as original (to prevent auto-save trigger)
        """
        item = self.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.setItem(row, col, item)
            
        # Temporarily disconnect to avoid triggering auto-save
        self.itemChanged.disconnect(self._handle_item_changed)
        
        item.setData(Qt.ItemDataRole.DisplayRole, value)
        
        if store_original:
            self._original_values[(row, col)] = value
            
        # Apply read-only if needed
        if col in self._readonly_columns:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
        self.itemChanged.connect(self._handle_item_changed)
        
    def getItemValue(self, row: int, col: int) -> Any:
        """
        Get item value
        """
        item = self.item(row, col)
        if item:
            return item.data(Qt.ItemDataRole.DisplayRole)
        return None
        
    def loadData(self, data: List[Dict[str, Any]], columns: List[str]):
        """
        Load data into the table
        
        Args:
            data: List of dictionaries with row data
            columns: List of column names
        """
        # Clear existing data
        self.clear()
        self._original_values.clear()
        
        # Set dimensions
        self.setRowCount(len(data))
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Populate data
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                value = row_data.get(col_name, "")
                self.setItemValue(row_idx, col_idx, value, store_original=True)
                
    def getRowData(self, row: int) -> Dict[str, Any]:
        """
        Get all data for a specific row
        """
        data = {}
        for col in range(self.columnCount()):
            header = self.horizontalHeaderItem(col)
            col_name = header.text() if header else f"col_{col}"
            data[col_name] = self.getItemValue(row, col)
        return data
        
    def getAllData(self) -> List[Dict[str, Any]]:
        """
        Get all table data
        """
        data = []
        for row in range(self.rowCount()):
            data.append(self.getRowData(row))
        return data
        
    def highlightRow(self, row: int, color: QColor):
        """
        Highlight a specific row with a color
        """
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(color)
                
    def clearHighlight(self, row: int):
        """
        Clear highlight from a specific row
        """
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QColor(Qt.GlobalColor.white))
                
    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle keyboard events including copy/paste shortcuts and Excel-like navigation
        """
        # Try copy/paste handler first
        if self._copy_paste_handler.handle_key_event(event):
            return
            
        # F2 - Edit cell
        if event.key() == Qt.Key.Key_F2:
            current_item = self.currentItem()
            if current_item and current_item.column() not in self._readonly_columns:
                self.editItem(current_item)
            return
            
        # Enter - Move down
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.state() == QTableWidget.State.EditingState:
                # If editing, finish edit and move down
                super().keyPressEvent(event)
                self._move_selection(1, 0)
            else:
                # If not editing, just move down
                self._move_selection(1, 0)
            return
            
        # Tab - Move right
        if event.key() == Qt.Key.Key_Tab:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+Tab - Move left
                self._move_selection(0, -1)
            else:
                # Tab - Move right
                self._move_selection(0, 1)
            return
            
        # Ctrl+D - Duplicate row
        if event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            current_row = self.currentRow()
            if current_row >= 0:
                self.duplicateRow(current_row)
            return
            
        # Delete - Delete rows
        if event.key() == Qt.Key.Key_Delete:
            if self.state() != QTableWidget.State.EditingState:
                # Only delete rows if not editing a cell
                selected_rows = set(item.row() for item in self.selectedItems())
                if selected_rows:
                    self.deleteSelectedRows()
                else:
                    # Clear current cell
                    self.clearSelectedCells()
            return
            
        # Ctrl+Plus - Insert row below
        if event.key() == Qt.Key.Key_Plus and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            current_row = self.currentRow()
            if current_row >= 0:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Ctrl+Shift+Plus - Insert row above
                    self.insertRowAbove(current_row)
                else:
                    # Ctrl+Plus - Insert row below
                    self.insertRowBelow(current_row)
            return
            
        # Default handling
        super().keyPressEvent(event)
        
    def _move_selection(self, row_delta: int, col_delta: int):
        """
        Move selection by the specified delta
        """
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        new_row = current_row + row_delta
        new_col = current_col + col_delta
        
        # Clamp to valid range
        new_row = max(0, min(new_row, self.rowCount() - 1))
        new_col = max(0, min(new_col, self.columnCount() - 1))
        
        # Set new current cell
        self.setCurrentCell(new_row, new_col)
        
    def copyCells(self) -> str:
        """
        Copy selected cells to clipboard
        """
        return self._copy_paste_handler.copy_cells()
        
    def pasteCells(self, overwrite: bool = True) -> bool:
        """
        Paste clipboard content into selected cells
        """
        return self._copy_paste_handler.paste_cells(overwrite)
        
    def pasteAsNewRows(self) -> bool:
        """
        Paste clipboard content as new rows
        """
        return self._copy_paste_handler.paste_as_new_rows()
        
    def _show_context_menu(self, pos: QPoint):
        """
        Show context menu with row and column operations
        """
        menu = QMenu(self)
        
        # Get current row
        current_row = self.rowAt(pos.y())
        current_col = self.columnAt(pos.x())
        
        # Row operations
        if current_row >= 0:
            insert_above_action = menu.addAction("Insert Row Above")
            insert_above_action.triggered.connect(lambda: self.insertRowAbove(current_row))
            
            insert_below_action = menu.addAction("Insert Row Below")
            insert_below_action.triggered.connect(lambda: self.insertRowBelow(current_row))
            
            duplicate_action = menu.addAction("Duplicate Row")
            duplicate_action.triggered.connect(lambda: self.duplicateRow(current_row))
            
            menu.addSeparator()
            
            delete_action = menu.addAction("Delete Row(s)")
            delete_action.triggered.connect(self.deleteSelectedRows)
            
            clear_action = menu.addAction("Clear Content")
            clear_action.triggered.connect(self.clearSelectedCells)
            
            menu.addSeparator()
            
        # Copy/Paste operations
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copyCells)
        copy_action.setShortcut("Ctrl+C")
        
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(lambda: self.pasteCells())
        paste_action.setShortcut("Ctrl+V")
        
        paste_new_action = menu.addAction("Paste as New Rows")
        paste_new_action.triggered.connect(self.pasteAsNewRows)
        paste_new_action.setShortcut("Ctrl+Shift+V")
        
        # Column operations submenu
        if current_col >= 0:
            menu.addSeparator()
            column_menu = menu.addMenu("Column Operations")
            
            hide_col_action = column_menu.addAction("Hide Column")
            hide_col_action.triggered.connect(lambda: self.hideColumn(current_col))
            
            show_all_action = column_menu.addAction("Show All Columns")
            show_all_action.triggered.connect(self.showAllColumns)
            
            column_menu.addSeparator()
            
            auto_resize_action = column_menu.addAction("Auto-Resize Column")
            auto_resize_action.triggered.connect(lambda: self.resizeColumnToContents(current_col))
            
            auto_resize_all_action = column_menu.addAction("Auto-Resize All Columns")
            auto_resize_all_action.triggered.connect(self.resizeColumnsToContents)
        
        menu.exec(self.mapToGlobal(pos))
        
    def insertRowAbove(self, row: int):
        """
        Insert a new row above the specified row
        """
        self.insertRow(row)
        logger.debug(f"Inserted row above row {row}")
        
    def insertRowBelow(self, row: int):
        """
        Insert a new row below the specified row
        """
        self.insertRow(row + 1)
        logger.debug(f"Inserted row below row {row}")
        
    def duplicateRow(self, row: int):
        """
        Duplicate the specified row
        """
        # Insert new row below
        self.insertRow(row + 1)
        
        # Copy data from original row
        for col in range(self.columnCount()):
            original_item = self.item(row, col)
            if original_item:
                new_item = QTableWidgetItem(original_item)
                self.setItem(row + 1, col, new_item)
                
        logger.debug(f"Duplicated row {row}")
        
    def deleteSelectedRows(self):
        """
        Delete all selected rows
        """
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
            
        # Delete in reverse order to maintain indices
        for row in sorted(selected_rows, reverse=True):
            self.removeRow(row)
            
        logger.debug(f"Deleted {len(selected_rows)} rows")
        
    def clearSelectedCells(self):
        """
        Clear content of selected cells
        """
        for item in self.selectedItems():
            if item.column() not in self._readonly_columns:
                item.setText("")
                
        logger.debug("Cleared selected cells")
        
    def showAllColumns(self):
        """
        Show all hidden columns
        """
        for col in range(self.columnCount()):
            self.showColumn(col)
            
    def _show_filter_dialog(self, column: int):
        """
        Show filter dialog for a column
        """
        # Get column name
        header_item = self.horizontalHeaderItem(column)
        column_name = header_item.text() if header_item else f"Column {column}"
        
        # Get all unique values in this column
        values = []
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item:
                values.append(item.text())
                
        # Get currently selected values
        selected_values = self._column_filters.get(column, set(values))
        
        # Show dialog
        dialog = ExcelFilterDialog(column_name, values, selected_values, self)
        if dialog.exec():
            selected = dialog.get_selected_values()
            self._apply_column_filter(column, selected)
            
    def _apply_column_filter(self, column: int, selected_values: List[str]):
        """
        Apply filter to a column
        """
        # Store filter
        self._column_filters[column] = set(selected_values)
        
        # Update header to show filter is active
        h_header = self.horizontalHeader()
        if isinstance(h_header, ExcelHeaderView):
            h_header.setFilterActive(column, len(selected_values) < self._get_unique_count(column))
            
        # Apply all filters
        self._apply_all_filters()
        
    def _get_unique_count(self, column: int) -> int:
        """
        Get count of unique values in a column
        """
        values = set()
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item:
                values.add(item.text())
        return len(values)
        
    def _apply_all_filters(self):
        """
        Apply all active filters to show/hide rows
        """
        if not self._column_filters:
            # No filters, show all rows
            for row in range(self.rowCount()):
                self.setRowHidden(row, False)
            return
            
        # Check each row against all filters
        for row in range(self.rowCount()):
            show_row = True
            
            for column, selected_values in self._column_filters.items():
                item = self.item(row, column)
                item_value = item.text() if item else ""
                
                if item_value not in selected_values:
                    show_row = False
                    break
                    
            self.setRowHidden(row, not show_row)
            
        logger.debug(f"Applied {len(self._column_filters)} column filters")
        
    def clearColumnFilter(self, column: int):
        """
        Clear filter for a specific column
        """
        if column in self._column_filters:
            del self._column_filters[column]
            
            # Update header
            h_header = self.horizontalHeader()
            if isinstance(h_header, ExcelHeaderView):
                h_header.setFilterActive(column, False)
                
            # Reapply remaining filters
            self._apply_all_filters()
            
    def clearAllFilters(self):
        """
        Clear all column filters
        """
        self._column_filters.clear()
        
        # Update header
        h_header = self.horizontalHeader()
        if isinstance(h_header, ExcelHeaderView):
            h_header.clearAllFilters()
            
        # Show all rows
        for row in range(self.rowCount()):
            self.setRowHidden(row, False)
            
        logger.debug("Cleared all filters")
        
    def getActiveFilters(self) -> Dict[int, Set[str]]:
        """
        Get all active filters
        """
        return self._column_filters.copy()
        
    def hasActiveFilters(self) -> bool:
        """
        Check if any filters are active
        """
        return len(self._column_filters) > 0
        
    def showColumnManagementDialog(self):
        """
        Show column management dialog
        """
        # Get column names
        column_names = []
        for col in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(col)
            column_names.append(header_item.text() if header_item else f"Column {col}")
            
        # Get current column states
        for col in range(self.columnCount()):
            if col not in self._column_states:
                self._column_states[col] = {
                    'visible': not self.isColumnHidden(col),
                    'width': self.columnWidth(col)
                }
                
        # Show dialog
        dialog = ColumnVisibilityDialog(column_names, self._column_states, self)
        dialog.columnsChanged.connect(self._apply_column_states)
        dialog.exec()
        
    def _apply_column_states(self, states: Dict[int, dict]):
        """
        Apply column visibility and width settings
        """
        self._column_states = states
        
        for col, state in states.items():
            # Apply visibility
            visible = state.get('visible', True)
            self.setColumnHidden(col, not visible)
            
            # Apply width
            if state.get('auto_resize', False):
                self.resizeColumnToContents(col)
            else:
                width = state.get('width', 100)
                self.setColumnWidth(col, width)
                
        logger.debug(f"Applied column states for {len(states)} columns")
        
    def getColumnStates(self) -> Dict[int, dict]:
        """
        Get current column states
        """
        states = {}
        for col in range(self.columnCount()):
            states[col] = {
                'visible': not self.isColumnHidden(col),
                'width': self.columnWidth(col)
            }
        return states
        
    def saveColumnStates(self) -> Dict[int, dict]:
        """
        Save current column states for persistence
        """
        return self.getColumnStates()
        
    def loadColumnStates(self, states: Dict[int, dict]):
        """
        Load and apply saved column states
        """
        self._apply_column_states(states)
