"""
Suggestion Tab Widget Module
Tab widget for displaying filtered results and company price suggestions
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any, Optional

from src.services.trip_service import TripService
from src.services.company_price_service import CompanyPriceService
from src.models.trip import Trip
from src.models.company_price import CompanyPrice


class SuggestionTabWidget(QWidget):
    """
    Suggestion tab widget with 4 tabs:
    - Filtered results from trips
    - Company A prices
    - Company B prices
    - Company C prices
    
    Features:
    - Read-only tables
    - Click to fill form functionality
    - Synchronized filtering with input form
    """
    
    # Signals
    suggestionSelected = pyqtSignal(dict)  # Emitted when a suggestion is clicked
    
    def __init__(self, 
                 trip_service: TripService,
                 company_price_service: CompanyPriceService,
                 parent=None):
        """
        Initialize suggestion tab widget
        
        Args:
            trip_service: TripService instance
            company_price_service: CompanyPriceService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.trip_service = trip_service
        self.company_price_service = company_price_service
        self._current_filters = {}
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.filtered_tab = self._create_filtered_tab()
        self.company_a_tab = self._create_company_tab("Company A")
        self.company_b_tab = self._create_company_tab("Company B")
        self.company_c_tab = self._create_company_tab("Company C")
        
        # Add tabs
        self.tab_widget.addTab(self.filtered_tab, "Kết Quả Lọc")
        self.tab_widget.addTab(self.company_a_tab, "Công Ty A")
        self.tab_widget.addTab(self.company_b_tab, "Công Ty B")
        self.tab_widget.addTab(self.company_c_tab, "Công Ty C")
        
        main_layout.addWidget(self.tab_widget)
    
    def _create_filtered_tab(self) -> QWidget:
        """Create the filtered results tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Info label
        self.filtered_info_label = QLabel("0 kết quả")
        layout.addWidget(self.filtered_info_label)
        
        # Table
        self.filtered_table = QTableWidget()
        self._configure_filtered_table()
        layout.addWidget(self.filtered_table)
        
        return widget
    
    def _create_company_tab(self, company_name: str) -> QWidget:
        """Create a company price tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Info label
        info_label = QLabel("0 bảng giá")
        layout.addWidget(info_label)
        
        # Table
        table = QTableWidget()
        self._configure_company_table(table)
        layout.addWidget(table)
        
        # Store references
        if company_name == "Company A":
            self.company_a_info_label = info_label
            self.company_a_table = table
        elif company_name == "Company B":
            self.company_b_info_label = info_label
            self.company_b_table = table
        elif company_name == "Company C":
            self.company_c_info_label = info_label
            self.company_c_table = table
        
        return widget
    
    def _configure_filtered_table(self):
        """Configure the filtered results table"""
        columns = [
            "Mã Chuyến",
            "Khách Hàng",
            "Điểm Đi",
            "Điểm Đến",
            "Giá Cả",
            "Khoán Lương",
            "Chi Phí Khác"
        ]
        
        self.filtered_table.setColumnCount(len(columns))
        self.filtered_table.setHorizontalHeaderLabels(columns)
        
        # Set properties
        self.filtered_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.filtered_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.filtered_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.filtered_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.filtered_table.setColumnWidth(0, 100)  # Mã Chuyến
        self.filtered_table.setColumnWidth(1, 200)  # Khách Hàng
        self.filtered_table.setColumnWidth(2, 150)  # Điểm Đi
        self.filtered_table.setColumnWidth(3, 150)  # Điểm Đến
        self.filtered_table.setColumnWidth(4, 120)  # Giá Cả
        self.filtered_table.setColumnWidth(5, 120)  # Khoán Lương
        self.filtered_table.setColumnWidth(6, 120)  # Chi Phí Khác
        
        # Stretch last column
        self.filtered_table.horizontalHeader().setStretchLastSection(True)
    
    def _configure_company_table(self, table: QTableWidget):
        """Configure a company price table"""
        columns = [
            "Khách Hàng",
            "Điểm Đi",
            "Điểm Đến",
            "Giá Cả",
            "Khoán Lương"
        ]
        
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # Set properties
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        
        # Set column widths
        table.setColumnWidth(0, 200)  # Khách Hàng
        table.setColumnWidth(1, 150)  # Điểm Đi
        table.setColumnWidth(2, 150)  # Điểm Đến
        table.setColumnWidth(3, 120)  # Giá Cả
        table.setColumnWidth(4, 120)  # Khoán Lương
        
        # Stretch last column
        table.horizontalHeader().setStretchLastSection(True)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Connect table click events
        self.filtered_table.cellClicked.connect(
            lambda row, col: self._on_filtered_row_clicked(row)
        )
        self.company_a_table.cellClicked.connect(
            lambda row, col: self._on_company_row_clicked(row, "Company A")
        )
        self.company_b_table.cellClicked.connect(
            lambda row, col: self._on_company_row_clicked(row, "Company B")
        )
        self.company_c_table.cellClicked.connect(
            lambda row, col: self._on_company_row_clicked(row, "Company C")
        )
    
    def _on_filtered_row_clicked(self, row: int):
        """Handle click on filtered results row"""
        data = self._get_filtered_row_data(row)
        if data:
            self.suggestionSelected.emit(data)
    
    def _on_company_row_clicked(self, row: int, company_name: str):
        """Handle click on company price row"""
        data = self._get_company_row_data(row, company_name)
        if data:
            self.suggestionSelected.emit(data)
    
    def _get_filtered_row_data(self, row: int) -> Optional[Dict[str, Any]]:
        """Get data from filtered results row"""
        if row < 0 or row >= self.filtered_table.rowCount():
            return None
        
        return {
            'ma_chuyen': self._get_cell_text(self.filtered_table, row, 0),
            'khach_hang': self._get_cell_text(self.filtered_table, row, 1),
            'diem_di': self._get_cell_text(self.filtered_table, row, 2),
            'diem_den': self._get_cell_text(self.filtered_table, row, 3),
            'gia_ca': self._parse_int(self._get_cell_text(self.filtered_table, row, 4)),
            'khoan_luong': self._parse_int(self._get_cell_text(self.filtered_table, row, 5)),
            'chi_phi_khac': self._parse_int(self._get_cell_text(self.filtered_table, row, 6)),
        }
    
    def _get_company_row_data(self, row: int, company_name: str) -> Optional[Dict[str, Any]]:
        """Get data from company price row"""
        table = self._get_company_table(company_name)
        if not table or row < 0 or row >= table.rowCount():
            return None
        
        return {
            'khach_hang': self._get_cell_text(table, row, 0),
            'diem_di': self._get_cell_text(table, row, 1),
            'diem_den': self._get_cell_text(table, row, 2),
            'gia_ca': self._parse_int(self._get_cell_text(table, row, 3)),
            'khoan_luong': self._parse_int(self._get_cell_text(table, row, 4)),
        }
    
    def _get_company_table(self, company_name: str) -> Optional[QTableWidget]:
        """Get table widget for company"""
        if company_name == "Company A":
            return self.company_a_table
        elif company_name == "Company B":
            return self.company_b_table
        elif company_name == "Company C":
            return self.company_c_table
        return None
    
    def _get_cell_text(self, table: QTableWidget, row: int, col: int) -> str:
        """Get text from table cell"""
        item = table.item(row, col)
        return item.text() if item else ""
    
    def _parse_int(self, value: str) -> int:
        """Parse integer from string, return 0 if invalid"""
        try:
            # Remove thousand separators
            value = value.replace(",", "").replace(".", "")
            return int(value)
        except (ValueError, AttributeError):
            return 0
    
    def update_filtered_results(self, filters: Dict[str, Any]):
        """
        Update filtered results based on filters
        
        Args:
            filters: Dictionary of filter criteria
        """
        self._current_filters = filters
        
        try:
            # Search trips with filters
            result = self.trip_service.search_trips(filters, page=1, page_size=100)
            trips = result['trips']
            
            # Update table
            self._populate_filtered_table(trips)
            
            # Update info label
            self.filtered_info_label.setText(f"{len(trips)} kết quả")
            
            # Also update company tabs with same filters
            self._update_company_tabs(filters)
            
        except Exception as e:
            self.filtered_info_label.setText(f"Lỗi: {str(e)}")
    
    def _populate_filtered_table(self, trips: List[Trip]):
        """Populate filtered results table"""
        self.filtered_table.setRowCount(0)
        
        for trip in trips:
            row = self.filtered_table.rowCount()
            self.filtered_table.insertRow(row)
            
            self.filtered_table.setItem(row, 0, QTableWidgetItem(trip.ma_chuyen))
            self.filtered_table.setItem(row, 1, QTableWidgetItem(trip.khach_hang))
            self.filtered_table.setItem(row, 2, QTableWidgetItem(trip.diem_di or ""))
            self.filtered_table.setItem(row, 3, QTableWidgetItem(trip.diem_den or ""))
            self.filtered_table.setItem(row, 4, QTableWidgetItem(f"{trip.gia_ca:,}"))
            self.filtered_table.setItem(row, 5, QTableWidgetItem(f"{trip.khoan_luong:,}"))
            self.filtered_table.setItem(row, 6, QTableWidgetItem(f"{trip.chi_phi_khac:,}"))
    
    def _update_company_tabs(self, filters: Dict[str, Any]):
        """Update all company tabs with filters"""
        # Extract relevant filters for company prices
        company_filters = {}
        if 'khach_hang' in filters:
            company_filters['khach_hang'] = filters['khach_hang']
        if 'diem_di' in filters:
            company_filters['diem_di'] = filters['diem_di']
        if 'diem_den' in filters:
            company_filters['diem_den'] = filters['diem_den']
        
        # Update each company tab
        self.update_company_prices("Company A", company_filters)
        self.update_company_prices("Company B", company_filters)
        self.update_company_prices("Company C", company_filters)
    
    def update_company_prices(self, company_name: str, filters: Optional[Dict[str, Any]] = None):
        """
        Update company price tab
        
        Args:
            company_name: Name of the company
            filters: Optional filter criteria
        """
        try:
            # Get prices
            prices = self.company_price_service.get_company_prices(
                company_name,
                filters,
                use_cache=True
            )
            
            # Get table and info label
            table = self._get_company_table(company_name)
            info_label = self._get_company_info_label(company_name)
            
            if not table or not info_label:
                return
            
            # Populate table
            self._populate_company_table(table, prices)
            
            # Update info label
            info_label.setText(f"{len(prices)} bảng giá")
            
        except Exception as e:
            info_label = self._get_company_info_label(company_name)
            if info_label:
                info_label.setText(f"Lỗi: {str(e)}")
    
    def _get_company_info_label(self, company_name: str) -> Optional[QLabel]:
        """Get info label for company"""
        if company_name == "Company A":
            return self.company_a_info_label
        elif company_name == "Company B":
            return self.company_b_info_label
        elif company_name == "Company C":
            return self.company_c_info_label
        return None
    
    def _populate_company_table(self, table: QTableWidget, prices: List[CompanyPrice]):
        """Populate company price table"""
        table.setRowCount(0)
        
        for price in prices:
            row = table.rowCount()
            table.insertRow(row)
            
            table.setItem(row, 0, QTableWidgetItem(price.khach_hang))
            table.setItem(row, 1, QTableWidgetItem(price.diem_di))
            table.setItem(row, 2, QTableWidgetItem(price.diem_den))
            table.setItem(row, 3, QTableWidgetItem(f"{price.gia_ca:,}"))
            table.setItem(row, 4, QTableWidgetItem(f"{price.khoan_luong:,}"))
    
    def load_all_company_prices(self):
        """Load all company prices without filters"""
        self.update_company_prices("Company A")
        self.update_company_prices("Company B")
        self.update_company_prices("Company C")
    
    def clear_all_tabs(self):
        """Clear all tabs"""
        self.filtered_table.setRowCount(0)
        self.company_a_table.setRowCount(0)
        self.company_b_table.setRowCount(0)
        self.company_c_table.setRowCount(0)
        
        self.filtered_info_label.setText("0 kết quả")
        self.company_a_info_label.setText("0 bảng giá")
        self.company_b_info_label.setText("0 bảng giá")
        self.company_c_info_label.setText("0 bảng giá")
    
    def get_current_tab_index(self) -> int:
        """Get current tab index"""
        return self.tab_widget.currentIndex()
    
    def set_current_tab_index(self, index: int):
        """Set current tab index"""
        self.tab_widget.setCurrentIndex(index)
