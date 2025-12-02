"""
Unit tests for Excel-Like Table components
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.widgets import (
    ExcelHeaderView,
    ExcelLikeTable,
    ExcelFilterDialog,
    ColumnVisibilityDialog,
    CopyPasteHandler
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestExcelHeaderView:
    """Test ExcelHeaderView functionality"""
    
    def test_header_creation(self, qapp):
        """Test header can be created"""
        header = ExcelHeaderView(Qt.Orientation.Horizontal)
        assert header is not None
        assert header.sectionsMovable()
        
    def test_freeze_column(self, qapp):
        """Test column freezing"""
        header = ExcelHeaderView(Qt.Orientation.Horizontal)
        
        # Initially not frozen
        assert not header.isFrozen(0)
        
        # Freeze column
        header.freezeColumn(0)
        assert header.isFrozen(0)
        
        # Unfreeze column
        header.unfreezeColumn(0)
        assert not header.isFrozen(0)
        
    def test_filter_active(self, qapp):
        """Test filter active state"""
        header = ExcelHeaderView(Qt.Orientation.Horizontal)
        
        # Initially not active
        assert not header.isFilterActive(0)
        
        # Set active
        header.setFilterActive(0, True)
        assert header.isFilterActive(0)
        
        # Clear
        header.clearAllFilters()
        assert not header.isFilterActive(0)


class TestExcelLikeTable:
    """Test ExcelLikeTable functionality"""
    
    def test_table_creation(self, qapp):
        """Test table can be created"""
        table = ExcelLikeTable()
        assert table is not None
        
    def test_load_data(self, qapp):
        """Test loading data into table"""
        table = ExcelLikeTable()
        
        data = [
            {"Name": "John", "Age": 30},
            {"Name": "Jane", "Age": 25},
        ]
        columns = ["Name", "Age"]
        
        table.loadData(data, columns)
        
        assert table.rowCount() == 2
        assert table.columnCount() == 2
        
    def test_get_row_data(self, qapp):
        """Test getting row data"""
        table = ExcelLikeTable()
        
        data = [
            {"Name": "John", "Age": 30},
        ]
        columns = ["Name", "Age"]
        
        table.loadData(data, columns)
        row_data = table.getRowData(0)
        
        assert row_data["Name"] == "John"
        assert row_data["Age"] == 30
        
    def test_readonly_column(self, qapp):
        """Test read-only column"""
        table = ExcelLikeTable()
        
        # Set column 0 as read-only
        table.setColumnReadOnly(0, True)
        assert table.isColumnReadOnly(0)
        
        # Set back to editable
        table.setColumnReadOnly(0, False)
        assert not table.isColumnReadOnly(0)
        
    def test_auto_save_settings(self, qapp):
        """Test auto-save settings"""
        table = ExcelLikeTable()
        
        # Enable auto-save
        table.setAutoSaveEnabled(True)
        
        # Set delay
        table.setAutoSaveDelay(1000)
        
        # Should not raise any errors
        assert True
        
    def test_insert_row_operations(self, qapp):
        """Test row insertion operations"""
        table = ExcelLikeTable()
        
        data = [
            {"Name": "John", "Age": 30},
        ]
        columns = ["Name", "Age"]
        table.loadData(data, columns)
        
        initial_count = table.rowCount()
        
        # Insert row below
        table.insertRowBelow(0)
        assert table.rowCount() == initial_count + 1
        
        # Insert row above
        table.insertRowAbove(0)
        assert table.rowCount() == initial_count + 2
        
    def test_column_delegates(self, qapp):
        """Test setting column delegates"""
        table = ExcelLikeTable()
        
        data = [
            {"Name": "John", "Amount": 1000},
        ]
        columns = ["Name", "Amount"]
        table.loadData(data, columns)
        
        # Set number delegate
        table.setColumnDelegate(1, 'number')
        
        # Set currency delegate
        table.setColumnDelegate(1, 'currency', currency_symbol='USD')
        
        # Should not raise errors
        assert True


class TestCopyPasteHandler:
    """Test CopyPasteHandler functionality"""
    
    def test_handler_creation(self, qapp):
        """Test handler can be created"""
        table = ExcelLikeTable()
        handler = CopyPasteHandler(table)
        assert handler is not None
        
    def test_copy_cells(self, qapp):
        """Test copying cells"""
        table = ExcelLikeTable()
        
        data = [
            {"Name": "John", "Age": 30},
        ]
        columns = ["Name", "Age"]
        table.loadData(data, columns)
        
        # Select all cells
        table.selectAll()
        
        # Copy
        handler = CopyPasteHandler(table)
        copied_text = handler.copy_cells()
        
        assert "John" in copied_text
        assert "30" in copied_text


class TestExcelFilterDialog:
    """Test ExcelFilterDialog functionality"""
    
    def test_dialog_creation(self, qapp):
        """Test dialog can be created"""
        values = ["Value1", "Value2", "Value3"]
        dialog = ExcelFilterDialog("Test Column", values)
        assert dialog is not None
        
    def test_get_selected_values(self, qapp):
        """Test getting selected values"""
        values = ["Value1", "Value2", "Value3"]
        selected = {"Value1", "Value2"}
        
        dialog = ExcelFilterDialog("Test Column", values, selected)
        result = dialog.get_selected_values()
        
        # Should have 2 selected values
        assert len(result) == 2


class TestColumnVisibilityDialog:
    """Test ColumnVisibilityDialog functionality"""
    
    def test_dialog_creation(self, qapp):
        """Test dialog can be created"""
        columns = ["Column1", "Column2", "Column3"]
        dialog = ColumnVisibilityDialog(columns)
        assert dialog is not None
        
    def test_get_column_states(self, qapp):
        """Test getting column states"""
        columns = ["Column1", "Column2"]
        dialog = ColumnVisibilityDialog(columns)
        
        states = dialog.get_column_states()
        
        # Should have states for all columns
        assert len(states) >= len(columns)
        
        # All should be visible by default
        for state in states.values():
            assert state.get('visible', True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
