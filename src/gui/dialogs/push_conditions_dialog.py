"""
Push Conditions Dialog - Dialog for configuring workflow push conditions
Provides condition builder UI with 12 operators, AND/OR logic, testing, and save/load
"""
import logging
from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QMessageBox, QComboBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialogButtonBox, QTextEdit,
    QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.push_conditions_service import PushConditionsService
from src.models.push_condition import PushCondition, ConditionOperator, LogicOperator

logger = logging.getLogger(__name__)


class PushConditionsDialog(QDialog):
    """
    Dialog for configuring push conditions for workflow automation.
    
    Features:
    - Condition builder UI
    - Support for 12 operators
    - AND/OR logic operator selection
    - Condition testing functionality
    - Save/load conditions
    """
    
    conditions_changed = pyqtSignal()
    
    def __init__(self, db_manager: EnhancedDatabaseManager, 
                 source_department_id: int, target_department_id: int, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.source_department_id = source_department_id
        self.target_department_id = target_department_id
        self.push_service = PushConditionsService(db_manager)
        self.conditions: List[PushCondition] = []
        
        self.setWindowTitle("Cấu Hình Điều Kiện Đẩy Dữ Liệu")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_conditions()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Department info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Từ Phòng Ban: {self.get_department_name(self.source_department_id)}"))
        info_layout.addWidget(QLabel("→"))
        info_layout.addWidget(QLabel(f"Đến Phòng Ban: {self.get_department_name(self.target_department_id)}"))
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Conditions section
        conditions_group = self._create_conditions_section()
        layout.addWidget(conditions_group)
        
        # Test section
        test_group = self._create_test_section()
        layout.addWidget(test_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Lưu Tất Cả")
        save_btn.clicked.connect(self.save_all_conditions)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_conditions_section(self):
        """Create the conditions list section"""
        group = QGroupBox("Danh Sách Điều Kiện")
        layout = QVBoxLayout(group)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("Thêm Điều Kiện")
        add_btn.clicked.connect(self.add_condition)
        toolbar.addWidget(add_btn)
        
        self.edit_btn = QPushButton("Sửa")
        self.edit_btn.clicked.connect(self.edit_condition)
        self.edit_btn.setEnabled(False)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_condition)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.conditions_table = QTableWidget()
        self.conditions_table.setColumnCount(5)
        self.conditions_table.setHorizontalHeaderLabels([
            "Thứ Tự", "Trường", "Toán Tử", "Giá Trị", "Logic"
        ])
        self.conditions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.conditions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.conditions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.conditions_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.conditions_table.cellDoubleClicked.connect(lambda: self.edit_condition())
        layout.addWidget(self.conditions_table)
        
        return group
    
    def _create_test_section(self):
        """Create the test section"""
        group = QGroupBox("Kiểm Tra Điều Kiện")
        layout = QVBoxLayout(group)
        
        layout.addWidget(QLabel("Nhập dữ liệu mẫu (JSON format):"))
        
        self.test_data_edit = QTextEdit()
        self.test_data_edit.setMaximumHeight(100)
        self.test_data_edit.setPlaceholderText('{"field_name": "value", "another_field": "value2"}')
        layout.addWidget(self.test_data_edit)
        
        test_layout = QHBoxLayout()
        test_btn = QPushButton("Kiểm Tra")
        test_btn.clicked.connect(self.test_conditions)
        test_layout.addWidget(test_btn)
        
        self.test_result_label = QLabel("Kết quả: ---")
        self.test_result_label.setStyleSheet("font-weight: bold;")
        test_layout.addWidget(self.test_result_label)
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        return group
    
    def get_department_name(self, department_id: int) -> str:
        """Get department name by ID"""
        try:
            query = "SELECT display_name FROM departments WHERE id = ?"
            results = self.db_manager.execute_query(query, (department_id,))
            if results:
                return results[0]['display_name']
            return f"Department {department_id}"
        except Exception as e:
            logger.error(f"Error getting department name: {e}")
            return f"Department {department_id}"
    
    def load_conditions(self):
        """Load conditions from database"""
        try:
            self.conditions = self.push_service.get_push_conditions(
                self.source_department_id,
                self.target_department_id
            )
            self.refresh_table()
        except Exception as e:
            logger.error(f"Error loading conditions: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải điều kiện: {str(e)}")
    
    def refresh_table(self):
        """Refresh the conditions table"""
        self.conditions_table.setRowCount(0)
        
        for condition in self.conditions:
            row = self.conditions_table.rowCount()
            self.conditions_table.insertRow(row)
            
            self.conditions_table.setItem(row, 0, QTableWidgetItem(str(condition.condition_order)))
            self.conditions_table.setItem(row, 1, QTableWidgetItem(condition.field_name))
            self.conditions_table.setItem(row, 2, QTableWidgetItem(self.get_operator_label(condition.operator)))
            self.conditions_table.setItem(row, 3, QTableWidgetItem(condition.value or ""))
            self.conditions_table.setItem(row, 4, QTableWidgetItem(condition.logic_operator))
            
            # Store condition ID
            self.conditions_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, condition.id)
    
    def get_operator_label(self, operator: str) -> str:
        """Get Vietnamese label for operator"""
        labels = {
            ConditionOperator.EQUALS: "Bằng",
            ConditionOperator.NOT_EQUALS: "Không bằng",
            ConditionOperator.CONTAINS: "Chứa",
            ConditionOperator.NOT_CONTAINS: "Không chứa",
            ConditionOperator.STARTS_WITH: "Bắt đầu với",
            ConditionOperator.ENDS_WITH: "Kết thúc với",
            ConditionOperator.GREATER_THAN: "Lớn hơn",
            ConditionOperator.LESS_THAN: "Nhỏ hơn",
            ConditionOperator.GREATER_OR_EQUAL: "Lớn hơn hoặc bằng",
            ConditionOperator.LESS_OR_EQUAL: "Nhỏ hơn hoặc bằng",
            ConditionOperator.IS_EMPTY: "Rỗng",
            ConditionOperator.IS_NOT_EMPTY: "Không rỗng"
        }
        return labels.get(operator, operator)
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.conditions_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_condition(self):
        """Add a new condition"""
        dialog = ConditionEditDialog(
            self.db_manager,
            self.source_department_id,
            self.target_department_id,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_conditions()
            self.conditions_changed.emit()
    
    def edit_condition(self):
        """Edit selected condition"""
        selected_row = self.conditions_table.currentRow()
        if selected_row < 0:
            return
        
        condition_id = self.conditions_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        condition = next((c for c in self.conditions if c.id == condition_id), None)
        
        if condition:
            dialog = ConditionEditDialog(
                self.db_manager,
                self.source_department_id,
                self.target_department_id,
                condition=condition,
                parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_conditions()
                self.conditions_changed.emit()
    
    def delete_condition(self):
        """Delete selected condition"""
        selected_row = self.conditions_table.currentRow()
        if selected_row < 0:
            return
        
        condition_id = self.conditions_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Xác Nhận Xóa",
            "Bạn có chắc muốn xóa điều kiện này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.push_service.delete_push_condition(condition_id)
                self.load_conditions()
                self.conditions_changed.emit()
                QMessageBox.information(self, "Thành Công", "Đã xóa điều kiện")
            except Exception as e:
                logger.error(f"Error deleting condition: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa điều kiện: {str(e)}")
    
    def test_conditions(self):
        """Test conditions with sample data"""
        try:
            import json
            
            test_data_str = self.test_data_edit.toPlainText().strip()
            if not test_data_str:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập dữ liệu mẫu")
                return
            
            test_data = json.loads(test_data_str)
            
            result = self.push_service.evaluate_conditions(self.conditions, test_data)
            
            if result:
                self.test_result_label.setText("Kết quả: ✓ Điều kiện thỏa mãn")
                self.test_result_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.test_result_label.setText("Kết quả: ✗ Điều kiện không thỏa mãn")
                self.test_result_label.setStyleSheet("color: red; font-weight: bold;")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Lỗi", "Dữ liệu JSON không hợp lệ")
        except Exception as e:
            logger.error(f"Error testing conditions: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể kiểm tra điều kiện: {str(e)}")
    
    def save_all_conditions(self):
        """Save all conditions"""
        try:
            # Conditions are saved individually when added/edited
            # This is just a confirmation
            QMessageBox.information(self, "Thành Công", "Tất cả điều kiện đã được lưu")
            self.conditions_changed.emit()
        except Exception as e:
            logger.error(f"Error saving conditions: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu điều kiện: {str(e)}")


class ConditionEditDialog(QDialog):
    """Dialog for adding/editing a single condition"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager,
                 source_department_id: int, target_department_id: int,
                 condition: Optional[PushCondition] = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.source_department_id = source_department_id
        self.target_department_id = target_department_id
        self.condition = condition
        self.is_edit_mode = condition is not None
        self.push_service = PushConditionsService(db_manager)
        
        self.setWindowTitle("Sửa Điều Kiện" if self.is_edit_mode else "Thêm Điều Kiện")
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_condition_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Field name
        layout.addWidget(QLabel("Trường:"))
        self.field_combo = QComboBox()
        self.load_available_fields()
        layout.addWidget(self.field_combo)
        
        # Operator
        layout.addWidget(QLabel("Toán Tử:"))
        self.operator_combo = QComboBox()
        self.populate_operators()
        self.operator_combo.currentIndexChanged.connect(self.on_operator_changed)
        layout.addWidget(self.operator_combo)
        
        # Value
        self.value_label = QLabel("Giá Trị:")
        layout.addWidget(self.value_label)
        self.value_edit = QLineEdit()
        layout.addWidget(self.value_edit)
        
        # Logic operator
        layout.addWidget(QLabel("Logic Operator:"))
        self.logic_combo = QComboBox()
        self.logic_combo.addItem("AND", LogicOperator.AND)
        self.logic_combo.addItem("OR", LogicOperator.OR)
        layout.addWidget(self.logic_combo)
        
        # Condition order
        layout.addWidget(QLabel("Thứ Tự:"))
        self.order_spin = QSpinBox()
        self.order_spin.setMinimum(0)
        self.order_spin.setMaximum(999)
        layout.addWidget(self.order_spin)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_condition)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.on_operator_changed()
    
    def load_available_fields(self):
        """Load available fields from department"""
        try:
            query = """
                SELECT field_name FROM field_configurations 
                WHERE department_id = ? AND is_active = 1
                ORDER BY field_name
            """
            results = self.db_manager.execute_query(query, (self.source_department_id,))
            
            self.field_combo.clear()
            for row in results:
                self.field_combo.addItem(row['field_name'])
        except Exception as e:
            logger.error(f"Error loading fields: {e}")
    
    def populate_operators(self):
        """Populate operator combo box"""
        operators = [
            (ConditionOperator.EQUALS, "Bằng"),
            (ConditionOperator.NOT_EQUALS, "Không bằng"),
            (ConditionOperator.CONTAINS, "Chứa"),
            (ConditionOperator.NOT_CONTAINS, "Không chứa"),
            (ConditionOperator.STARTS_WITH, "Bắt đầu với"),
            (ConditionOperator.ENDS_WITH, "Kết thúc với"),
            (ConditionOperator.GREATER_THAN, "Lớn hơn"),
            (ConditionOperator.LESS_THAN, "Nhỏ hơn"),
            (ConditionOperator.GREATER_OR_EQUAL, "Lớn hơn hoặc bằng"),
            (ConditionOperator.LESS_OR_EQUAL, "Nhỏ hơn hoặc bằng"),
            (ConditionOperator.IS_EMPTY, "Rỗng"),
            (ConditionOperator.IS_NOT_EMPTY, "Không rỗng")
        ]
        
        for op_value, op_label in operators:
            self.operator_combo.addItem(op_label, op_value)
    
    def on_operator_changed(self):
        """Handle operator change"""
        operator = self.operator_combo.currentData()
        
        # Hide value field for operators that don't need it
        no_value_operators = {
            ConditionOperator.IS_EMPTY,
            ConditionOperator.IS_NOT_EMPTY
        }
        
        needs_value = operator not in no_value_operators
        self.value_label.setVisible(needs_value)
        self.value_edit.setVisible(needs_value)
    
    def load_condition_data(self):
        """Load existing condition data"""
        if not self.condition:
            return
        
        # Set field
        index = self.field_combo.findText(self.condition.field_name)
        if index >= 0:
            self.field_combo.setCurrentIndex(index)
        
        # Set operator
        index = self.operator_combo.findData(self.condition.operator)
        if index >= 0:
            self.operator_combo.setCurrentIndex(index)
        
        # Set value
        self.value_edit.setText(self.condition.value or "")
        
        # Set logic operator
        index = self.logic_combo.findData(self.condition.logic_operator)
        if index >= 0:
            self.logic_combo.setCurrentIndex(index)
        
        # Set order
        self.order_spin.setValue(self.condition.condition_order)
    
    def save_condition(self):
        """Save the condition"""
        try:
            field_name = self.field_combo.currentText()
            if not field_name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn trường")
                return
            
            operator = self.operator_combo.currentData()
            value = self.value_edit.text().strip() if self.value_edit.isVisible() else None
            logic_operator = self.logic_combo.currentData()
            condition_order = self.order_spin.value()
            
            if self.is_edit_mode:
                # Update existing condition
                updates = {
                    'field_name': field_name,
                    'operator': operator,
                    'value': value,
                    'logic_operator': logic_operator,
                    'condition_order': condition_order
                }
                self.push_service.update_push_condition(self.condition.id, updates)
                QMessageBox.information(self, "Thành Công", "Đã cập nhật điều kiện")
            else:
                # Create new condition
                new_condition = PushCondition(
                    source_department_id=self.source_department_id,
                    target_department_id=self.target_department_id,
                    field_name=field_name,
                    operator=operator,
                    value=value,
                    logic_operator=logic_operator,
                    condition_order=condition_order,
                    is_active=True
                )
                
                # Validate
                errors = self.push_service.validate_condition(new_condition)
                if errors:
                    QMessageBox.warning(self, "Lỗi Validation", "\n".join(errors))
                    return
                
                self.push_service.create_push_condition(new_condition)
                QMessageBox.information(self, "Thành Công", "Đã thêm điều kiện mới")
            
            self.accept()
        except Exception as e:
            logger.error(f"Error saving condition: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu điều kiện: {str(e)}")
