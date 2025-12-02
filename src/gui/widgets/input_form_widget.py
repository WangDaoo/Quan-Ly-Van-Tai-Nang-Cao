"""
Input Form Widget Module
Specialized form widget for trip data input with dynamic form integration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any, Optional

from src.models.field_configuration import FieldConfiguration
from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService
from src.services.formula_engine import FormulaEngine
from src.services.workflow_service import WorkflowService
from .dynamic_form_widget import DynamicFormWidget


class InputFormWidget(QWidget):
    """
    Input form widget for trip data entry
    Integrates DynamicFormWidget with trip-specific functionality
    
    Features:
    - Dynamic form based on field configurations
    - Form submission with validation
    - Auto-focus and tab navigation
    - Form reset after successful submit
    - Integration with TripService
    """
    
    # Signals
    tripCreated = pyqtSignal(dict)  # Emitted when trip is created successfully
    tripUpdated = pyqtSignal(dict)  # Emitted when trip is updated successfully
    formCleared = pyqtSignal()  # Emitted when form is cleared
    validationFailed = pyqtSignal(dict)  # Emitted when validation fails
    
    def __init__(self, trip_service: TripService, 
                 field_config_service: FieldConfigService = None,
                 department_id: int = None,
                 parent=None):
        """
        Initialize input form widget
        
        Args:
            trip_service: TripService instance for database operations
            field_config_service: FieldConfigService for loading field configs
            department_id: Department ID for loading specific field configs
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.trip_service = trip_service
        self.field_config_service = field_config_service
        self.department_id = department_id
        self._current_trip_id = None  # For edit mode
        self._is_edit_mode = False
        
        # Formula engine for auto-calculation
        self.formula_engine = None
        self.workflow_service = None
        if trip_service and hasattr(trip_service, 'db'):
            self.formula_engine = FormulaEngine(trip_service.db)
            self.workflow_service = WorkflowService(trip_service.db)
        
        self._setup_ui()
        self._load_field_configurations()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Title label
        self.title_label = QLabel("Nhập Thông Tin Chuyến Xe")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(self.title_label)
        
        # Dynamic form widget
        self.form_widget = DynamicFormWidget(show_buttons=False)
        main_layout.addWidget(self.form_widget)
        
        # Custom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.clear_button = QPushButton("Xóa")
        self.clear_button.setMinimumWidth(100)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        self.submit_button = QPushButton("Thêm Chuyến")
        self.submit_button.setMinimumWidth(100)
        self.submit_button.setDefault(True)
        self.submit_button.clicked.connect(self._on_submit_clicked)
        button_layout.addWidget(self.submit_button)
        
        main_layout.addLayout(button_layout)
        
        # Status message
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        main_layout.addWidget(self.status_label)
    
    def _load_field_configurations(self):
        """Load field configurations from database"""
        if not self.field_config_service or not self.department_id:
            # Use default trip fields if no field config service
            self._use_default_fields()
            return
        
        try:
            # Load field configs for department
            field_configs = self.field_config_service.get_field_configs_by_department(
                self.department_id
            )
            
            if field_configs:
                self.form_widget.load_field_configs(field_configs)
            else:
                self._use_default_fields()
                
        except Exception as e:
            self._show_error(f"Lỗi tải cấu hình form: {str(e)}")
            self._use_default_fields()
    
    def _use_default_fields(self):
        """Use default trip fields when no configuration is available"""
        default_configs = [
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="khach_hang",
                field_type="text",
                widget_type="textbox",
                is_required=True,
                display_order=1,
                category="Thông Tin Cơ Bản"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="diem_di",
                field_type="text",
                widget_type="textbox",
                is_required=False,
                display_order=2,
                category="Thông Tin Cơ Bản"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="diem_den",
                field_type="text",
                widget_type="textbox",
                is_required=False,
                display_order=3,
                category="Thông Tin Cơ Bản"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="gia_ca",
                field_type="currency",
                widget_type="currency",
                is_required=True,
                display_order=4,
                category="Thông Tin Tài Chính"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="khoan_luong",
                field_type="currency",
                widget_type="currency",
                is_required=False,
                default_value="0",
                display_order=5,
                category="Thông Tin Tài Chính"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="chi_phi_khac",
                field_type="currency",
                widget_type="currency",
                is_required=False,
                default_value="0",
                display_order=6,
                category="Thông Tin Tài Chính"
            ),
            FieldConfiguration(
                department_id=self.department_id or 1,
                field_name="ghi_chu",
                field_type="textarea",
                widget_type="textarea",
                is_required=False,
                display_order=7,
                category="Thông Tin Bổ Sung"
            ),
        ]
        
        self.form_widget.load_field_configs(default_configs)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Connect form signals
        self.form_widget.formDataChanged.connect(self._on_form_data_changed)
        self.form_widget.validationFailed.connect(self._on_validation_failed)
        
        # Auto-focus first field
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def _on_form_data_changed(self, data: Dict[str, Any]):
        """
        Handle form data changes
        
        Implements:
        - Automatic formula evaluation (Requirement 6.3)
        - Update calculated fields real-time (Requirement 6.3)
        - Error handling for formula errors (Requirement 6.3)
        """
        # Hide status message when user types
        self.status_label.hide()
        
        # Evaluate formulas if formula engine is available
        if self.formula_engine and self.department_id:
            try:
                # Get calculated values from formulas
                calculated_values = self.formula_engine.evaluate_all_formulas(
                    self.department_id,
                    data
                )
                
                # Update calculated fields
                for field_name, value in calculated_values.items():
                    current_value = self.form_widget.get_field_value(field_name)
                    # Only update if value changed to avoid infinite loops
                    if current_value != value:
                        # Block signals temporarily to avoid triggering another calculation
                        widget = self.form_widget.get_field_widget(field_name)
                        if widget:
                            widget.blockSignals(True)
                            self.form_widget.set_field_value(field_name, value)
                            widget.blockSignals(False)
                
            except Exception as e:
                # Log error but don't show to user unless it's critical
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error evaluating formulas: {e}")
    
    def _on_validation_failed(self, errors: Dict[str, str]):
        """Handle validation failures"""
        self.validationFailed.emit(errors)
    
    def _on_clear_clicked(self):
        """Handle clear button click"""
        self.clear_form()
    
    def _on_submit_clicked(self):
        """Handle submit button click"""
        self.submit_form()
    
    def submit_form(self):
        """
        Submit the form after validation
        
        Implements:
        - Validation before save (Requirement 1.2)
        - Success/error message display (Requirement 1.1)
        - Form reset after save (Requirement 1.1)
        - Auto-refresh table after save (Requirement 1.5)
        """
        # Validate form
        if not self.form_widget.validate_form(show_errors=True):
            self._show_error("Vui lòng kiểm tra lại thông tin nhập vào")
            self.validationFailed.emit({"form": "Validation failed"})
            return
        
        # Get form data
        form_data = self.form_widget.get_form_data()
        
        # Additional validation for required fields
        if not form_data.get('khach_hang'):
            self._show_error("Khách hàng là trường bắt buộc")
            self.validationFailed.emit({"khach_hang": "Required field"})
            return
        
        if not form_data.get('gia_ca'):
            self._show_error("Giá cả là trường bắt buộc")
            self.validationFailed.emit({"gia_ca": "Required field"})
            return
        
        try:
            if self._is_edit_mode and self._current_trip_id:
                # Update existing trip
                updated_trip = self.trip_service.update_trip(
                    self._current_trip_id, 
                    form_data
                )
                self._show_success(f"✓ Đã cập nhật chuyến {updated_trip.ma_chuyen}")
                self.tripUpdated.emit(updated_trip.model_dump())
                
                # Check workflow automation for updates
                self._check_workflow_automation(
                    self._current_trip_id,
                    updated_trip.model_dump()
                )
            else:
                # Create new trip
                created_trip = self.trip_service.create_trip(form_data)
                self._show_success(f"✓ Đã thêm chuyến {created_trip.ma_chuyen}")
                self.tripCreated.emit(created_trip.model_dump())
                
                # Check workflow automation for new records
                self._check_workflow_automation(
                    created_trip.id,
                    created_trip.model_dump()
                )
            
            # Reset form after successful submit
            self.clear_form()
            self._set_focus_to_first_field()
            
        except ValueError as e:
            error_msg = f"Lỗi validation: {str(e)}"
            self._show_error(error_msg)
            self.validationFailed.emit({"validation": str(e)})
        except Exception as e:
            error_msg = f"Lỗi lưu dữ liệu: {str(e)}"
            self._show_error(error_msg)
            self.validationFailed.emit({"database": str(e)})
    
    def clear_form(self):
        """Clear the form"""
        self.form_widget.clear_form()
        self._current_trip_id = None
        self._is_edit_mode = False
        self.submit_button.setText("Thêm Chuyến")
        self.status_label.hide()
        self.formCleared.emit()
    
    def load_trip_data(self, trip_data: Dict[str, Any]):
        """
        Load trip data into form for editing
        
        Args:
            trip_data: Dictionary containing trip data
        """
        self.form_widget.set_form_data(trip_data)
        
        if 'id' in trip_data:
            self._current_trip_id = trip_data['id']
            self._is_edit_mode = True
            self.submit_button.setText("Cập Nhật")
        
        self.status_label.hide()
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get current form data"""
        return self.form_widget.get_form_data()
    
    def set_field_value(self, field_name: str, value: Any):
        """Set value for a specific field"""
        self.form_widget.set_field_value(field_name, value)
    
    def get_field_value(self, field_name: str) -> Any:
        """Get value from a specific field"""
        return self.form_widget.get_field_value(field_name)
    
    def _set_focus_to_first_field(self):
        """Set focus to the first field in the form"""
        field_widgets = self.form_widget.form_builder.get_all_field_widgets()
        if field_widgets:
            first_widget = next(iter(field_widgets.values()))
            first_widget.setFocus()
    
    def _show_success(self, message: str):
        """Show success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.show()
    
    def _show_error(self, message: str):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.show()
    
    def set_department_id(self, department_id: int):
        """
        Set department ID and reload field configurations
        
        Args:
            department_id: Department ID
        """
        self.department_id = department_id
        self._load_field_configurations()
    
    def reload_field_configurations(self):
        """Reload field configurations from database"""
        self._load_field_configurations()
    
    def set_edit_mode(self, enabled: bool):
        """
        Enable or disable edit mode
        
        Args:
            enabled: True for edit mode, False for create mode
        """
        self._is_edit_mode = enabled
        if enabled:
            self.submit_button.setText("Cập Nhật")
        else:
            self.submit_button.setText("Thêm Chuyến")
            self._current_trip_id = None
    
    def is_edit_mode(self) -> bool:
        """Check if widget is in edit mode"""
        return self._is_edit_mode
    
    def get_current_trip_id(self) -> Optional[int]:
        """Get current trip ID in edit mode"""
        return self._current_trip_id
    
    def _check_workflow_automation(self, record_id: int, record_data: Dict[str, Any]):
        """
        Check and execute workflow automation
        
        Implements:
        - Automatic condition evaluation (Requirement 7.3)
        - Auto-push when conditions met (Requirement 7.4)
        - Workflow history logging (Requirement 7.5)
        
        Args:
            record_id: ID of the record
            record_data: Dictionary of record data
        """
        if not self.workflow_service or not self.department_id:
            return
        
        try:
            # Get all departments to check for push conditions
            # For now, we'll check push to all other departments
            # In a real implementation, this would be configurable
            
            # Get available target departments (excluding current)
            query = "SELECT id FROM departments WHERE is_active = 1 AND id != ?"
            db_manager = self.trip_service.db
            target_depts = db_manager.fetch_all(query, (self.department_id,))
            
            for dept_row in target_depts:
                target_dept_id = dept_row[0]
                
                # Try auto-push if conditions are met
                success = self.workflow_service.auto_push_if_conditions_met(
                    record_id=record_id,
                    record_data=record_data,
                    source_department_id=self.department_id,
                    target_department_id=target_dept_id,
                    pushed_by=None,  # Could be set to current user ID
                    field_mapping=None  # Could be configured per department
                )
                
                if success:
                    # Show notification
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(
                        f"Auto-pushed record {record_id} from dept {self.department_id} "
                        f"to dept {target_dept_id}"
                    )
                    
        except Exception as e:
            # Log error but don't interrupt user workflow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in workflow automation: {e}")
    
    def manual_push_to_department(
        self,
        target_department_id: int,
        record_id: Optional[int] = None,
        record_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Manually push record to another department
        
        Implements:
        - Manual push option (Requirement 7.4)
        
        Args:
            target_department_id: Target department ID
            record_id: Record ID (uses current if not provided)
            record_data: Record data (uses current form data if not provided)
            
        Returns:
            True if push successful, False otherwise
        """
        if not self.workflow_service or not self.department_id:
            return False
        
        # Use current trip if not provided
        if record_id is None:
            record_id = self._current_trip_id
        
        if record_data is None:
            record_data = self.form_widget.get_form_data()
        
        if not record_id or not record_data:
            QMessageBox.warning(
                self,
                "Lỗi",
                "Không có dữ liệu để đẩy"
            )
            return False
        
        try:
            # Perform manual push
            success = self.workflow_service.push_record(
                record_id=record_id,
                record_data=record_data,
                source_department_id=self.department_id,
                target_department_id=target_department_id,
                pushed_by=None,  # Could be set to current user ID
                field_mapping=None  # Could be configured
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Thành Công",
                    f"Đã đẩy dữ liệu sang phòng ban đích"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    "Không thể đẩy dữ liệu"
                )
            
            return success
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Lỗi đẩy dữ liệu: {str(e)}"
            )
            return False
