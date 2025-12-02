"""
Dynamic Form Widget Module
High-level widget that integrates FormBuilder with data binding and form operations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QScrollArea, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any, Optional

from src.models.field_configuration import FieldConfiguration
from .form_builder import FormBuilder


class DynamicFormWidget(QWidget):
    """
    Dynamic form widget that integrates FormBuilder
    Provides form rendering, data binding, validation, and form operations
    """
    
    # Signals
    formSubmitted = pyqtSignal(dict)  # Emitted when form is submitted with valid data
    formCleared = pyqtSignal()  # Emitted when form is cleared
    formDataChanged = pyqtSignal(dict)  # Emitted when any field changes
    validationFailed = pyqtSignal(dict)  # Emitted when validation fails with errors
    
    def __init__(self, field_configs: List[FieldConfiguration] = None, 
                 show_buttons: bool = True, parent=None):
        """
        Initialize dynamic form widget
        
        Args:
            field_configs: List of field configurations
            show_buttons: Whether to show submit/clear buttons
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.form_builder = FormBuilder()
        self._field_configs = field_configs or []
        self._show_buttons = show_buttons
        self._current_data = {}
        
        self._setup_ui()
        
        if field_configs:
            self.load_field_configs(field_configs)
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Create scroll area for form
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Form container (will be populated by FormBuilder)
        self.form_container = QWidget()
        self.scroll_area.setWidget(self.form_container)
        
        main_layout.addWidget(self.scroll_area)
        
        # Buttons
        if self._show_buttons:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.clear_button = QPushButton("Clear")
            self.clear_button.clicked.connect(self.clear_form)
            button_layout.addWidget(self.clear_button)
            
            self.submit_button = QPushButton("Submit")
            self.submit_button.clicked.connect(self.submit_form)
            self.submit_button.setDefault(True)
            button_layout.addWidget(self.submit_button)
            
            main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.hide()
        main_layout.addWidget(self.status_label)
    
    def load_field_configs(self, field_configs: List[FieldConfiguration]):
        """
        Load and render form from field configurations
        
        Args:
            field_configs: List of FieldConfiguration objects
        """
        self._field_configs = field_configs
        
        # Build form
        form_widget = self.form_builder.build_form(field_configs)
        
        # Replace form container
        old_widget = self.scroll_area.takeWidget()
        if old_widget:
            old_widget.deleteLater()
        
        self.form_container = form_widget
        self.scroll_area.setWidget(self.form_container)
        
        # Connect field change signals
        for field_name, widget in self.form_builder.get_all_field_widgets().items():
            widget.valueChanged.connect(
                lambda value, field=field_name: self._on_field_changed(field, value)
            )
    
    def _on_field_changed(self, field_name: str, value: Any):
        """Handle field value change"""
        self._current_data[field_name] = value
        self.formDataChanged.emit(self._current_data.copy())
        
        # Hide status label on change
        self.status_label.hide()
    
    def get_form_data(self) -> Dict[str, Any]:
        """
        Get current form data
        
        Returns:
            Dictionary of field names to values
        """
        return self.form_builder.get_form_data()
    
    def set_form_data(self, data: Dict[str, Any]):
        """
        Set form data
        
        Args:
            data: Dictionary of field names to values
        """
        self.form_builder.set_form_data(data)
        self._current_data = data.copy()
    
    def clear_form(self):
        """Clear all form fields"""
        self.form_builder.clear_form()
        self._current_data.clear()
        self.status_label.hide()
        self.formCleared.emit()
    
    def reset_form(self):
        """Reset form to default values"""
        # Set default values from field configs
        default_data = {}
        for config in self._field_configs:
            if config.default_value:
                default_data[config.field_name] = config.default_value
        
        if default_data:
            self.set_form_data(default_data)
        else:
            self.clear_form()
    
    def validate_form(self, show_errors: bool = True) -> bool:
        """
        Validate the form
        
        Args:
            show_errors: Whether to show error messages
            
        Returns:
            True if form is valid, False otherwise
        """
        is_valid, errors = self.form_builder.validate_form()
        
        if not is_valid:
            self.validationFailed.emit(errors)
            
            if show_errors:
                error_messages = "\n".join([f"• {field}: {msg}" for field, msg in errors.items()])
                self.status_label.setText(f"Validation errors:\n{error_messages}")
                self.status_label.show()
        else:
            self.status_label.hide()
        
        return is_valid
    
    def submit_form(self):
        """Submit the form after validation"""
        if self.validate_form(show_errors=True):
            form_data = self.get_form_data()
            self.formSubmitted.emit(form_data)
            self.status_label.hide()
    
    def get_field_widget(self, field_name: str):
        """
        Get a specific field widget
        
        Args:
            field_name: Name of the field
            
        Returns:
            BaseFieldWidget instance or None
        """
        return self.form_builder.get_field_widget(field_name)
    
    def set_field_value(self, field_name: str, value: Any):
        """
        Set value for a specific field
        
        Args:
            field_name: Name of the field
            value: Value to set
        """
        widget = self.get_field_widget(field_name)
        if widget:
            widget.set_value(value)
    
    def get_field_value(self, field_name: str) -> Any:
        """
        Get value from a specific field
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field value or None
        """
        widget = self.get_field_widget(field_name)
        if widget:
            return widget.get_value()
        return None
    
    def set_field_enabled(self, field_name: str, enabled: bool):
        """
        Enable or disable a specific field
        
        Args:
            field_name: Name of the field
            enabled: True to enable, False to disable
        """
        widget = self.get_field_widget(field_name)
        if widget:
            widget.setEnabled(enabled)
    
    def set_field_visible(self, field_name: str, visible: bool):
        """
        Show or hide a specific field
        
        Args:
            field_name: Name of the field
            visible: True to show, False to hide
        """
        widget = self.get_field_widget(field_name)
        if widget:
            widget.setVisible(visible)
    
    def add_cross_field_validator(self, validator_func):
        """
        Add a cross-field validator
        
        Args:
            validator_func: Function that takes form_data dict and returns 
                          (is_valid, error_message, field_name)
        """
        self.form_builder.add_cross_field_validator(validator_func)
    
    def set_submit_button_text(self, text: str):
        """Set the submit button text"""
        if hasattr(self, 'submit_button'):
            self.submit_button.setText(text)
    
    def set_clear_button_text(self, text: str):
        """Set the clear button text"""
        if hasattr(self, 'clear_button'):
            self.clear_button.setText(text)
    
    def set_buttons_visible(self, visible: bool):
        """Show or hide the form buttons"""
        if hasattr(self, 'submit_button'):
            self.submit_button.setVisible(visible)
        if hasattr(self, 'clear_button'):
            self.clear_button.setVisible(visible)
    
    def is_form_dirty(self) -> bool:
        """
        Check if form has been modified
        
        Returns:
            True if form data differs from initial state
        """
        current_data = self.get_form_data()
        return current_data != self._current_data
    
    def get_field_configs(self) -> List[FieldConfiguration]:
        """Get the current field configurations"""
        return self._field_configs.copy()
    
    def reload_form(self):
        """Reload the form with current field configurations"""
        if self._field_configs:
            current_data = self.get_form_data()
            self.load_field_configs(self._field_configs)
            self.set_form_data(current_data)
