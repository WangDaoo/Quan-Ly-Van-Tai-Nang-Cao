"""
Pagination Widget Module
Widget for page navigation with page size selection and jump to page functionality
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIntValidator
from typing import List


class PaginationWidget(QWidget):
    """
    Pagination widget for navigating through large datasets
    
    Features:
    - Page navigation (first, previous, next, last)
    - Page size selection
    - Total records display
    - Jump to page functionality
    - Current page indicator
    """
    
    # Signals
    pageChanged = pyqtSignal(int)  # Emitted when page changes (new page number)
    pageSizeChanged = pyqtSignal(int)  # Emitted when page size changes
    
    def __init__(self, 
                 page_sizes: List[int] = None,
                 default_page_size: int = 100,
                 parent=None):
        """
        Initialize pagination widget
        
        Args:
            page_sizes: List of available page sizes (default: [50, 100, 200, 500])
            default_page_size: Default page size
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._current_page = 1
        self._total_pages = 1
        self._total_records = 0
        self._page_size = default_page_size
        self._page_sizes = page_sizes or [50, 100, 200, 500]
        
        self._setup_ui()
        self._setup_connections()
        self._update_ui_state()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Total records label
        self.total_label = QLabel("Tổng: 0 bản ghi")
        main_layout.addWidget(self.total_label)
        
        main_layout.addStretch()
        
        # Page size selector
        self.page_size_label = QLabel("Hiển thị:")
        main_layout.addWidget(self.page_size_label)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.setMinimumWidth(80)
        for size in self._page_sizes:
            self.page_size_combo.addItem(f"{size} dòng", size)
        # Set default
        index = self.page_size_combo.findData(self._page_size)
        if index >= 0:
            self.page_size_combo.setCurrentIndex(index)
        main_layout.addWidget(self.page_size_combo)
        
        main_layout.addSpacing(20)
        
        # First page button
        self.first_button = QPushButton("<<")
        self.first_button.setFixedWidth(40)
        self.first_button.setToolTip("Trang đầu")
        main_layout.addWidget(self.first_button)
        
        # Previous page button
        self.prev_button = QPushButton("<")
        self.prev_button.setFixedWidth(40)
        self.prev_button.setToolTip("Trang trước")
        main_layout.addWidget(self.prev_button)
        
        # Page info label
        self.page_info_label = QLabel("Trang 1 / 1")
        self.page_info_label.setMinimumWidth(100)
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.page_info_label)
        
        # Next page button
        self.next_button = QPushButton(">")
        self.next_button.setFixedWidth(40)
        self.next_button.setToolTip("Trang sau")
        main_layout.addWidget(self.next_button)
        
        # Last page button
        self.last_button = QPushButton(">>")
        self.last_button.setFixedWidth(40)
        self.last_button.setToolTip("Trang cuối")
        main_layout.addWidget(self.last_button)
        
        main_layout.addSpacing(20)
        
        # Jump to page
        self.jump_label = QLabel("Đến trang:")
        main_layout.addWidget(self.jump_label)
        
        self.jump_spinbox = QSpinBox()
        self.jump_spinbox.setMinimum(1)
        self.jump_spinbox.setMaximum(1)
        self.jump_spinbox.setValue(1)
        self.jump_spinbox.setFixedWidth(80)
        main_layout.addWidget(self.jump_spinbox)
        
        self.jump_button = QPushButton("Đi")
        self.jump_button.setFixedWidth(50)
        main_layout.addWidget(self.jump_button)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Navigation buttons
        self.first_button.clicked.connect(self._on_first_clicked)
        self.prev_button.clicked.connect(self._on_prev_clicked)
        self.next_button.clicked.connect(self._on_next_clicked)
        self.last_button.clicked.connect(self._on_last_clicked)
        
        # Jump to page
        self.jump_button.clicked.connect(self._on_jump_clicked)
        self.jump_spinbox.returnPressed.connect(self._on_jump_clicked)
        
        # Page size change
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
    
    def _on_first_clicked(self):
        """Handle first page button click"""
        if self._current_page != 1:
            self.set_current_page(1)
    
    def _on_prev_clicked(self):
        """Handle previous page button click"""
        if self._current_page > 1:
            self.set_current_page(self._current_page - 1)
    
    def _on_next_clicked(self):
        """Handle next page button click"""
        if self._current_page < self._total_pages:
            self.set_current_page(self._current_page + 1)
    
    def _on_last_clicked(self):
        """Handle last page button click"""
        if self._current_page != self._total_pages:
            self.set_current_page(self._total_pages)
    
    def _on_jump_clicked(self):
        """Handle jump to page button click"""
        target_page = self.jump_spinbox.value()
        if target_page != self._current_page:
            self.set_current_page(target_page)
    
    def _on_page_size_changed(self, index: int):
        """Handle page size change"""
        if index >= 0:
            new_page_size = self.page_size_combo.itemData(index)
            if new_page_size != self._page_size:
                self._page_size = new_page_size
                # Reset to first page when page size changes
                self._current_page = 1
                self.pageSizeChanged.emit(new_page_size)
    
    def set_total_records(self, total: int):
        """
        Set total number of records
        
        Args:
            total: Total number of records
        """
        self._total_records = total
        
        # Calculate total pages
        if total > 0 and self._page_size > 0:
            self._total_pages = (total + self._page_size - 1) // self._page_size
        else:
            self._total_pages = 1
        
        # Ensure current page is valid
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages
        
        # Update jump spinbox max
        self.jump_spinbox.setMaximum(self._total_pages)
        
        # Update UI
        self._update_ui_state()
    
    def set_current_page(self, page: int):
        """
        Set current page
        
        Args:
            page: Page number (1-based)
        """
        if page < 1:
            page = 1
        elif page > self._total_pages:
            page = self._total_pages
        
        if page != self._current_page:
            self._current_page = page
            self.jump_spinbox.setValue(page)
            self._update_ui_state()
            self.pageChanged.emit(page)
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
    
    def get_page_size(self) -> int:
        """Get current page size"""
        return self._page_size
    
    def get_total_pages(self) -> int:
        """Get total number of pages"""
        return self._total_pages
    
    def get_total_records(self) -> int:
        """Get total number of records"""
        return self._total_records
    
    def _update_ui_state(self):
        """Update UI state based on current page and total pages"""
        # Update labels
        self.total_label.setText(f"Tổng: {self._total_records:,} bản ghi")
        self.page_info_label.setText(f"Trang {self._current_page} / {self._total_pages}")
        
        # Update button states
        self.first_button.setEnabled(self._current_page > 1)
        self.prev_button.setEnabled(self._current_page > 1)
        self.next_button.setEnabled(self._current_page < self._total_pages)
        self.last_button.setEnabled(self._current_page < self._total_pages)
        
        # Update jump controls
        self.jump_button.setEnabled(self._total_pages > 1)
        self.jump_spinbox.setEnabled(self._total_pages > 1)
    
    def reset(self):
        """Reset pagination to initial state"""
        self._current_page = 1
        self._total_pages = 1
        self._total_records = 0
        self.jump_spinbox.setValue(1)
        self.jump_spinbox.setMaximum(1)
        self._update_ui_state()
    
    def set_page_size(self, page_size: int):
        """
        Set page size programmatically
        
        Args:
            page_size: New page size
        """
        index = self.page_size_combo.findData(page_size)
        if index >= 0:
            self.page_size_combo.setCurrentIndex(index)
    
    def get_page_range(self) -> tuple[int, int]:
        """
        Get the range of records for current page
        
        Returns:
            Tuple of (start_index, end_index) (1-based)
        """
        if self._total_records == 0:
            return (0, 0)
        
        start = (self._current_page - 1) * self._page_size + 1
        end = min(start + self._page_size - 1, self._total_records)
        
        return (start, end)
    
    def get_page_info_text(self) -> str:
        """
        Get formatted page info text
        
        Returns:
            String like "Hiển thị 1-100 / 500 bản ghi"
        """
        if self._total_records == 0:
            return "Không có dữ liệu"
        
        start, end = self.get_page_range()
        return f"Hiển thị {start}-{end} / {self._total_records:,} bản ghi"
    
    def has_next_page(self) -> bool:
        """Check if there is a next page"""
        return self._current_page < self._total_pages
    
    def has_previous_page(self) -> bool:
        """Check if there is a previous page"""
        return self._current_page > 1
    
    def is_first_page(self) -> bool:
        """Check if current page is the first page"""
        return self._current_page == 1
    
    def is_last_page(self) -> bool:
        """Check if current page is the last page"""
        return self._current_page == self._total_pages
