"""
Workflow History Dialog - Dialog for viewing workflow execution history
Provides filtering by date range, department, status, export to Excel, and detail view
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QComboBox, QDateEdit, QTextEdit, QSplitter,
    QFileDialog
)
from PyQt6.QtCore import Qt, QDate

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.workflow_history import WorkflowHistory, WorkflowStatus

logger = logging.getLogger(__name__)


class WorkflowHistoryDialog(QDialog):
    """
    Dialog for viewing workflow execution history.
    
    Features:
    - Filtering by date range, department, status
    - Export history to Excel
    - Detail view for each workflow entry
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.history_entries: List[WorkflowHistory] = []
        
        self.setWindowTitle("Lịch Sử Workflow")
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        self.load_departments()
        self.load_history()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Filters section
        filters_group = self._create_filters_section()
        layout.addWidget(filters_group)
        
        # Create splitter for table and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top - History table
        table_widget = self._create_table_section()
        splitter.addWidget(table_widget)
        
        # Bottom - Details
        details_widget = self._create_details_section()
        splitter.addWidget(details_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Xuất Excel")
        export_btn.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("Làm Mới")
        refresh_btn.clicked.connect(self.load_history)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_filters_section(self):
        """Create the filters section"""
        group = QGroupBox("Bộ Lọc")
        layout = QHBoxLayout(group)
        
        # Date range
        layout.addWidget(QLabel("Từ ngày:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        layout.addWidget(self.from_date)
        
        layout.addWidget(QLabel("Đến ngày:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        layout.addWidget(self.to_date)
        
        # Department filter
        layout.addWidget(QLabel("Phòng ban:"))
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tất cả", None)
        layout.addWidget(self.department_combo)
        
        # Status filter
        layout.addWidget(QLabel("Trạng thái:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả", None)
        self.status_combo.addItem("Thành công", WorkflowStatus.SUCCESS)
        self.status_combo.addItem("Thất bại", WorkflowStatus.FAILED)
        self.status_combo.addItem("Đang chờ", WorkflowStatus.PENDING)
        self.status_combo.addItem("Đã hủy", WorkflowStatus.CANCELLED)
        layout.addWidget(self.status_combo)
        
        # Apply button
        apply_btn = QPushButton("Áp Dụng")
        apply_btn.clicked.connect(self.load_history)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        return group
    
    def _create_table_section(self):
        """Create the history table section"""
        widget = QGroupBox("Lịch Sử")
        layout = QVBoxLayout(widget)
        
        # Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Record ID", "Từ Phòng Ban", "Đến Phòng Ban", 
            "Người Thực Hiện", "Trạng Thái", "Thời Gian"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.history_table)
        
        # Count label
        self.count_label = QLabel("Tổng: 0 bản ghi")
        layout.addWidget(self.count_label)
        
        return widget
    
    def _create_details_section(self):
        """Create the details section"""
        widget = QGroupBox("Chi Tiết")
        layout = QVBoxLayout(widget)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        return widget
    
    def load_departments(self):
        """Load departments for filter"""
        try:
            query = "SELECT id, display_name FROM departments ORDER BY display_name"
            results = self.db_manager.execute_query(query)
            
            for row in results:
                self.department_combo.addItem(row['display_name'], row['id'])
        except Exception as e:
            logger.error(f"Error loading departments: {e}")
    
    def load_history(self):
        """Load workflow history with filters"""
        try:
            # Build query with filters
            query = "SELECT * FROM workflow_history WHERE 1=1"
            params = []
            
            # Date range filter
            from_date = self.from_date.date().toPyDate()
            to_date = self.to_date.date().toPyDate()
            query += " AND DATE(created_at) BETWEEN ? AND ?"
            params.extend([from_date.isoformat(), to_date.isoformat()])
            
            # Department filter
            department_id = self.department_combo.currentData()
            if department_id:
                query += " AND (source_department_id = ? OR target_department_id = ?)"
                params.extend([department_id, department_id])
            
            # Status filter
            status = self.status_combo.currentData()
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            results = self.db_manager.execute_query(query, tuple(params))
            
            self.history_entries = [WorkflowHistory(**row) for row in results]
            self.refresh_table()
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải lịch sử: {str(e)}")
    
    def refresh_table(self):
        """Refresh the history table"""
        self.history_table.setRowCount(0)
        
        for entry in self.history_entries:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(entry.record_id)))
            self.history_table.setItem(row, 2, QTableWidgetItem(
                self.get_department_name(entry.source_department_id)
            ))
            self.history_table.setItem(row, 3, QTableWidgetItem(
                self.get_department_name(entry.target_department_id)
            ))
            self.history_table.setItem(row, 4, QTableWidgetItem(
                self.get_employee_name(entry.pushed_by) if entry.pushed_by else "System"
            ))
            
            # Status with color
            status_item = QTableWidgetItem(self.get_status_label(entry.status))
            if entry.status == WorkflowStatus.SUCCESS:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif entry.status == WorkflowStatus.FAILED:
                status_item.setForeground(Qt.GlobalColor.red)
            self.history_table.setItem(row, 5, status_item)
            
            self.history_table.setItem(row, 6, QTableWidgetItem(
                entry.created_at.strftime("%Y-%m-%d %H:%M:%S") if entry.created_at else ""
            ))
            
            # Store entry ID
            self.history_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, entry.id)
        
        self.count_label.setText(f"Tổng: {len(self.history_entries)} bản ghi")
    
    def get_department_name(self, department_id: int) -> str:
        """Get department name by ID"""
        try:
            query = "SELECT display_name FROM departments WHERE id = ?"
            results = self.db_manager.execute_query(query, (department_id,))
            if results:
                return results[0]['display_name']
            return f"Dept {department_id}"
        except Exception as e:
            logger.error(f"Error getting department name: {e}")
            return f"Dept {department_id}"
    
    def get_employee_name(self, employee_id: Optional[int]) -> str:
        """Get employee name by ID"""
        if not employee_id:
            return "N/A"
        
        try:
            query = "SELECT full_name FROM employees WHERE id = ?"
            results = self.db_manager.execute_query(query, (employee_id,))
            if results:
                return results[0]['full_name']
            return f"Employee {employee_id}"
        except Exception as e:
            logger.error(f"Error getting employee name: {e}")
            return f"Employee {employee_id}"
    
    def get_status_label(self, status: str) -> str:
        """Get Vietnamese label for status"""
        labels = {
            WorkflowStatus.SUCCESS: "Thành công",
            WorkflowStatus.FAILED: "Thất bại",
            WorkflowStatus.PENDING: "Đang chờ",
            WorkflowStatus.CANCELLED: "Đã hủy"
        }
        return labels.get(status, status)
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            self.update_details()
    
    def update_details(self):
        """Update the details pane"""
        selected_row = self.history_table.currentRow()
        if selected_row < 0:
            self.details_text.clear()
            return
        
        entry_id = self.history_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        entry = next((e for e in self.history_entries if e.id == entry_id), None)
        
        if entry:
            details = f"""
<h3>Chi Tiết Workflow #{entry.id}</h3>

<p><b>Record ID:</b> {entry.record_id}</p>
<p><b>Từ Phòng Ban:</b> {self.get_department_name(entry.source_department_id)}</p>
<p><b>Đến Phòng Ban:</b> {self.get_department_name(entry.target_department_id)}</p>
<p><b>Người Thực Hiện:</b> {self.get_employee_name(entry.pushed_by) if entry.pushed_by else 'System'}</p>
<p><b>Trạng Thái:</b> {self.get_status_label(entry.status)}</p>
<p><b>Thời Gian:</b> {entry.created_at.strftime("%Y-%m-%d %H:%M:%S") if entry.created_at else 'N/A'}</p>
"""
            
            if entry.error_message:
                details += f"""
<p><b>Thông Báo Lỗi:</b></p>
<pre style="background-color: #ffeeee; padding: 10px; border-radius: 5px;">{entry.error_message}</pre>
"""
            
            self.details_text.setHtml(details)
    
    def export_to_excel(self):
        """Export history to Excel file"""
        if not self.history_entries:
            QMessageBox.warning(self, "Lỗi", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất Lịch Sử",
            f"workflow_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                import pandas as pd
                
                # Prepare data
                data = []
                for entry in self.history_entries:
                    data.append({
                        'ID': entry.id,
                        'Record ID': entry.record_id,
                        'Từ Phòng Ban': self.get_department_name(entry.source_department_id),
                        'Đến Phòng Ban': self.get_department_name(entry.target_department_id),
                        'Người Thực Hiện': self.get_employee_name(entry.pushed_by) if entry.pushed_by else 'System',
                        'Trạng Thái': self.get_status_label(entry.status),
                        'Thời Gian': entry.created_at.strftime("%Y-%m-%d %H:%M:%S") if entry.created_at else '',
                        'Thông Báo Lỗi': entry.error_message or ''
                    })
                
                # Create DataFrame and export
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False, engine='openpyxl')
                
                QMessageBox.information(self, "Thành Công", f"Đã xuất {len(data)} bản ghi")
            except ImportError:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    "Cần cài đặt pandas và openpyxl để xuất Excel"
                )
            except Exception as e:
                logger.error(f"Error exporting to Excel: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xuất Excel: {str(e)}")
