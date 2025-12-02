"""
Column Visibility Dialog - Manage column visibility and width
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ColumnVisibilityDialog(QDialog):
    """
    Dialog for managing column visibility and width:
    - Show/hide columns
    - Auto-resize columns
    - Set custom column width
    - Persist column state
    """
    
    columnsChanged = pyqtSignal(dict)  # Emits dict of column settings
    
    def __init__(self, column_names: List[str], column_states: Dict[int, dict] = None, parent=None):
        super().__init__(parent)
        
        self.column_names = column_names
        self.column_states = column_states if column_states else {}
        
        # Initialize default states if not provided
        for i, name in enumerate(column_names):
            if i not in self.column_states:
                self.column_states[i] = {
                    'visible': True,
                    'width': 100
                }
        
        self.setWindowTitle("Column Management")
        self.setModal(True)
        self.resize(400, 500)
        
        self._setup_ui()
        self._populate_list()
        
    def _setup_ui(self):
        """
        Setup the dialog UI
        """
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Manage Column Visibility and Width")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        # Column list
        list_group = QGroupBox("Columns")
        list_layout = QVBoxLayout(list_group)
        
        self.list_widget = QListWidget()
        list_layout.addWidget(self.list_widget)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        self.show_all_btn = QPushButton("Show All")
        self.show_all_btn.clicked.connect(self._show_all)
        self.hide_all_btn = QPushButton("Hide All")
        self.hide_all_btn.clicked.connect(self._hide_all)
        quick_layout.addWidget(self.show_all_btn)
        quick_layout.addWidget(self.hide_all_btn)
        list_layout.addLayout(quick_layout)
        
        layout.addWidget(list_group)
        
        # Width settings
        width_group = QGroupBox("Column Width")
        width_layout = QVBoxLayout(width_group)
        
        width_control_layout = QHBoxLayout()
        width_label = QLabel("Width (px):")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(50, 500)
        self.width_spinbox.setValue(100)
        self.width_spinbox.valueChanged.connect(self._update_selected_width)
        width_control_layout.addWidget(width_label)
        width_control_layout.addWidget(self.width_spinbox)
        width_control_layout.addStretch()
        width_layout.addLayout(width_control_layout)
        
        width_btn_layout = QHBoxLayout()
        self.auto_resize_btn = QPushButton("Auto-Resize Selected")
        self.auto_resize_btn.clicked.connect(self._auto_resize_selected)
        self.auto_resize_all_btn = QPushButton("Auto-Resize All")
        self.auto_resize_all_btn.clicked.connect(self._auto_resize_all)
        width_btn_layout.addWidget(self.auto_resize_btn)
        width_btn_layout.addWidget(self.auto_resize_all_btn)
        width_layout.addLayout(width_btn_layout)
        
        layout.addWidget(width_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect list selection
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _populate_list(self):
        """
        Populate the list with columns
        """
        self.list_widget.clear()
        
        for i, name in enumerate(self.column_names):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Set checked state based on visibility
            state = self.column_states.get(i, {'visible': True})
            if state.get('visible', True):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            # Store column index
            item.setData(Qt.ItemDataRole.UserRole, i)
            
            self.list_widget.addItem(item)
            
    def _show_all(self):
        """
        Show all columns
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Checked)
            
    def _hide_all(self):
        """
        Hide all columns
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
            
    def _on_selection_changed(self):
        """
        Handle selection change - update width spinbox
        """
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            col_index = item.data(Qt.ItemDataRole.UserRole)
            state = self.column_states.get(col_index, {'width': 100})
            self.width_spinbox.setValue(state.get('width', 100))
            
    def _update_selected_width(self, width: int):
        """
        Update width for selected column
        """
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            col_index = item.data(Qt.ItemDataRole.UserRole)
            if col_index not in self.column_states:
                self.column_states[col_index] = {}
            self.column_states[col_index]['width'] = width
            
    def _auto_resize_selected(self):
        """
        Mark selected column for auto-resize
        """
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            col_index = item.data(Qt.ItemDataRole.UserRole)
            if col_index not in self.column_states:
                self.column_states[col_index] = {}
            self.column_states[col_index]['auto_resize'] = True
            
    def _auto_resize_all(self):
        """
        Mark all columns for auto-resize
        """
        for i in range(len(self.column_names)):
            if i not in self.column_states:
                self.column_states[i] = {}
            self.column_states[i]['auto_resize'] = True
            
    def _reset_defaults(self):
        """
        Reset all columns to default settings
        """
        self.column_states = {}
        for i in range(len(self.column_names)):
            self.column_states[i] = {
                'visible': True,
                'width': 100
            }
        self._populate_list()
        
    def get_column_states(self) -> Dict[int, dict]:
        """
        Get the column states with visibility and width
        """
        # Update visibility from checkboxes
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            col_index = item.data(Qt.ItemDataRole.UserRole)
            
            if col_index not in self.column_states:
                self.column_states[col_index] = {}
                
            self.column_states[col_index]['visible'] = (
                item.checkState() == Qt.CheckState.Checked
            )
            
        return self.column_states
        
    def accept(self):
        """
        Handle OK button - emit column states
        """
        states = self.get_column_states()
        self.columnsChanged.emit(states)
        super().accept()
