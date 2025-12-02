"""
Form Builder Module
Dynamically creates forms from field configurations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QGroupBox, QLabel, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any, Optional
import json

from src.models.field_configuration import FieldConfiguration
from .field_widgets import (
    BaseFieldWidget, TextboxWidget, NumberWidget, CurrencyWidget,
    DateEditWidget, ComboboxWidget, CheckboxWidget, EmailWidget,
    PhoneWidget, TextAreaWidget, URLWidget
)
from .form_validator import FormValidator, ValidationRuleBuilder


class WidgetFactory:
    """Factory class to create appropriate widgets based on field configuration"""
    
    @staticmethod
    def create_widget(field_config: FieldConfiguration) -> BaseFieldWidget:
        """
        Create a widget based on field configuration
        
        Args:
            field_config: FieldConfiguration object
            
        Returns:
            BaseFieldWidget instance
        """
        widget_type = field_config.widget_type.lower()
        
        # Parse options if available
        options = []
        if field_config.options:
            if isinstance(field_config.options, str):
                try:
                    options = json.loads(field_config.options)
                except json.JSONDecodeError:
                    options = field_config.options.split(',')
            elif isinstance(field_config.options, list):
                options = field_config.options
        
        # Parse validation rules
        validation_rules = {}
        if field_config.validation_rules:
            if isinstance(field_config.validation_rules, str):
                try:
                    validation_rules = json.loads(field_config.validation_rules)
                except json.JSONDecodeError:
                    validation_rules = {}
            elif isinstance(field_config.validation_rules, dict):
                validation_rules = field_config.validation_rules
        
        # Create widget based on type
        if widget_type in ('text', 'textbox'):
            max_length = validation_rules.get('max_length', 255)
            placeholder = validation_rules.get('placeholder', '')
            return TextboxWidget(placeholder=placeholder, max_length=max_length)
        
        elif widget_type in ('number', 'number_widget'):
            min_value = validation_rules.get('min_value', 0)
            max_value = validation_rules.get('max_value', 999999999)
            step = validation_rules.get('step', 1)
            decimals = validation_rules.get('decimals', 0)
            return NumberWidget(min_value=min_value, max_value=max_value, 
                              step=step, decimals=decimals)
        
        elif widget_type in ('currency', 'currency_widget'):
            currency_symbol = validation_rules.get('currency_symbol', 'VND')
            return CurrencyWidget(currency_symbol=currency_symbol)
        
        elif widget_type in ('date', 'date_edit'):
            return DateEditWidget()
        
        elif widget_type in ('dropdown', 'combobox'):
            editable = validation_rules.get('editable', True)
            return ComboboxWidget(options=options, editable=editable)
        
        elif widget_type in ('checkbox', 'checkbox_widget'):
            label = validation_rules.get('label', '')
            return CheckboxWidget(label=label)
        
        elif widget_type in ('email', 'email_widget'):
            placeholder = validation_rules.get('placeholder', 'email@example.com')
            return EmailWidget(placeholder=placeholder)
        
        elif widget_type in ('phone', 'phone_widget'):
            placeholder = validation_rules.get('placeholder', '0123456789')
            return PhoneWidget(placeholder=placeholder)
        
        elif widget_type in ('textarea', 'textarea_widget'):
            placeholder = validation_rules.get('placeholder', '')
            max_length = validation_rules.get('max_length', 1000)
            return TextAreaWidget(placeholder=placeholder, max_length=max_length)
        
        elif widget_type in ('url', 'url_widget'):
            placeholder = validation_rules.get('placeholder', 'https://example.com')
            return URLWidget(placeholder=placeholder)
        
        else:
            # Default to textbox
            return TextboxWidget()


class FormBuilder:
    """
    Builds dynamic forms from field configurations
    Handles grouping, layout, validation, and signal connections
    """
    
    def __init__(self):
        self.widget_factory = WidgetFactory()
        self.form_validator = FormValidator()
        self._field_widgets: Dict[str, BaseFieldWidget] = {}
        self._field_configs: List[FieldConfiguration] = []
    
    def build_form(self, field_configs: List[FieldConfiguration], 
                   parent: Optional[QWidget] = None) -> QWidget:
        """
        Build a form from field configurations
        
        Args:
            field_configs: List of FieldConfiguration objects
            parent: Parent widget
            
        Returns:
            QWidget containing the form
        """
        self._field_configs = field_configs
        self._field_widgets.clear()
        self.form_validator = FormValidator()
        
        # Sort by display_order
        sorted_configs = sorted(field_configs, key=lambda x: x.display_order)
        
        # Group by category
        grouped_configs = self._group_by_category(sorted_configs)
        
        # Create main widget
        main_widget = QWidget(parent)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create form for each category
        for category, configs in grouped_configs.items():
            group_widget = self._create_category_group(category, configs)
            main_layout.addWidget(group_widget)
        
        main_layout.addStretch()
        
        return main_widget
    
    def _group_by_category(self, configs: List[FieldConfiguration]) -> Dict[str, List[FieldConfiguration]]:
        """Group field configurations by category"""
        grouped = {}
        
        for config in configs:
            if not config.is_active:
                continue
            
            category = config.category or "General"
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(config)
        
        return grouped
    
    def _create_category_group(self, category: str, 
                               configs: List[FieldConfiguration]) -> QWidget:
        """Create a group box for a category"""
        group_box = QGroupBox(category)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        for config in configs:
            # Create widget
            widget = self.widget_factory.create_widget(config)
            self._field_widgets[config.field_name] = widget
            
            # Set default value
            if config.default_value:
                widget.set_value(config.default_value)
            
            # Setup validation
            self._setup_validation(config, widget)
            
            # Connect signals
            widget.valueChanged.connect(
                lambda value, field=config.field_name: self._on_field_changed(field, value)
            )
            widget.validationChanged.connect(
                lambda is_valid, field=config.field_name: self._on_validation_changed(field, is_valid)
            )
            
            # Create label
            label_text = config.field_name
            if config.is_required:
                label_text += " *"
            label = QLabel(label_text)
            
            # Add to form
            form_layout.addRow(label, widget)
        
        group_box.setLayout(form_layout)
        return group_box
    
    def _setup_validation(self, config: FieldConfiguration, widget: BaseFieldWidget):
        """Setup validation for a field"""
        # Parse validation rules
        validation_rules = {}
        if config.validation_rules:
            if isinstance(config.validation_rules, str):
                try:
                    validation_rules = json.loads(config.validation_rules)
                except json.JSONDecodeError:
                    validation_rules = {}
            elif isinstance(config.validation_rules, dict):
                validation_rules = config.validation_rules
        
        # Add required flag
        validation_rules['required'] = config.is_required
        
        # Build validators
        validators = ValidationRuleBuilder.build_from_config(validation_rules)
        
        # Add validators to form validator
        for validator in validators:
            self.form_validator.add_validator(config.field_name, validator)
    
    def _on_field_changed(self, field_name: str, value: Any):
        """Handle field value change"""
        # Validate field
        is_valid, error_message = self.form_validator.validate_field(field_name, value)
        
        # Update widget visual state
        if field_name in self._field_widgets:
            widget = self._field_widgets[field_name]
            widget.set_error_state(is_valid, error_message)
    
    def _on_validation_changed(self, field_name: str, is_valid: bool):
        """Handle validation state change"""
        pass  # Can be used for additional logic
    
    def get_field_widget(self, field_name: str) -> Optional[BaseFieldWidget]:
        """Get a field widget by name"""
        return self._field_widgets.get(field_name)
    
    def get_all_field_widgets(self) -> Dict[str, BaseFieldWidget]:
        """Get all field widgets"""
        return self._field_widgets.copy()
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get all form data as a dictionary"""
        form_data = {}
        for field_name, widget in self._field_widgets.items():
            form_data[field_name] = widget.get_value()
        return form_data
    
    def set_form_data(self, data: Dict[str, Any]):
        """Set form data from a dictionary"""
        for field_name, value in data.items():
            if field_name in self._field_widgets:
                self._field_widgets[field_name].set_value(value)
    
    def clear_form(self):
        """Clear all form fields"""
        for widget in self._field_widgets.values():
            widget.clear()
    
    def validate_form(self) -> tuple[bool, Dict[str, str]]:
        """
        Validate the entire form
        Returns: (is_valid, error_dict)
        """
        form_data = self.get_form_data()
        is_valid, errors = self.form_validator.validate_form(form_data)
        
        # Update visual state for all fields
        for field_name, widget in self._field_widgets.items():
            if field_name in errors:
                widget.set_error_state(False, errors[field_name])
            else:
                widget.set_error_state(True, "")
        
        return is_valid, errors
    
    def add_cross_field_validator(self, validator_func):
        """Add a cross-field validator"""
        self.form_validator.add_cross_field_validator(validator_func)
    
    def connect_formula_engine(self, formula_engine):
        """
        Connect formula engine to automatically calculate fields
        
        Args:
            formula_engine: FormulaEngine instance
        """
        # This will be implemented when integrating with formula engine
        pass
