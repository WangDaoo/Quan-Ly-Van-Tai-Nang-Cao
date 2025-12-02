"""
Employee Model - Model for managing employee information
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class Employee(BaseModel):
    """
    Model representing an employee with validation rules.
    
    Validates:
    - Required fields (username, full_name)
    - Email format (RFC 5322)
    - Phone number format
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=100, description="Unique username")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: Optional[str] = Field(default=None, description="Email address (validated)")
    phone: Optional[str] = Field(default=None, description="Phone number")
    department_id: Optional[int] = Field(default=None, description="Department ID")
    is_active: bool = Field(default=True, description="Whether employee is active")
    created_at: Optional[datetime] = None
    
    @field_validator('username', 'full_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Validate that required string fields are not empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Trường này không được để trống")
        
        return v.strip()
    
    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """
        Validate username format (alphanumeric, underscore, hyphen only)
        """
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                "Username chỉ được chứa chữ cái, số, dấu gạch dưới và dấu gạch ngang"
            )
        
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate email format (RFC 5322 simplified)
        """
        if v is None or v == "":
            return v
        
        # Simple email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, v):
            raise ValueError(
                "Email không hợp lệ. Định dạng: example@domain.com"
            )
        
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate phone number format (Vietnamese phone numbers)
        Accepts formats: 0123456789, +84123456789, 84123456789
        """
        if v is None or v == "":
            return v
        
        # Remove spaces and common separators
        cleaned = re.sub(r'[\s\-\.\(\)]', '', v)
        
        # Vietnamese phone number patterns
        patterns = [
            r'^0\d{9,10}$',           # 0123456789 or 01234567890
            r'^\+84\d{9,10}$',        # +84123456789
            r'^84\d{9,10}$',          # 84123456789
        ]
        
        if not any(re.match(pattern, cleaned) for pattern in patterns):
            raise ValueError(
                "Số điện thoại không hợp lệ. Định dạng: 0123456789, +84123456789, hoặc 84123456789"
            )
        
        return cleaned
