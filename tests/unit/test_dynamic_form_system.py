"""
Unit tests for Dynamic Form System
Tests field widgets, validators, form builder, and dynamic form widget
"""

import pytest
from src.models.field_configuration import FieldConfiguration
from src.gui.widgets import (
    TextboxWidget, NumberWidget, CurrencyWidget, DateEditWidget,
    ComboboxWidget, CheckboxWidget, EmailWidget, PhoneWidget,
    TextAreaWidget, URLWidget,
    RequiredValidator, NumberOnlyValidator, TextOnlyValidator,
    NoSpecialCharsValidator, EmailFormatValidator, PatternMatchingValidator,
    FormValidator, ValidationRuleBuilder, WidgetFactory, FormBuilder
)


class TestFieldWidgets:
    """Test all 10 field widget types"""
    
    def test_textbox_widget(self):
        """Test TextboxWidget"""
        widget = TextboxWidget(placeholder="Test", max_length=10)
        widget.set_value("Hello")
        assert widget.get_value() == "Hello"
        widget.clear()
        assert widget.get_value() == ""
    
    def test_number_widget(self):
        """Test NumberWidget"""
        widget = NumberWidget(min_value=0, max_value=100, step=5)
        widget.set_value(50)
        assert widget.get_value() == 50
        widget.clear()
        assert widget.get_value() == 0
    
    def test_currency_widget(self):
        """Test CurrencyWidget"""
        widget = CurrencyWidget(currency_symbol="VND")
        widget.set_value(1000000)
        assert widget.get_value() == 1000000
        widget.clear()
        assert widget.get_value() == 0
    
    def test_date_edit_widget(self):
        """Test DateEditWidget"""
        widget = DateEditWidget()
        widget.set_value("2024-01-15")
        assert widget.get_value() == "2024-01-15"
    
    def test_combobox_widget(self):
        """Test ComboboxWidget"""
        options = ["Option 1", "Option 2", "Option 3"]
        widget = ComboboxWidget(options=options, editable=True)
        widget.set_value("Option 2")
        assert widget.get_value() == "Option 2"
        widget.clear()
        assert widget.get_value() == ""
    
    def test_checkbox_widget(self):
        """Test CheckboxWidget"""
        widget = CheckboxWidget(label="Test")
        widget.set_value(True)
        assert widget.get_value() is True
        widget.clear()
        assert widget.get_value() is False
    
    def test_email_widget(self):
        """Test EmailWidget"""
        widget = EmailWidget()
        widget.set_value("test@example.com")
        assert widget.get_value() == "test@example.com"
        assert widget.is_valid() is True
        
        widget.set_value("invalid-email")
        assert widget.is_valid() is False
    
    def test_phone_widget(self):
        """Test PhoneWidget"""
        widget = PhoneWidget()
        widget.set_value("0123456789")
        assert widget.get_value() == "0123456789"
        assert widget.is_valid() is True
        
        widget.set_value("123")
        assert widget.is_valid() is False
    
    def test_textarea_widget(self):
        """Test TextAreaWidget"""
        widget = TextAreaWidget(max_length=100)
        widget.set_value("This is a test")
        assert widget.get_value() == "This is a test"
        widget.clear()
        assert widget.get_value() == ""
    
    def test_url_widget(self):
        """Test URLWidget"""
        widget = URLWidget()
        widget.set_value("https://example.com")
        assert widget.get_value() == "https://example.com"
        assert widget.is_valid() is True
        
        widget.set_value("not-a-url")
        assert widget.is_valid() is False


class TestValidators:
    """Test all 6 validator types"""
    
    def test_required_validator(self):
        """Test RequiredValidator"""
        validator = RequiredValidator()
        
        is_valid, msg = validator.validate("test")
        assert is_valid is True
        
        is_valid, msg = validator.validate("")
        assert is_valid is False
        
        is_valid, msg = validator.validate(None)
        assert is_valid is False
    
    def test_number_only_validator(self):
        """Test NumberOnlyValidator"""
        validator = NumberOnlyValidator(allow_decimals=False)
        
        is_valid, msg = validator.validate("123")
        assert is_valid is True
        
        is_valid, msg = validator.validate("abc")
        assert is_valid is False
        
        # Test with decimals
        validator_decimal = NumberOnlyValidator(allow_decimals=True)
        is_valid, msg = validator_decimal.validate("123.45")
        assert is_valid is True
    
    def test_text_only_validator(self):
        """Test TextOnlyValidator"""
        validator = TextOnlyValidator(allow_spaces=True)
        
        is_valid, msg = validator.validate("Hello World")
        assert is_valid is True
        
        is_valid, msg = validator.validate("Hello123")
        assert is_valid is False
    
    def test_no_special_chars_validator(self):
        """Test NoSpecialCharsValidator"""
        validator = NoSpecialCharsValidator(allowed_chars="-_")
        
        is_valid, msg = validator.validate("test_name-123")
        assert is_valid is True
        
        is_valid, msg = validator.validate("test@name")
        assert is_valid is False
    
    def test_email_format_validator(self):
        """Test EmailFormatValidator"""
        validator = EmailFormatValidator()
        
        is_valid, msg = validator.validate("test@example.com")
        assert is_valid is True
        
        is_valid, msg = validator.validate("invalid-email")
        assert is_valid is False
    
    def test_pattern_matching_validator(self):
        """Test PatternMatchingValidator"""
        validator = PatternMatchingValidator(r'^\d{3}-\d{4}$')
        
        is_valid, msg = validator.validate("123-4567")
        assert is_valid is True
        
        is_valid, msg = validator.validate("123-456")
        assert is_valid is False


class TestFormValidator:
    """Test FormValidator class"""
    
    def test_add_and_validate_field(self):
        """Test adding validators and validating fields"""
        form_validator = FormValidator()
        
        # Add required validator
        form_validator.add_validator("name", RequiredValidator())
        
        # Validate with value
        is_valid, msg = form_validator.validate_field("name", "John")
        assert is_valid is True
        
        # Validate without value
        is_valid, msg = form_validator.validate_field("name", "")
        assert is_valid is False
    
    def test_validate_form(self):
        """Test validating entire form"""
        form_validator = FormValidator()
        
        form_validator.add_validator("name", RequiredValidator())
        form_validator.add_validator("age", NumberOnlyValidator())
        
        # Valid form data
        form_data = {"name": "John", "age": "25"}
        is_valid, errors = form_validator.validate_form(form_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid form data
        form_data = {"name": "", "age": "abc"}
        is_valid, errors = form_validator.validate_form(form_data)
        assert is_valid is False
        assert "name" in errors
        assert "age" in errors


class TestValidationRuleBuilder:
    """Test ValidationRuleBuilder"""
    
    def test_build_from_config(self):
        """Test building validators from configuration"""
        config = {
            "required": True,
            "type": "number",
            "no_special_chars": True
        }
        
        validators = ValidationRuleBuilder.build_from_config(config)
        
        assert len(validators) >= 2
        assert any(isinstance(v, RequiredValidator) for v in validators)
        assert any(isinstance(v, NumberOnlyValidator) for v in validators)


class TestWidgetFactory:
    """Test WidgetFactory"""
    
    def test_create_textbox_widget(self):
        """Test creating textbox widget from config"""
        config = FieldConfiguration(
            department_id=1,
            field_name="Test",
            field_type="text",
            widget_type="textbox",
            validation_rules={"max_length": 50}
        )
        
        widget = WidgetFactory.create_widget(config)
        assert isinstance(widget, TextboxWidget)
    
    def test_create_number_widget(self):
        """Test creating number widget from config"""
        config = FieldConfiguration(
            department_id=1,
            field_name="Age",
            field_type="number",
            widget_type="number",
            validation_rules={"min_value": 0, "max_value": 100}
        )
        
        widget = WidgetFactory.create_widget(config)
        assert isinstance(widget, NumberWidget)
    
    def test_create_combobox_widget(self):
        """Test creating combobox widget from config"""
        config = FieldConfiguration(
            department_id=1,
            field_name="City",
            field_type="dropdown",
            widget_type="combobox",
            options=["Hanoi", "HCMC", "Danang"]
        )
        
        widget = WidgetFactory.create_widget(config)
        assert isinstance(widget, ComboboxWidget)


class TestFormBuilder:
    """Test FormBuilder"""
    
    def test_build_form(self):
        """Test building form from field configurations"""
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                is_required=True,
                display_order=1,
                category="Basic"
            ),
            FieldConfiguration(
                department_id=1,
                field_name="Age",
                field_type="number",
                widget_type="number",
                is_required=False,
                display_order=2,
                category="Basic"
            )
        ]
        
        form_builder = FormBuilder()
        form_widget = form_builder.build_form(configs)
        
        assert form_widget is not None
        assert len(form_builder.get_all_field_widgets()) == 2
        assert "Name" in form_builder.get_all_field_widgets()
        assert "Age" in form_builder.get_all_field_widgets()
    
    def test_get_and_set_form_data(self):
        """Test getting and setting form data"""
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        form_builder = FormBuilder()
        form_builder.build_form(configs)
        
        # Set data
        form_builder.set_form_data({"Name": "John"})
        
        # Get data
        data = form_builder.get_form_data()
        assert data["Name"] == "John"
    
    def test_validate_form(self):
        """Test form validation"""
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                is_required=True,
                display_order=1
            )
        ]
        
        form_builder = FormBuilder()
        form_builder.build_form(configs)
        
        # Set empty value
        form_builder.set_form_data({"Name": ""})
        
        # Validate
        is_valid, errors = form_builder.validate_form()
        assert is_valid is False
        assert "Name" in errors


class TestDynamicFormWidget:
    """Test DynamicFormWidget integration"""
    
    def test_create_dynamic_form_widget(self, qtbot):
        """Test creating DynamicFormWidget"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                is_required=True,
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs, show_buttons=True)
        qtbot.addWidget(widget)
        assert widget is not None
        assert len(widget.get_field_configs()) == 1
    
    def test_form_rendering(self, qtbot):
        """Test form rendering with proper layout"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Field1",
                field_type="text",
                widget_type="textbox",
                display_order=1,
                category="Category1"
            ),
            FieldConfiguration(
                department_id=1,
                field_name="Field2",
                field_type="number",
                widget_type="number",
                display_order=2,
                category="Category1"
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Check that form container exists
        assert widget.form_container is not None
        assert widget.scroll_area is not None
        
        # Check that fields are accessible
        assert widget.get_field_widget("Field1") is not None
        assert widget.get_field_widget("Field2") is not None
    
    def test_form_data_binding(self, qtbot):
        """Test form data binding (get/set)"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            ),
            FieldConfiguration(
                department_id=1,
                field_name="Age",
                field_type="number",
                widget_type="number",
                display_order=2
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set form data
        test_data = {"Name": "John Doe", "Age": 30}
        widget.set_form_data(test_data)
        
        # Get form data
        retrieved_data = widget.get_form_data()
        assert retrieved_data["Name"] == "John Doe"
        assert retrieved_data["Age"] == 30
    
    def test_form_reset_functionality(self, qtbot):
        """Test form reset functionality"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                default_value="Default Name",
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set some data
        widget.set_form_data({"Name": "Changed Name"})
        assert widget.get_form_data()["Name"] == "Changed Name"
        
        # Reset form
        widget.reset_form()
        
        # Should return to default value
        assert widget.get_form_data()["Name"] == "Default Name"
    
    def test_form_clear_functionality(self, qtbot):
        """Test form clear functionality"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            ),
            FieldConfiguration(
                department_id=1,
                field_name="Age",
                field_type="number",
                widget_type="number",
                display_order=2
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set some data
        widget.set_form_data({"Name": "John", "Age": 30})
        
        # Clear form
        widget.clear_form()
        
        # Check that form is cleared
        data = widget.get_form_data()
        assert data["Name"] == ""
        assert data["Age"] == 0
    
    def test_form_validation(self, qtbot):
        """Test form validation"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                is_required=True,
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set empty value (should fail validation)
        widget.set_form_data({"Name": ""})
        assert widget.validate_form(show_errors=False) is False
        
        # Set valid value
        widget.set_form_data({"Name": "John"})
        assert widget.validate_form(show_errors=False) is True
    
    def test_individual_field_operations(self, qtbot):
        """Test individual field get/set operations"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set individual field value
        widget.set_field_value("Name", "Test Name")
        
        # Get individual field value
        value = widget.get_field_value("Name")
        assert value == "Test Name"
    
    def test_field_visibility_control(self, qtbot):
        """Test field visibility control"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        widget.show()
        
        field_widget = widget.get_field_widget("Name")
        
        # Initially visible
        assert field_widget.isVisible() is True
        
        # Hide field
        widget.set_field_visible("Name", False)
        assert field_widget.isVisible() is False
        
        # Show field
        widget.set_field_visible("Name", True)
        assert field_widget.isVisible() is True
    
    def test_field_enabled_control(self, qtbot):
        """Test field enabled/disabled control"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Disable field
        widget.set_field_enabled("Name", False)
        field_widget = widget.get_field_widget("Name")
        assert field_widget.isEnabled() is False
        
        # Enable field
        widget.set_field_enabled("Name", True)
        assert field_widget.isEnabled() is True
    
    def test_button_visibility(self, qtbot):
        """Test button visibility control"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        # Create with buttons
        widget = DynamicFormWidget(field_configs=configs, show_buttons=True)
        qtbot.addWidget(widget)
        widget.show()
        
        assert hasattr(widget, 'submit_button')
        assert hasattr(widget, 'clear_button')
        
        # Initially visible
        assert widget.submit_button.isVisible() is True
        assert widget.clear_button.isVisible() is True
        
        # Hide buttons
        widget.set_buttons_visible(False)
        assert widget.submit_button.isVisible() is False
        assert widget.clear_button.isVisible() is False
        
        # Show buttons
        widget.set_buttons_visible(True)
        assert widget.submit_button.isVisible() is True
        assert widget.clear_button.isVisible() is True
    
    def test_form_reload(self, qtbot):
        """Test form reload functionality"""
        from src.gui.widgets import DynamicFormWidget
        
        configs = [
            FieldConfiguration(
                department_id=1,
                field_name="Name",
                field_type="text",
                widget_type="textbox",
                display_order=1
            )
        ]
        
        widget = DynamicFormWidget(field_configs=configs)
        qtbot.addWidget(widget)
        
        # Set data
        widget.set_form_data({"Name": "Test"})
        
        # Reload form
        widget.reload_form()
        
        # Data should be preserved
        assert widget.get_form_data()["Name"] == "Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
