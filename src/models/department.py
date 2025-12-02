"""
Department Model - Model for managing organizational departments
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Department(BaseModel):
    """
    Model representing an organizational department.
    
    Validates:
    - Required fields (name, display_name)
    - Unique name constraint
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100, description="Department unique name")
    display_name: str = Field(..., min_length=1, max_length=255, description="Department display name")
    description: Optional[str] = Field(default=None, description="Department description")
    is_active: bool = Field(default=True, description="Whether department is active")
    created_at: Optional[datetime] = None
    
    @field_validator('name', 'display_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Validate that name fields are not empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Tên phòng ban không được để trống")
        
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """
        Validate department name format (alphanumeric and underscores only)
        """
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                "Tên phòng ban chỉ được chứa chữ cái, số và dấu gạch dưới"
            )
        
        return v
