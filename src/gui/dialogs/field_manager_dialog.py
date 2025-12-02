"""
Field Manager Dialog - Dialog for managing field configurations
Provides add/edit/delete functionality, drag & drop reordering, preview, and export/import
"""
import json
import logging
from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QLabel,
    QComboBox, QLineEdit, QCheckBox, QTextEdit, QSpinBox, QGroupBox,
    QFormLayout, QDialogButtonBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from src.services.field_config_service import FieldConfigService
from src.models.field_configuration import FieldConfiguration, FieldType, WidgetType

logger = logging.getLogger(__name__)


class FieldManagerDialog(QDialog):
    """
    Dialog for managing field configurations with full CRUD operations.
    
    Features:
    - Add/Edit/Delete field configurations
    - Drag & drop reordering
    - Field preview
    - Export/Import field configs to/from JSON
    """
    
    fields_changed = pyqtSignal()
    
    def __init__(self, field_config_service: FieldConfigService, department_id: int, parent=None):
        super().__init__(parent)
        self.field_config_service = field_config_service
        self.department_id = department_id
        self.current_configs: List[FieldConfiguration] = []
        
        self.setWindowTitle("Quản Lý Cấu Hình Trường")
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        self.load_field_configs()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Field list
        left_widget = self._create_field_list_section()
        splitter.addWidget(left_widget)
        
        # Right side - Preview and edit
        right_widget = self._create_preview_section()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)
    
    def _create_field_list_section(self):
        """Create the field list section with table"""
        widget = QGroupBox("Danh Sách Trường")
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.add_btn = QPushButton("Thêm Trường")
        self.add_btn.clicked.connect(self.add_field)
        toolbar.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Sửa")
        self.edit_btn.clicked.connect(self.edit_field)
        self.edit_btn.setEnabled(False)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_field)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        self.duplicate_btn = QPushButton("Nhân Bản")
        self.duplicate_btn.clicked.connect(self.duplicate_field)
        self.duplicate_btn.setEnabled(False)
        toolbar.addWidget(self.duplicate_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.field_table = QTableWidget()
        self.field_table.setColumnCount(6)
        self.field_table.setHorizontalHeaderLabels([
            "Thứ Tự", "Tên Trường", "Loại", "Bắt Buộc", "Danh Mục", "Trạng Thái"
        ])
        self.field_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.field_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.field_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.field_table.setDragDropMode(QTableWidget.DragDropMode.InternalMove)
        self.field_table.setDragEnabled(True)
        self.field_table.setAcceptDrops(True)
        self.field_table.setDropIndicatorShown(True)
        self.field_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.field_table.cellDoubleClicked.connect(lambda: self.edit_field())
        
        layout.addWidget(self.field_table)
        
        return widget
    
    def _create_preview_section(self):
        """Create the preview section"""
        widget = QGroupBox("Xem Trước")
        layout = QVBoxLayout(widget)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        return widget
    
    def _create_button_layout(self):
        """Create bottom button layout"""
        layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Xuất Cấu Hình")
        self.export_btn.clicked.connect(self.export_configs)
        layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("Nhập Cấu Hình")
        self.import_btn.clicked.connect(self.import_configs)
        layout.addWidget(self.import_btn)
        
        layout.addStretch()
        
        self.close_btn = QPushButton("Đóng")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
        
        return layout
    
    def load_field_configs(self):
        """Load field configurations from database"""
        try:
            self.current_configs = self.field_config_service.get_field_configs_by_department(
                self.department_id, active_only=False
            )
            self.refresh_table()
        except Exception as e:
            logger.error(f"Error loading field configs: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải cấu hình trường: {str(e)}")
    
    def refresh_table(self):
        """Refresh the field table"""
        self.field_table.setRowCount(0)
        
        for config in self.current_configs:
            row = self.field_table.rowCount()
            self.field_table.insertRow(row)
            
            self.field_table.setItem(row, 0, QTableWidgetItem(str(config.display_order)))
            self.field_table.setItem(row, 1, QTableWidgetItem(config.field_name))
            self.field_table.setItem(row, 2, QTableWidgetItem(config.field_type))
            self.field_table.setItem(row, 3, QTableWidgetItem("Có" if config.is_required else "Không"))
            self.field_table.setItem(row, 4, QTableWidgetItem(config.category or ""))
            self.field_table.setItem(row, 5, QTableWidgetItem("Hoạt động" if config.is_active else "Không hoạt động"))
            
            # Store config ID in first column
            self.field_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, config.id)
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.field_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection)
        
        if has_selection:
            self.update_preview()
    
    def update_preview(self):
        """Update the preview pane"""
        selected_row = self.field_table.currentRow()
        if selected_row < 0:
            self.preview_text.clear()
            return
        
        config_id = self.field_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        config = next((c for c in self.current_configs if c.id == config_id), None)
        
        if config:
            preview = f"""
<h3>{config.field_name}</h3>
<p><b>Loại:</b> {config.field_type}</p>
<p><b>Widget:</b> {config.widget_type}</p>
<p><b>Bắt buộc:</b> {'Có' if config.is_required else 'Không'}</p>
<p><b>Danh mục:</b> {config.category or 'Không có'}</p>
<p><b>Thứ tự:</b> {config.display_order}</p>
<p><b>Giá trị mặc định:</b> {config.default_value or 'Không có'}</p>
"""
            if config.options:
                preview += f"<p><b>Tùy chọn:</b> {', '.join(config.options)}</p>"
            
            if config.validation_rules:
                preview += "<p><b>Quy tắc validation:</b></p><ul>"
                for key, value in config.validation_rules.items():
                    preview += f"<li>{key}: {value}</li>"
                preview += "</ul>"
            
            self.preview_text.setHtml(preview)
    
    def add_field(self):
        """Add a new field configuration"""
        dialog = FieldEditDialog(self.field_config_service, self.department_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_field_configs()
            self.fields_changed.emit()
    
    def edit_field(self):
        """Edit selected field configuration"""
        selected_row = self.field_table.currentRow()
        if selected_row < 0:
            return
        
        config_id = self.field_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        config = next((c for c in self.current_configs if c.id == config_id), None)
        
        if config:
            dialog = FieldEditDialog(
                self.field_config_service, 
                self.department_id, 
                config=config,
                parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_field_configs()
                self.fields_changed.emit()
    
    def delete_field(self):
        """Delete selected field configuration"""
        selected_row = self.field_table.currentRow()
        if selected_row < 0:
            return
        
        config_id = self.field_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        config = next((c for c in self.current_configs if c.id == config_id), None)
        
        if config:
            reply = QMessageBox.question(
                self,
                "Xác Nhận Xóa",
                f"Bạn có chắc muốn xóa trường '{config.field_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.field_config_service.delete_field_config(config_id, soft_delete=True)
                    self.load_field_configs()
                    self.fields_changed.emit()
                    QMessageBox.information(self, "Thành Công", "Đã xóa trường thành công")
                except Exception as e:
                    logger.error(f"Error deleting field: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa trường: {str(e)}")
    
    def duplicate_field(self):
        """Duplicate selected field configuration"""
        selected_row = self.field_table.currentRow()
        if selected_row < 0:
            return
        
        config_id = self.field_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            duplicated = self.field_config_service.duplicate_field_config(config_id)
            self.load_field_configs()
            self.fields_changed.emit()
            QMessageBox.information(self, "Thành Công", f"Đã nhân bản trường thành '{duplicated.field_name}'")
        except Exception as e:
            logger.error(f"Error duplicating field: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể nhân bản trường: {str(e)}")
    
    def export_configs(self):
        """Export field configurations to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất Cấu Hình",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                configs_data = [
                    config.model_dump(exclude={'id', 'created_at'})
                    for config in self.current_configs
                    if config.is_active
                ]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(configs_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Thành Công", f"Đã xuất {len(configs_data)} cấu hình")
            except Exception as e:
                logger.error(f"Error exporting configs: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xuất cấu hình: {str(e)}")
    
    def import_configs(self):
        """Import field configurations from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập Cấu Hình",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    configs_data = json.load(f)
                
                if not isinstance(configs_data, list):
                    raise ValueError("File JSON phải chứa một mảng các cấu hình")
                
                imported_count = 0
                for config_data in configs_data:
                    config_data['department_id'] = self.department_id
                    try:
                        self.field_config_service.create_field_config(config_data)
                        imported_count += 1
                    except Exception as e:
                        logger.warning(f"Skipped config {config_data.get('field_name')}: {e}")
                
                self.load_field_configs()
                self.fields_changed.emit()
                QMessageBox.information(
                    self, 
                    "Thành Công", 
                    f"Đã nhập {imported_count}/{len(configs_data)} cấu hình"
                )
            except Exception as e:
                logger.error(f"Error importing configs: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập cấu hình: {str(e)}")
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for reordering"""
        super().dropEvent(event)
        self.reorder_fields()
    
    def reorder_fields(self):
        """Reorder fields based on table order"""
        try:
            config_orders = []
            for row in range(self.field_table.rowCount()):
                config_id = self.field_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                config_orders.append({'id': config_id, 'display_order': row})
            
            self.field_config_service.reorder_field_configs(config_orders)
            self.load_field_configs()
            self.fields_changed.emit()
        except Exception as e:
            logger.error(f"Error reordering fields: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể sắp xếp lại: {str(e)}")


class FieldEditDialog(QDialog):
    """Dialog for adding/editing a field configuration"""
    
    def __init__(self, field_config_service: FieldConfigService, department_id: int, 
                 config: Optional[FieldConfiguration] = None, parent=None):
        super().__init__(parent)
        self.field_config_service = field_config_service
        self.department_id = department_id
        self.config = config
        self.is_edit_mode = config is not None
        
        self.setWindowTitle("Sửa Trường" if self.is_edit_mode else "Thêm Trường")
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_config_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Field name
        self.field_name_edit = QLineEdit()
        form_layout.addRow("Tên Trường:", self.field_name_edit)
        
        # Field type
        self.field_type_combo = QComboBox()
        field_types = self.field_config_service.get_available_field_types()
        for ft in field_types:
            self.field_type_combo.addItem(ft['label'], ft['value'])
        self.field_type_combo.currentIndexChanged.connect(self.on_field_type_changed)
        form_layout.addRow("Loại Trường:", self.field_type_combo)
        
        # Category
        self.category_edit = QLineEdit()
        form_layout.addRow("Danh Mục:", self.category_edit)
        
        # Is required
        self.is_required_check = QCheckBox()
        form_layout.addRow("Bắt Buộc:", self.is_required_check)
        
        # Default value
        self.default_value_edit = QLineEdit()
        form_layout.addRow("Giá Trị Mặc Định:", self.default_value_edit)
        
        # Display order
        self.display_order_spin = QSpinBox()
        self.display_order_spin.setMinimum(0)
        self.display_order_spin.setMaximum(999)
        form_layout.addRow("Thứ Tự Hiển Thị:", self.display_order_spin)
        
        # Options (for dropdown)
        self.options_label = QLabel("Tùy Chọn (mỗi dòng một tùy chọn):")
        self.options_text = QTextEdit()
        self.options_text.setMaximumHeight(100)
        form_layout.addRow(self.options_label, self.options_text)
        
        # Is active
        self.is_active_check = QCheckBox()
        self.is_active_check.setChecked(True)
        form_layout.addRow("Hoạt Động:", self.is_active_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.on_field_type_changed()
    
    def on_field_type_changed(self):
        """Handle field type change"""
        field_type = self.field_type_combo.currentData()
        is_dropdown = field_type == FieldType.DROPDOWN
        self.options_label.setVisible(is_dropdown)
        self.options_text.setVisible(is_dropdown)
    
    def load_config_data(self):
        """Load existing config data into form"""
        if not self.config:
            return
        
        self.field_name_edit.setText(self.config.field_name)
        
        index = self.field_type_combo.findData(self.config.field_type)
        if index >= 0:
            self.field_type_combo.setCurrentIndex(index)
        
        self.category_edit.setText(self.config.category or "")
        self.is_required_check.setChecked(self.config.is_required)
        self.default_value_edit.setText(self.config.default_value or "")
        self.display_order_spin.setValue(self.config.display_order)
        
        if self.config.options:
            self.options_text.setPlainText("\n".join(self.config.options))
        
        self.is_active_check.setChecked(self.config.is_active)
    
    def save_config(self):
        """Save the field configuration"""
        try:
            field_name = self.field_name_edit.text().strip()
            if not field_name:
                QMessageBox.warning(self, "Lỗi", "Tên trường không được để trống")
                return
            
            field_type = self.field_type_combo.currentData()
            widget_type = self.field_config_service.get_widget_type_for_field_type(field_type)
            
            config_data = {
                'department_id': self.department_id,
                'field_name': field_name,
                'field_type': field_type,
                'widget_type': widget_type,
                'is_required': self.is_required_check.isChecked(),
                'category': self.category_edit.text().strip() or None,
                'default_value': self.default_value_edit.text().strip() or None,
                'display_order': self.display_order_spin.value(),
                'is_active': self.is_active_check.isChecked()
            }
            
            # Handle options for dropdown
            if field_type == FieldType.DROPDOWN:
                options_text = self.options_text.toPlainText().strip()
                if options_text:
                    options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
                    config_data['options'] = options
                else:
                    QMessageBox.warning(self, "Lỗi", "Trường dropdown phải có ít nhất một tùy chọn")
                    return
            
            # Validate
            validation_result = self.field_config_service.validate_field_config_data(config_data)
            if not validation_result['is_valid']:
                error_msg = "\n".join(validation_result['errors'])
                QMessageBox.warning(self, "Lỗi Validation", error_msg)
                return
            
            # Save
            if self.is_edit_mode:
                self.field_config_service.update_field_config(self.config.id, config_data)
                QMessageBox.information(self, "Thành Công", "Đã cập nhật trường thành công")
            else:
                self.field_config_service.create_field_config(config_data)
                QMessageBox.information(self, "Thành Công", "Đã thêm trường thành công")
            
            self.accept()
        except Exception as e:
            logger.error(f"Error saving field config: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cấu hình: {str(e)}")
