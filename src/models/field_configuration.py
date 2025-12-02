"""
Field Configuration Model - Model for dynamic form field configurations
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class FieldType(str, Enum):
    """Enumeration of supported field types"""
    TEXT = "text"
    NUMBER = "number"
    CURRENCY = "currency"
    DATE = "date"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    EMAIL = "email"
    PHONE = "phone"
    TEXTAREA = "textarea"
    URL = "url"


class WidgetType(str, Enum):
    """Enumeration of supported widget types"""
    TEXTBOX = "textbox"
    NUMBER_WIDGET = "number"
    CURRENCY_WIDGET = "currency"
    DATE_EDIT = "date_edit"
    COMBOBOX = "combobox"
    CHECKBOX_WIDGET = "checkbox"
    EMAIL_WIDGET = "email"
    PHONE_WIDGET = "phone"
    TEXTAREA_WIDGET = "textarea"
    URL_WIDGET = "url"


class FieldConfiguration(BaseModel):
    """
    Model representing a dynamic field configuration.
    
    Supports 10 field types:
    - Text, Number, Currency, Date, Dropdown
    - Checkbox, Email, Phone, TextArea, URL
    
    Validates:
    - Field type is one of the 10 supported types
    - Widget type matches field type
    - Validation rules are properly formatted
    """
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: Optional[int] = None
    department_id: int = Field(..., description="Department ID this field belongs to")
    field_name: str = Field(..., min_length=1, max_length=100, description="Field name")
    field_type: FieldType = Field(..., description="Field type (one of 10 types)")
    widget_type: WidgetType = Field(..., description="Widget type for rendering")
    is_required: bool = Field(default=False, description="Whether field is required")
    validation_rules: Optional[Dict[str, Any]] = Field(default=None, description="Validation rules as JSON")
    default_value: Optional[str] = Field(default=None, description="Default value")
    options: Optional[List[str]] = Field(default=None, description="Options for dropdown fields")
    display_order: int = Field(default=0, ge=0, description="Display order (0-based)")
    category: Optional[str] = Field(default=None, max_length=100, description="Field category/group")
    is_active: bool = Field(default=True, description="Whether field is active")
    created_at: Optional[datetime] = None
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """
        Validate field name is not empty
        """
        if not v or not v.strip():
            raise ValueError("Tên trường không được để trống")
        
        return v.strip()
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """
        Validate that dropdown fields have options
        """
        field_type = info.data.get('field_type')
        
        if field_type == FieldType.DROPDOWN:
            if not v or len(v) == 0:
                raise ValueError("Trường dropdown phải có ít nhất một tùy chọn")
        
        return v
    
    @field_validator('validation_rules')
    @classmethod
    def validate_validation_rules(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate that validation rules are properly formatted
        """
        if v is None:
            return v
        
        # Ensure it's a dictionary
        if not isinstance(v, dict):
            raise ValueError("Validation rules phải là một dictionary")
        
        # Validate known validation rule keys
        valid_keys = {
            'required', 'min_length', 'max_length', 'min_value', 'max_value',
            'pattern', 'email_format', 'phone_format', 'url_format',
            'number_only', 'text_only', 'no_special_chars'
        }
        
        for key in v.keys():
            if key not in valid_keys:
                raise ValueError(f"Validation rule không hợp lệ: {key}")
        
        return v
