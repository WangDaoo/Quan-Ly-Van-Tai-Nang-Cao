"""
Excel Filter Dialog - Advanced filtering with checkbox list
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


class ExcelFilterDialog(QDialog):
    """
    Excel-style filter dialog with:
    - Checkbox list of unique values
    - Search box to filter the list
    - Select/Deselect all functionality
    """
    
    filterApplied = pyqtSignal(list)  # Emits list of selected values
    
    def __init__(self, column_name: str, values: List[str], 
                 selected_values: Set[str] = None, parent=None):
        super().__init__(parent)
        
        self.column_name = column_name
        self.all_values = sorted(set(values))  # Unique values, sorted
        self.selected_values = selected_values if selected_values else set(self.all_values)
        
        self.setWindowTitle(f"Filter - {column_name}")
        self.setModal(True)
        self.resize(300, 400)
        
        self._setup_ui()
        self._populate_list()
        
    def _setup_ui(self):
        """
        Setup the dialog UI
        """
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"Filter values for: {self.column_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.textChanged.connect(self._filter_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Select/Deselect all
        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        select_layout.addWidget(self.select_all_btn)
        select_layout.addWidget(self.deselect_all_btn)
        layout.addLayout(select_layout)
        
        # List widget with checkboxes
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Selection count
        self.count_label = QLabel()
        self._update_count_label()
        layout.addWidget(self.count_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def _populate_list(self):
        """
        Populate the list with checkboxes
        """
        self.list_widget.clear()
        
        for value in self.all_values:
            item = QListWidgetItem(str(value))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Set checked state
            if value in self.selected_values:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.list_widget.addItem(item)
            
        # Connect item changed signal
        self.list_widget.itemChanged.connect(self._update_count_label)
        
    def _filter_list(self, search_text: str):
        """
        Filter the list based on search text
        """
        search_text = search_text.lower()
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_text = item.text().lower()
            
            # Show/hide based on search
            if search_text in item_text:
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def _select_all(self):
        """
        Select all visible items
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)
                
        self._update_count_label()
        
    def _deselect_all(self):
        """
        Deselect all visible items
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Unchecked)
                
        self._update_count_label()
        
    def _update_count_label(self):
        """
        Update the selection count label
        """
        selected_count = 0
        total_count = self.list_widget.count()
        
        for i in range(total_count):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_count += 1
                
        self.count_label.setText(f"Selected: {selected_count} of {total_count}")
        
    def get_selected_values(self) -> List[str]:
        """
        Get the list of selected values
        """
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
                
        return selected
        
    def accept(self):
        """
        Handle OK button - emit selected values
        """
        selected = self.get_selected_values()
        self.filterApplied.emit(selected)
        super().accept()
