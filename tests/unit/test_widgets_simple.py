"""
Simple tests for Dynamic Form System without pytest
"""

from src.models.field_configuration import FieldConfiguration
from src.gui.widgets import (
    TextboxWidget, NumberWidget, CurrencyWidget,
    RequiredValidator, NumberOnlyValidator, EmailFormatValidator,
    FormValidator, ValidationRuleBuilder, WidgetFactory, FormBuilder
)


def test_textbox_widget():
    """Test TextboxWidget"""
    print("Testing TextboxWidget...")
    widget = TextboxWidget(placeholder="Test", max_length=10)
    widget.set_value("Hello")
    assert widget.get_value() == "Hello", "TextboxWidget get_value failed"
    widget.clear()
    assert widget.get_value() == "", "TextboxWidget clear failed"
    print("✓ TextboxWidget passed")


def test_number_widget():
    """Test NumberWidget"""
    print("Testing NumberWidget...")
    widget = NumberWidget(min_value=0, max_value=100, step=5)
    widget.set_value(50)
    assert widget.get_value() == 50, "NumberWidget get_value failed"
    widget.clear()
    assert widget.get_value() == 0, "NumberWidget clear failed"
    print("✓ NumberWidget passed")


def test_currency_widget():
    """Test CurrencyWidget"""
    print("Testing CurrencyWidget...")
    widget = CurrencyWidget(currency_symbol="VND")
    widget.set_value(1000000)
    assert widget.get_value() == 1000000, "CurrencyWidget get_value failed"
    widget.clear()
    assert widget.get_value() == 0, "CurrencyWidget clear failed"
    print("✓ CurrencyWidget passed")


def test_required_validator():
    """Test RequiredValidator"""
    print("Testing RequiredValidator...")
    validator = RequiredValidator()
    
    is_valid, msg = validator.validate("test")
    assert is_valid is True, "RequiredValidator should accept non-empty value"
    
    is_valid, msg = validator.validate("")
    assert is_valid is False, "RequiredValidator should reject empty value"
    
    is_valid, msg = validator.validate(None)
    assert is_valid is False, "RequiredValidator should reject None"
    print("✓ RequiredValidator passed")


def test_number_only_validator():
    """Test NumberOnlyValidator"""
    print("Testing NumberOnlyValidator...")
    validator = NumberOnlyValidator(allow_decimals=False)
    
    is_valid, msg = validator.validate("123")
    assert is_valid is True, "NumberOnlyValidator should accept numbers"
    
    is_valid, msg = validator.validate("abc")
    assert is_valid is False, "NumberOnlyValidator should reject text"
    
    # Test with decimals
    validator_decimal = NumberOnlyValidator(allow_decimals=True)
    is_valid, msg = validator_decimal.validate("123.45")
    assert is_valid is True, "NumberOnlyValidator should accept decimals when allowed"
    print("✓ NumberOnlyValidator passed")


def test_email_format_validator():
    """Test EmailFormatValidator"""
    print("Testing EmailFormatValidator...")
    validator = EmailFormatValidator()
    
    is_valid, msg = validator.validate("test@example.com")
    assert is_valid is True, "EmailFormatValidator should accept valid email"
    
    is_valid, msg = validator.validate("invalid-email")
    assert is_valid is False, "EmailFormatValidator should reject invalid email"
    print("✓ EmailFormatValidator passed")


def test_form_validator():
    """Test FormValidator"""
    print("Testing FormValidator...")
    form_validator = FormValidator()
    
    # Add required validator
    form_validator.add_validator("name", RequiredValidator())
    
    # Validate with value
    is_valid, msg = form_validator.validate_field("name", "John")
    assert is_valid is True, "FormValidator should accept valid value"
    
    # Validate without value
    is_valid, msg = form_validator.validate_field("name", "")
    assert is_valid is False, "FormValidator should reject empty required field"
    print("✓ FormValidator passed")


def test_validation_rule_builder():
    """Test ValidationRuleBuilder"""
    print("Testing ValidationRuleBuilder...")
    config = {
        "required": True,
        "type": "number",
        "no_special_chars": True
    }
    
    validators = ValidationRuleBuilder.build_from_config(config)
    
    assert len(validators) >= 2, "ValidationRuleBuilder should create multiple validators"
    assert any(isinstance(v, RequiredValidator) for v in validators), "Should include RequiredValidator"
    assert any(isinstance(v, NumberOnlyValidator) for v in validators), "Should include NumberOnlyValidator"
    print("✓ ValidationRuleBuilder passed")


def test_widget_factory():
    """Test WidgetFactory"""
    print("Testing WidgetFactory...")
    config = FieldConfiguration(
        department_id=1,
        field_name="Test",
        field_type="text",
        widget_type="textbox",
        validation_rules={"max_length": 50}
    )
    
    widget = WidgetFactory.create_widget(config)
    assert isinstance(widget, TextboxWidget), "WidgetFactory should create TextboxWidget"
    print("✓ WidgetFactory passed")


def test_form_builder():
    """Test FormBuilder"""
    print("Testing FormBuilder...")
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
    
    assert form_widget is not None, "FormBuilder should create form widget"
    assert len(form_builder.get_all_field_widgets()) == 2, "FormBuilder should create 2 widgets"
    assert "Name" in form_builder.get_all_field_widgets(), "FormBuilder should include Name field"
    assert "Age" in form_builder.get_all_field_widgets(), "FormBuilder should include Age field"
    
    # Test get and set form data
    form_builder.set_form_data({"Name": "John", "Age": 25})
    data = form_builder.get_form_data()
    assert data["Name"] == "John", "FormBuilder should set and get Name correctly"
    assert data["Age"] == 25, "FormBuilder should set and get Age correctly"
    
    print("✓ FormBuilder passed")


def main():
    """Run all tests"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Create QApplication for widgets
    app = QApplication(sys.argv)
    
    print("\n" + "="*60)
    print("Running Dynamic Form System Tests")
    print("="*60 + "\n")
    
    try:
        test_textbox_widget()
        test_number_widget()
        test_currency_widget()
        test_required_validator()
        test_number_only_validator()
        test_email_format_validator()
        test_form_validator()
        test_validation_rule_builder()
        test_widget_factory()
        test_form_builder()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
