"""
Copy/Paste Handler - Excel-compatible copy/paste functionality
"""

from PyQt6.QtWidgets import QTableWidget, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CopyPasteHandler:
    """
    Handler for copy/paste operations with Excel compatibility
    """
    
    def __init__(self, table: QTableWidget):
        self.table = table
        
    def copy_cells(self) -> str:
        """
        Copy selected cells to clipboard in Excel-compatible format
        Returns the copied text
        """
        selection = self.table.selectedRanges()
        if not selection:
            return ""
            
        # Get the selection range
        sel_range = selection[0]
        top_row = sel_range.topRow()
        bottom_row = sel_range.bottomRow()
        left_col = sel_range.leftColumn()
        right_col = sel_range.rightColumn()
        
        # Build tab-separated text (Excel format)
        lines = []
        for row in range(top_row, bottom_row + 1):
            cells = []
            for col in range(left_col, right_col + 1):
                item = self.table.item(row, col)
                if item:
                    cells.append(str(item.text()))
                else:
                    cells.append("")
            lines.append("\t".join(cells))
            
        text = "\n".join(lines)
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        logger.debug(f"Copied {len(lines)} rows, {right_col - left_col + 1} columns")
        return text
        
    def paste_cells(self, overwrite: bool = True) -> bool:
        """
        Paste clipboard content into selected cells
        
        Args:
            overwrite: If True, overwrite existing cells. If False, skip non-empty cells
            
        Returns:
            True if paste was successful
        """
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text:
            return False
            
        # Get current selection
        selection = self.table.selectedRanges()
        if not selection:
            # No selection, use current cell
            current_row = self.table.currentRow()
            current_col = self.table.currentColumn()
            if current_row < 0 or current_col < 0:
                return False
            start_row = current_row
            start_col = current_col
        else:
            sel_range = selection[0]
            start_row = sel_range.topRow()
            start_col = sel_range.leftColumn()
            
        # Parse clipboard data (tab-separated, newline-separated)
        lines = text.split("\n")
        rows_data = []
        for line in lines:
            if line:  # Skip empty lines
                rows_data.append(line.split("\t"))
                
        if not rows_data:
            return False
            
        # Paste data
        for row_offset, row_data in enumerate(rows_data):
            target_row = start_row + row_offset
            
            # Check if we need to add rows
            if target_row >= self.table.rowCount():
                self.table.setRowCount(target_row + 1)
                
            for col_offset, cell_value in enumerate(row_data):
                target_col = start_col + col_offset
                
                # Check if column exists
                if target_col >= self.table.columnCount():
                    continue
                    
                # Check if column is read-only
                if hasattr(self.table, 'isColumnReadOnly') and self.table.isColumnReadOnly(target_col):
                    continue
                    
                # Get or create item
                item = self.table.item(target_row, target_col)
                if not item:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    item = QTableWidgetItem()
                    self.table.setItem(target_row, target_col, item)
                    
                # Paste value
                if overwrite or not item.text():
                    item.setText(cell_value)
                    
        logger.debug(f"Pasted {len(rows_data)} rows starting at ({start_row}, {start_col})")
        return True
        
    def paste_as_new_rows(self) -> bool:
        """
        Paste clipboard content as new rows at the end of the table
        
        Returns:
            True if paste was successful
        """
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text:
            return False
            
        # Parse clipboard data
        lines = text.split("\n")
        rows_data = []
        for line in lines:
            if line:  # Skip empty lines
                rows_data.append(line.split("\t"))
                
        if not rows_data:
            return False
            
        # Add new rows at the end
        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(rows_data))
        
        # Paste data
        for row_offset, row_data in enumerate(rows_data):
            target_row = start_row + row_offset
            
            for col_offset, cell_value in enumerate(row_data):
                # Check if column exists
                if col_offset >= self.table.columnCount():
                    continue
                    
                # Check if column is read-only
                if hasattr(self.table, 'isColumnReadOnly') and self.table.isColumnReadOnly(col_offset):
                    continue
                    
                # Create item
                from PyQt6.QtWidgets import QTableWidgetItem
                item = QTableWidgetItem(cell_value)
                self.table.setItem(target_row, col_offset, item)
                
        logger.debug(f"Pasted {len(rows_data)} new rows starting at row {start_row}")
        return True
        
    def handle_key_event(self, event: QKeyEvent) -> bool:
        """
        Handle keyboard shortcuts for copy/paste
        
        Returns:
            True if event was handled
        """
        # Ctrl+C - Copy
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.copy_cells()
            return True
            
        # Ctrl+V - Paste
        elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_cells()
            return True
            
        # Ctrl+Shift+V - Paste as new rows
        elif (event.key() == Qt.Key.Key_V and 
              event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            self.paste_as_new_rows()
            return True
            
        return False
        
    def get_selected_range(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the selected range as (top_row, left_col, bottom_row, right_col)
        """
        selection = self.table.selectedRanges()
        if not selection:
            return None
            
        sel_range = selection[0]
        return (
            sel_range.topRow(),
            sel_range.leftColumn(),
            sel_range.bottomRow(),
            sel_range.rightColumn()
        )
        
    def select_range(self, top_row: int, left_col: int, bottom_row: int, right_col: int):
        """
        Select a range of cells
        """
        from PyQt6.QtWidgets import QTableWidgetSelectionRange
        sel_range = QTableWidgetSelectionRange(top_row, left_col, bottom_row, right_col)
        self.table.setRangeSelected(sel_range, True)
