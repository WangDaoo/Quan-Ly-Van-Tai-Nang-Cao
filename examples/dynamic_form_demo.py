"""
Demo script for Dynamic Form System
Demonstrates the 10 field widgets, validators, form builder, and dynamic form widget
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from src.models.field_configuration import FieldConfiguration
from src.gui.widgets import DynamicFormWidget


def create_sample_field_configs():
    """Create sample field configurations for testing"""
    configs = [
        # Text field
        FieldConfiguration(
            id=1,
            department_id=1,
            field_name="Tên khách hàng",
            field_type="text",
            widget_type="textbox",
            is_required=True,
            validation_rules={"max_length": 100},
            display_order=1,
            category="Thông tin cơ bản"
        ),
        
        # Number field
        FieldConfiguration(
            id=2,
            department_id=1,
            field_name="Số lượng",
            field_type="number",
            widget_type="number",
            is_required=False,
            validation_rules={},
            display_order=2,
            category="Thông tin cơ bản"
        ),
        
        # Currency field
        FieldConfiguration(
            id=3,
            department_id=1,
            field_name="Giá cả",
            field_type="currency",
            widget_type="currency",
            is_required=True,
            validation_rules={},
            display_order=3,
            category="Thông tin cơ bản"
        ),
        
        # Date field
        FieldConfiguration(
            id=4,
            department_id=1,
            field_name="Ngày giao hàng",
            field_type="date",
            widget_type="date_edit",
            is_required=False,
            display_order=4,
            category="Thông tin cơ bản"
        ),
        
        # Dropdown field
        FieldConfiguration(
            id=5,
            department_id=1,
            field_name="Điểm đi",
            field_type="dropdown",
            widget_type="combobox",
            is_required=True,
            options=["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng"],
            validation_rules={},
            display_order=5,
            category="Địa điểm"
        ),
        
        # Checkbox field
        FieldConfiguration(
            id=6,
            department_id=1,
            field_name="Đã thanh toán",
            field_type="checkbox",
            widget_type="checkbox",
            is_required=False,
            validation_rules={},
            display_order=6,
            category="Thanh toán"
        ),
        
        # Email field
        FieldConfiguration(
            id=7,
            department_id=1,
            field_name="Email liên hệ",
            field_type="email",
            widget_type="email",
            is_required=False,
            validation_rules={},
            display_order=7,
            category="Liên hệ"
        ),
        
        # Phone field
        FieldConfiguration(
            id=8,
            department_id=1,
            field_name="Số điện thoại",
            field_type="phone",
            widget_type="phone",
            is_required=False,
            validation_rules={},
            display_order=8,
            category="Liên hệ"
        ),
        
        # TextArea field
        FieldConfiguration(
            id=9,
            department_id=1,
            field_name="Ghi chú",
            field_type="textarea",
            widget_type="textarea",
            is_required=False,
            validation_rules={"max_length": 500},
            display_order=9,
            category="Thông tin bổ sung"
        ),
        
        # URL field
        FieldConfiguration(
            id=10,
            department_id=1,
            field_name="Website",
            field_type="url",
            widget_type="url",
            is_required=False,
            validation_rules={},
            display_order=10,
            category="Thông tin bổ sung"
        ),
    ]
    
    return configs


class DynamicFormDemo(QMainWindow):
    """Demo window for dynamic form system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Form System Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create sample field configs
        field_configs = create_sample_field_configs()
        
        # Tab 1: Full form with all widgets
        form_widget = DynamicFormWidget(field_configs, show_buttons=True)
        form_widget.formSubmitted.connect(self.on_form_submitted)
        form_widget.formCleared.connect(self.on_form_cleared)
        form_widget.formDataChanged.connect(self.on_form_data_changed)
        form_widget.validationFailed.connect(self.on_validation_failed)
        
        tab_widget.addTab(form_widget, "Dynamic Form")
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def on_form_submitted(self, data):
        """Handle form submission"""
        print("Form submitted with data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        self.statusBar().showMessage("Form submitted successfully!", 3000)
    
    def on_form_cleared(self):
        """Handle form clear"""
        print("Form cleared")
        self.statusBar().showMessage("Form cleared", 2000)
    
    def on_form_data_changed(self, data):
        """Handle form data change"""
        # Uncomment to see real-time changes
        # print(f"Form data changed: {data}")
        pass
    
    def on_validation_failed(self, errors):
        """Handle validation failure"""
        print("Validation failed:")
        for field, error in errors.items():
            print(f"  {field}: {error}")
        self.statusBar().showMessage("Validation failed - check form errors", 3000)


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show demo window
    demo = DynamicFormDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
