"""
Field Preset Dialog - Dialog for managing field configuration presets
Provides preset list view, load functionality, preview, and validation
"""
import json
import logging
from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QListWidget, QListWidgetItem, QGroupBox,
    QTextEdit, QFileDialog, QSplitter, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.field_config_service import FieldConfigService

logger = logging.getLogger(__name__)


class FieldPresetDialog(QDialog):
    """
    Dialog for managing field configuration presets.
    
    Features:
    - Preset list view
    - Load preset functionality
    - Preset preview
    - Preset validation
    - Import/Export presets
    """
    
    preset_loaded = pyqtSignal(str)  # Emits preset name
    
    def __init__(self, field_config_service: FieldConfigService, department_id: int, parent=None):
        super().__init__(parent)
        self.field_config_service = field_config_service
        self.department_id = department_id
        self.presets: Dict[str, Dict[str, Any]] = {}
        
        self.setWindowTitle("Quản Lý Preset Cấu Hình")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_presets()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Preset list
        left_widget = self._create_preset_list_section()
        splitter.addWidget(left_widget)
        
        # Right side - Preview
        right_widget = self._create_preview_section()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Nhập Preset")
        import_btn.clicked.connect(self.import_preset)
        button_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Xuất Preset")
        export_btn.clicked.connect(self.export_preset)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_preset_list_section(self):
        """Create the preset list section"""
        widget = QGroupBox("Danh Sách Preset")
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.load_btn = QPushButton("Tải Preset")
        self.load_btn.clicked.connect(self.load_selected_preset)
        self.load_btn.setEnabled(False)
        toolbar.addWidget(self.load_btn)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_preset)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # List widget
        self.preset_list = QListWidget()
        self.preset_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.preset_list.itemDoubleClicked.connect(self.load_selected_preset)
        layout.addWidget(self.preset_list)
        
        # Info label
        self.info_label = QLabel("Không có preset nào")
        self.info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.info_label)
        
        return widget
    
    def _create_preview_section(self):
        """Create the preview section"""
        widget = QGroupBox("Xem Trước Preset")
        layout = QVBoxLayout(widget)
        
        # Preset details
        details_layout = QVBoxLayout()
        
        self.preset_name_label = QLabel("Tên: ---")
        self.preset_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self.preset_name_label)
        
        self.preset_type_label = QLabel("Loại: ---")
        details_layout.addWidget(self.preset_type_label)
        
        self.preset_count_label = QLabel("Số lượng: ---")
        details_layout.addWidget(self.preset_count_label)
        
        layout.addLayout(details_layout)
        
        # Preview text
        layout.addWidget(QLabel("Nội dung:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        # Validation status
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)
        
        return widget
    
    def load_presets(self):
        """Load available presets"""
        # In a real implementation, this would load from a preset directory or database
        # For now, we'll create some example presets
        self.presets = {
            "Cơ Bản": {
                "type": "field_configs",
                "description": "Cấu hình trường cơ bản",
                "data": [
                    {
                        "field_name": "Mã chuyến",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": True,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Khách hàng",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": True,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Giá cả",
                        "field_type": "currency",
                        "widget_type": "currency",
                        "is_required": True,
                        "category": "Tài chính"
                    }
                ]
            },
            "Đầy Đủ": {
                "type": "field_configs",
                "description": "Cấu hình trường đầy đủ",
                "data": [
                    {
                        "field_name": "Mã chuyến",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": True,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Khách hàng",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": True,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Điểm đi",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": False,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Điểm đến",
                        "field_type": "text",
                        "widget_type": "textbox",
                        "is_required": False,
                        "category": "Thông tin cơ bản"
                    },
                    {
                        "field_name": "Giá cả",
                        "field_type": "currency",
                        "widget_type": "currency",
                        "is_required": True,
                        "category": "Tài chính"
                    },
                    {
                        "field_name": "Khoán lương",
                        "field_type": "currency",
                        "widget_type": "currency",
                        "is_required": False,
                        "category": "Tài chính"
                    },
                    {
                        "field_name": "Chi phí khác",
                        "field_type": "currency",
                        "widget_type": "currency",
                        "is_required": False,
                        "category": "Tài chính"
                    },
                    {
                        "field_name": "Ghi chú",
                        "field_type": "textarea",
                        "widget_type": "textarea",
                        "is_required": False,
                        "category": "Khác"
                    }
                ]
            }
        }
        
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the preset list"""
        self.preset_list.clear()
        
        for preset_name in self.presets.keys():
            item = QListWidgetItem(preset_name)
            self.preset_list.addItem(item)
        
        if self.presets:
            self.info_label.setText(f"Có {len(self.presets)} preset")
        else:
            self.info_label.setText("Không có preset nào")
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = self.preset_list.currentItem() is not None
        self.load_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection:
            self.update_preview()
    
    def update_preview(self):
        """Update the preview pane"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            self.preset_name_label.setText("Tên: ---")
            self.preset_type_label.setText("Loại: ---")
            self.preset_count_label.setText("Số lượng: ---")
            self.preview_text.clear()
            self.validation_label.clear()
            return
        
        preset_name = current_item.text()
        preset = self.presets.get(preset_name)
        
        if preset:
            self.preset_name_label.setText(f"Tên: {preset_name}")
            
            preset_type = preset.get('type', 'unknown')
            type_labels = {
                'field_configs': 'Cấu hình trường',
                'formulas': 'Công thức',
                'push_conditions': 'Điều kiện đẩy'
            }
            self.preset_type_label.setText(f"Loại: {type_labels.get(preset_type, preset_type)}")
            
            data = preset.get('data', [])
            self.preset_count_label.setText(f"Số lượng: {len(data)} items")
            
            # Display data as formatted JSON
            preview_json = json.dumps(preset, indent=2, ensure_ascii=False)
            self.preview_text.setPlainText(preview_json)
            
            # Validate preset
            self.validate_preset(preset)
    
    def validate_preset(self, preset: Dict[str, Any]):
        """Validate a preset"""
        try:
            preset_type = preset.get('type')
            data = preset.get('data', [])
            
            if not preset_type:
                self.validation_label.setText("⚠ Preset thiếu thông tin loại")
                self.validation_label.setStyleSheet("color: orange;")
                return
            
            if not data:
                self.validation_label.setText("⚠ Preset không có dữ liệu")
                self.validation_label.setStyleSheet("color: orange;")
                return
            
            # Validate based on type
            if preset_type == 'field_configs':
                errors = []
                for i, config in enumerate(data):
                    if 'field_name' not in config:
                        errors.append(f"Item {i+1}: Thiếu field_name")
                    if 'field_type' not in config:
                        errors.append(f"Item {i+1}: Thiếu field_type")
                
                if errors:
                    self.validation_label.setText("✗ Lỗi validation:\n" + "\n".join(errors))
                    self.validation_label.setStyleSheet("color: red;")
                else:
                    self.validation_label.setText("✓ Preset hợp lệ")
                    self.validation_label.setStyleSheet("color: green;")
            else:
                self.validation_label.setText("✓ Preset hợp lệ")
                self.validation_label.setStyleSheet("color: green;")
        except Exception as e:
            logger.error(f"Error validating preset: {e}")
            self.validation_label.setText(f"✗ Lỗi validation: {str(e)}")
            self.validation_label.setStyleSheet("color: red;")
    
    def load_selected_preset(self):
        """Load the selected preset"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            return
        
        preset_name = current_item.text()
        preset = self.presets.get(preset_name)
        
        if not preset:
            return
        
        reply = QMessageBox.question(
            self,
            "Xác Nhận Tải Preset",
            f"Bạn có chắc muốn tải preset '{preset_name}'?\n"
            "Điều này sẽ thêm các cấu hình từ preset vào phòng ban hiện tại.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                preset_type = preset.get('type')
                data = preset.get('data', [])
                
                if preset_type == 'field_configs':
                    self.load_field_configs(data)
                elif preset_type == 'formulas':
                    self.load_formulas(data)
                elif preset_type == 'push_conditions':
                    self.load_push_conditions(data)
                else:
                    QMessageBox.warning(self, "Lỗi", f"Loại preset không được hỗ trợ: {preset_type}")
                    return
                
                self.preset_loaded.emit(preset_name)
                QMessageBox.information(self, "Thành Công", f"Đã tải preset '{preset_name}'")
            except Exception as e:
                logger.error(f"Error loading preset: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể tải preset: {str(e)}")
    
    def load_field_configs(self, configs: List[Dict[str, Any]]):
        """Load field configurations from preset"""
        loaded_count = 0
        skipped_count = 0
        
        for config_data in configs:
            try:
                config_data['department_id'] = self.department_id
                self.field_config_service.create_field_config(config_data)
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Skipped config {config_data.get('field_name')}: {e}")
                skipped_count += 1
        
        if skipped_count > 0:
            QMessageBox.information(
                self,
                "Kết Quả",
                f"Đã tải {loaded_count} cấu hình\n"
                f"Bỏ qua {skipped_count} cấu hình (có thể đã tồn tại)"
            )
    
    def load_formulas(self, formulas: List[Dict[str, Any]]):
        """Load formulas from preset"""
        # Implementation would be similar to load_field_configs
        QMessageBox.information(self, "Thông Báo", "Tính năng đang được phát triển")
    
    def load_push_conditions(self, conditions: List[Dict[str, Any]]):
        """Load push conditions from preset"""
        # Implementation would be similar to load_field_configs
        QMessageBox.information(self, "Thông Báo", "Tính năng đang được phát triển")
    
    def delete_preset(self):
        """Delete selected preset"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            return
        
        preset_name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "Xác Nhận Xóa",
            f"Bạn có chắc muốn xóa preset '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                del self.presets[preset_name]
                self.refresh_list()
                QMessageBox.information(self, "Thành Công", "Đã xóa preset")
            except Exception as e:
                logger.error(f"Error deleting preset: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa preset: {str(e)}")
    
    def import_preset(self):
        """Import preset from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập Preset",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                
                # Ask for preset name
                preset_name, ok = QInputDialog.getText(
                    self,
                    "Tên Preset",
                    "Nhập tên cho preset:",
                    text=preset_data.get('name', 'Imported Preset')
                )
                
                if ok and preset_name:
                    self.presets[preset_name] = preset_data
                    self.refresh_list()
                    QMessageBox.information(self, "Thành Công", "Đã nhập preset")
            except Exception as e:
                logger.error(f"Error importing preset: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập preset: {str(e)}")
    
    def export_preset(self):
        """Export selected preset to JSON file"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn preset để xuất")
            return
        
        preset_name = current_item.text()
        preset = self.presets.get(preset_name)
        
        if preset:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Xuất Preset",
                f"{preset_name}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(preset, f, ensure_ascii=False, indent=2)
                    
                    QMessageBox.information(self, "Thành Công", "Đã xuất preset")
                except Exception as e:
                    logger.error(f"Error exporting preset: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể xuất preset: {str(e)}")
