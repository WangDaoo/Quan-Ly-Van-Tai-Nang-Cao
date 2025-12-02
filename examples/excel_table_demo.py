"""
Demo for Excel-Like Table Features

This demo showcases:
- Excel header with column resizing, reordering, freezing, and filtering
- Editable cells with auto-save
- Number and currency formatting
- Copy/Paste functionality (Ctrl+C, Ctrl+V, Ctrl+Shift+V)
- Context menu with row operations
- Advanced filtering with checkbox dialog
- Keyboard shortcuts (F2, Enter, Tab, Ctrl+D, Delete, etc.)
- Column management dialog
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, '..')

from src.gui.widgets import ExcelLikeTable


class ExcelTableDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel-Like Table Demo")
        self.resize(1000, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Info label
        info_label = QLabel(
            "<b>Excel-Like Table Features:</b><br>"
            "• <b>F2</b>: Edit cell<br>"
            "• <b>Enter</b>: Move down, <b>Tab</b>: Move right, <b>Shift+Tab</b>: Move left<br>"
            "• <b>Ctrl+C</b>: Copy, <b>Ctrl+V</b>: Paste, <b>Ctrl+Shift+V</b>: Paste as new rows<br>"
            "• <b>Ctrl+D</b>: Duplicate row, <b>Delete</b>: Delete rows<br>"
            "• <b>Ctrl++</b>: Insert row below, <b>Ctrl+Shift++</b>: Insert row above<br>"
            "• <b>Right-click</b>: Context menu with row/column operations<br>"
            "• <b>Click filter icon</b> in header to filter columns<br>"
            "• <b>Drag columns</b> to reorder, <b>Right-click header</b> for freeze/unfreeze"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Create table
        self.table = ExcelLikeTable()
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Sample Data")
        load_btn.clicked.connect(self.load_sample_data)
        button_layout.addWidget(load_btn)
        
        column_mgmt_btn = QPushButton("Column Management")
        column_mgmt_btn.clicked.connect(self.table.showColumnManagementDialog)
        button_layout.addWidget(column_mgmt_btn)
        
        clear_filters_btn = QPushButton("Clear All Filters")
        clear_filters_btn.clicked.connect(self.table.clearAllFilters)
        button_layout.addWidget(clear_filters_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.table.cellEdited.connect(self.on_cell_edited)
        self.table.autoSaveTriggered.connect(self.on_auto_save)
        
        # Load initial data
        self.load_sample_data()
        
    def load_sample_data(self):
        """Load sample data into the table"""
        # Sample data
        data = [
            {"Mã chuyến": "C001", "Khách hàng": "Công ty A", "Điểm đi": "Hà Nội", "Điểm đến": "TP.HCM", "Giá cả": 5000000, "Khoán lương": 3000000, "Chi phí khác": 500000},
            {"Mã chuyến": "C002", "Khách hàng": "Công ty B", "Điểm đi": "Đà Nẵng", "Điểm đến": "Hà Nội", "Giá cả": 3000000, "Khoán lương": 2000000, "Chi phí khác": 300000},
            {"Mã chuyến": "C003", "Khách hàng": "Công ty A", "Điểm đi": "TP.HCM", "Điểm đến": "Cần Thơ", "Giá cả": 2000000, "Khoán lương": 1500000, "Chi phí khác": 200000},
            {"Mã chuyến": "C004", "Khách hàng": "Công ty C", "Điểm đi": "Hà Nội", "Điểm đến": "Hải Phòng", "Giá cả": 1500000, "Khoán lương": 1000000, "Chi phí khác": 150000},
            {"Mã chuyến": "C005", "Khách hàng": "Công ty B", "Điểm đi": "TP.HCM", "Điểm đến": "Đà Nẵng", "Giá cả": 3500000, "Khoán lương": 2500000, "Chi phí khác": 400000},
            {"Mã chuyến": "C006", "Khách hàng": "Công ty A", "Điểm đi": "Hà Nội", "Điểm đến": "Vinh", "Giá cả": 2500000, "Khoán lương": 1800000, "Chi phí khác": 250000},
            {"Mã chuyến": "C007", "Khách hàng": "Công ty D", "Điểm đi": "Đà Nẵng", "Điểm đến": "Quy Nhơn", "Giá cả": 1800000, "Khoán lương": 1200000, "Chi phí khác": 180000},
            {"Mã chuyến": "C008", "Khách hàng": "Công ty C", "Điểm đi": "TP.HCM", "Điểm đến": "Vũng Tàu", "Giá cả": 1200000, "Khoán lương": 800000, "Chi phí khác": 120000},
            {"Mã chuyến": "C009", "Khách hàng": "Công ty B", "Điểm đi": "Hà Nội", "Điểm đến": "Thanh Hóa", "Giá cả": 2200000, "Khoán lương": 1600000, "Chi phí khác": 220000},
            {"Mã chuyến": "C010", "Khách hàng": "Công ty A", "Điểm đi": "TP.HCM", "Điểm đến": "Nha Trang", "Giá cả": 2800000, "Khoán lương": 2000000, "Chi phí khác": 280000},
        ]
        
        columns = ["Mã chuyến", "Khách hàng", "Điểm đi", "Điểm đến", "Giá cả", "Khoán lương", "Chi phí khác"]
        
        # Load data
        self.table.loadData(data, columns)
        
        # Set column 0 (Mã chuyến) as read-only
        self.table.setColumnReadOnly(0, True)
        
        # Set currency formatting for price columns
        self.table.setColumnDelegate(4, 'currency')  # Giá cả
        self.table.setColumnDelegate(5, 'currency')  # Khoán lương
        self.table.setColumnDelegate(6, 'currency')  # Chi phí khác
        
        self.status_label.setText(f"Loaded {len(data)} rows")
        
    def on_cell_edited(self, row, col, old_value, new_value):
        """Handle cell edit"""
        self.status_label.setText(f"Cell ({row}, {col}) changed from '{old_value}' to '{new_value}'")
        
    def on_auto_save(self, row, col, value):
        """Handle auto-save"""
        self.status_label.setText(f"Auto-saved: Row {row}, Column {col} = {value}")


def main():
    app = QApplication(sys.argv)
    demo = ExcelTableDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
