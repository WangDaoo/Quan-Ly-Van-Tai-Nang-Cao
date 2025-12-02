"""
Main Table Widget Module
Table widget for displaying and editing trip data with Excel-like features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor
from typing import List, Dict, Any, Optional

from src.services.trip_service import TripService
from src.models.trip import Trip
from .excel_like_table import ExcelLikeTable


class MainTableWidget(QWidget):
    """
    Main table widget for displaying trip data
    Integrates ExcelLikeTable with trip-specific functionality
    
    Features:
    - Data loading from database
    - Auto-save on edit
    - Row selection and multi-select
    - Alternating row colors
    - Integration with TripService
    """
    
    # Signals
    rowSelected = pyqtSignal(dict)  # Emitted when a row is selected
    rowsSelected = pyqtSignal(list)  # Emitted when multiple rows are selected
    dataChanged = pyqtSignal(int, dict)  # Emitted when data is changed (trip_id, data)
    dataLoaded = pyqtSignal(int)  # Emitted when data is loaded (row count)
    tripDeleted = pyqtSignal(int)  # Emitted when trip is deleted (trip_id)
    
    def __init__(self, trip_service: TripService, parent=None):
        """
        Initialize main table widget
        
        Args:
            trip_service: TripService instance for database operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.trip_service = trip_service
        self._current_page = 1
        self._page_size = 100
        self._total_records = 0
        self._trip_data = []  # Store trip data for reference
        
        # Debouncing for auto-save
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)  # 500ms debounce
        self._save_timer.timeout.connect(self._perform_save)
        self._pending_save_data = None
        
        self._setup_ui()
        self._setup_connections()
        self._configure_table()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Header with title and info
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Danh Sách Chuyến Xe")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.info_label = QLabel("0 chuyến")
        header_layout.addWidget(self.info_label)
        
        main_layout.addLayout(header_layout)
        
        # Excel-like table
        self.table = ExcelLikeTable()
        main_layout.addWidget(self.table)
    
    def _configure_table(self):
        """Configure table properties"""
        # Define columns for trip data
        columns = [
            "ID",
            "Mã Chuyến",
            "Khách Hàng",
            "Điểm Đi",
            "Điểm Đến",
            "Giá Cả",
            "Khoán Lương",
            "Chi Phí Khác",
            "Ghi Chú",
            "Ngày Tạo"
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.ExtendedSelection)
        
        # Hide ID column (but keep it for reference)
        self.table.setColumnHidden(0, True)
        
        # Set column widths
        self.table.setColumnWidth(1, 100)  # Mã Chuyến
        self.table.setColumnWidth(2, 200)  # Khách Hàng
        self.table.setColumnWidth(3, 150)  # Điểm Đi
        self.table.setColumnWidth(4, 150)  # Điểm Đến
        self.table.setColumnWidth(5, 120)  # Giá Cả
        self.table.setColumnWidth(6, 120)  # Khoán Lương
        self.table.setColumnWidth(7, 120)  # Chi Phí Khác
        self.table.setColumnWidth(8, 200)  # Ghi Chú
        self.table.setColumnWidth(9, 150)  # Ngày Tạo
        
        # Make Mã Chuyến column read-only (it's auto-generated)
        # This will be handled in cell change event
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Connect table signals
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        # Note: Row deletion is handled through context menu in ExcelLikeTable
    
    def _on_cell_changed(self, row: int, column: int):
        """
        Handle cell change with auto-save and debouncing
        
        Implements:
        - Auto-save with debouncing (Requirement 1.4)
        - Validation on edit (Requirement 1.5)
        - Error handling for failed updates (Requirement 1.5)
        """
        # Don't save if we're loading data
        if self.table.signalsBlocked():
            return
        
        # Don't allow editing ID, Mã Chuyến, or Ngày Tạo columns
        if column in [0, 1, 9]:
            return
        
        # Get trip ID from hidden column
        trip_id_item = self.table.item(row, 0)
        if not trip_id_item:
            return
        
        try:
            trip_id = int(trip_id_item.text())
        except ValueError:
            return
        
        # Get updated data from row
        updated_data = self._get_row_data(row)
        
        # Validate required fields
        if not updated_data.get('khach_hang'):
            QMessageBox.warning(
                self,
                "Lỗi Validation",
                "Khách hàng là trường bắt buộc"
            )
            self.load_data()  # Reload to revert
            return
        
        if not updated_data.get('gia_ca') or updated_data.get('gia_ca') == 0:
            QMessageBox.warning(
                self,
                "Lỗi Validation",
                "Giá cả là trường bắt buộc và phải lớn hơn 0"
            )
            self.load_data()  # Reload to revert
            return
        
        # Remove ID and ma_chuyen from update data
        updated_data.pop('id', None)
        updated_data.pop('ma_chuyen', None)
        
        # Store pending save data
        self._pending_save_data = (trip_id, updated_data)
        
        # Restart debounce timer
        self._save_timer.stop()
        self._save_timer.start()
    
    def _perform_save(self):
        """Perform the actual save operation after debounce"""
        if not self._pending_save_data:
            return
        
        trip_id, updated_data = self._pending_save_data
        self._pending_save_data = None
        
        try:
            # Update in database
            updated_trip = self.trip_service.update_trip(trip_id, updated_data)
            
            # Emit signal
            self.dataChanged.emit(trip_id, updated_trip.model_dump())
            
            # Show brief success message in status bar (if parent has one)
            parent = self.parent()
            while parent:
                if hasattr(parent, 'statusBar'):
                    parent.statusBar().showMessage(
                        f"✓ Đã lưu thay đổi cho chuyến {updated_trip.ma_chuyen}",
                        2000
                    )
                    break
                parent = parent.parent()
            
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Lỗi Validation",
                f"Không thể lưu thay đổi: {str(e)}"
            )
            # Reload data to revert changes
            self.load_data()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi Lưu Dữ Liệu",
                f"Không thể lưu thay đổi: {str(e)}"
            )
            # Reload data to revert changes
            self.load_data()
    
    def _on_selection_changed(self):
        """Handle selection change"""
        selected_rows = self.table.get_selected_rows()
        
        if len(selected_rows) == 1:
            # Single selection
            row_data = self._get_row_data(selected_rows[0])
            self.rowSelected.emit(row_data)
        elif len(selected_rows) > 1:
            # Multiple selection
            rows_data = [self._get_row_data(row) for row in selected_rows]
            self.rowsSelected.emit(rows_data)
    
    def _on_row_deleted(self, rows: List[int]):
        """Handle row deletion"""
        if not rows:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Xác Nhận Xóa",
            f"Bạn có chắc muốn xóa {len(rows)} chuyến đã chọn?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete trips
        deleted_count = 0
        for row in sorted(rows, reverse=True):  # Delete from bottom to top
            trip_id_item = self.table.item(row, 0)
            if trip_id_item:
                try:
                    trip_id = int(trip_id_item.text())
                    self.trip_service.delete_trip(trip_id)
                    self.tripDeleted.emit(trip_id)
                    deleted_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Lỗi Xóa",
                        f"Không thể xóa chuyến: {str(e)}"
                    )
        
        # Reload data
        if deleted_count > 0:
            self.load_data()
            QMessageBox.information(
                self,
                "Thành Công",
                f"Đã xóa {deleted_count} chuyến"
            )
    
    def load_data(self, page: int = 1, page_size: int = 100):
        """
        Load trip data from database
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
        """
        try:
            # Get data from service
            result = self.trip_service.get_all_trips(page=page, page_size=page_size)
            
            trips = result['trips']
            self._total_records = result['total']
            self._current_page = page
            self._page_size = page_size
            self._trip_data = trips
            
            # Block signals while loading
            self.table.blockSignals(True)
            
            # Clear table
            self.table.setRowCount(0)
            
            # Populate table
            for trip in trips:
                self._add_trip_row(trip)
            
            # Unblock signals
            self.table.blockSignals(False)
            
            # Update info label
            self._update_info_label()
            
            # Emit signal
            self.dataLoaded.emit(len(trips))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi Tải Dữ Liệu",
                f"Không thể tải dữ liệu: {str(e)}"
            )
    
    def _add_trip_row(self, trip: Trip):
        """Add a trip as a new row"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Format date
        created_at = ""
        if trip.created_at:
            if isinstance(trip.created_at, str):
                created_at = trip.created_at.split('.')[0]  # Remove microseconds
            else:
                created_at = trip.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # Set cell values
        self.table.set_cell_value(row, 0, str(trip.id))  # Hidden ID
        self.table.set_cell_value(row, 1, trip.ma_chuyen)
        self.table.set_cell_value(row, 2, trip.khach_hang)
        self.table.set_cell_value(row, 3, trip.diem_di or "")
        self.table.set_cell_value(row, 4, trip.diem_den or "")
        self.table.set_cell_value(row, 5, str(trip.gia_ca))
        self.table.set_cell_value(row, 6, str(trip.khoan_luong))
        self.table.set_cell_value(row, 7, str(trip.chi_phi_khac))
        self.table.set_cell_value(row, 8, trip.ghi_chu or "")
        self.table.set_cell_value(row, 9, created_at)
        
        # Make ID and Mã Chuyến read-only
        id_item = self.table.item(row, 0)
        ma_chuyen_item = self.table.item(row, 1)
        created_at_item = self.table.item(row, 9)
        
        if id_item:
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if ma_chuyen_item:
            ma_chuyen_item.setFlags(ma_chuyen_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if created_at_item:
            created_at_item.setFlags(created_at_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    
    def _get_row_data(self, row: int) -> Dict[str, Any]:
        """Get data from a row as dictionary"""
        return {
            'id': int(self.table.get_cell_value(row, 0)) if self.table.get_cell_value(row, 0) else None,
            'ma_chuyen': self.table.get_cell_value(row, 1),
            'khach_hang': self.table.get_cell_value(row, 2),
            'diem_di': self.table.get_cell_value(row, 3),
            'diem_den': self.table.get_cell_value(row, 4),
            'gia_ca': int(self.table.get_cell_value(row, 5)) if self.table.get_cell_value(row, 5) else 0,
            'khoan_luong': int(self.table.get_cell_value(row, 6)) if self.table.get_cell_value(row, 6) else 0,
            'chi_phi_khac': int(self.table.get_cell_value(row, 7)) if self.table.get_cell_value(row, 7) else 0,
            'ghi_chu': self.table.get_cell_value(row, 8),
        }
    
    def _update_info_label(self):
        """Update the info label with record count"""
        if self._total_records == 0:
            self.info_label.setText("0 chuyến")
        else:
            start = (self._current_page - 1) * self._page_size + 1
            end = min(start + len(self._trip_data) - 1, self._total_records)
            self.info_label.setText(
                f"Hiển thị {start}-{end} / {self._total_records} chuyến"
            )
    
    def refresh_data(self):
        """Refresh the current page data"""
        self.load_data(self._current_page, self._page_size)
    
    def get_selected_trip_data(self) -> Optional[Dict[str, Any]]:
        """Get data from the selected row"""
        selected_rows = self.table.get_selected_rows()
        if len(selected_rows) == 1:
            return self._get_row_data(selected_rows[0])
        return None
    
    def get_selected_trips_data(self) -> List[Dict[str, Any]]:
        """Get data from all selected rows"""
        selected_rows = self.table.get_selected_rows()
        return [self._get_row_data(row) for row in selected_rows]
    
    def clear_selection(self):
        """Clear row selection"""
        self.table.clearSelection()
    
    def select_row_by_trip_id(self, trip_id: int):
        """
        Select a row by trip ID
        
        Args:
            trip_id: Trip ID to select
        """
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item and int(id_item.text()) == trip_id:
                self.table.selectRow(row)
                break
    
    def get_table(self) -> ExcelLikeTable:
        """Get the underlying ExcelLikeTable widget"""
        return self.table
    
    def set_page_size(self, page_size: int):
        """Set the page size and reload data"""
        self._page_size = page_size
        self.load_data(1, page_size)
    
    def get_total_records(self) -> int:
        """Get total number of records"""
        return self._total_records
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
    
    def get_page_size(self) -> int:
        """Get page size"""
        return self._page_size

    def get_total_records(self) -> int:
        """Get total number of records"""
        return self._total_records
    
    def get_page_size(self) -> int:
        """Get current page size"""
        return self._page_size
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
    
    def set_page_size(self, page_size: int):
        """Set page size"""
        self._page_size = page_size
        self.load_data(page=1)
    
    def get_all_trips(self) -> List[Trip]:
        """Get all trips from database"""
        try:
            trip_data_list = self.trip_service.get_all_trips()
            return [Trip(**trip_data) for trip_data in trip_data_list]
        except Exception as e:
            print(f"Error getting all trips: {e}")
            return []
    
    def get_filtered_trips(self) -> List[Trip]:
        """Get filtered trips (currently displayed trips)"""
        return [Trip(**trip_data) for trip_data in self._trip_data]
    
    def get_selected_trips(self) -> List[Trip]:
        """Get selected trips"""
        selected_rows = self.table.get_selected_rows()
        selected_trips = []
        
        for row in selected_rows:
            if row < len(self._trip_data):
                trip_data = self._trip_data[row]
                selected_trips.append(Trip(**trip_data))
        
        return selected_trips
