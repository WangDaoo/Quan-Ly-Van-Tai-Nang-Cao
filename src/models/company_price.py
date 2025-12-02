"""
Company Price Model - Model for managing company pricing information
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CompanyPrice(BaseModel):
    """
    Model representing pricing information from different companies.
    
    Validates:
    - Required fields (company name, customer, locations, price)
    - Numeric fields (price, salary)
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    company_name: str = Field(..., min_length=1, description="Company name (required)")
    khach_hang: str = Field(..., min_length=1, description="Customer name (required)")
    diem_di: str = Field(..., min_length=1, description="Departure location (required)")
    diem_den: str = Field(..., min_length=1, description="Destination location (required)")
    gia_ca: int = Field(..., ge=0, description="Price (required, must be >= 0)")
    khoan_luong: int = Field(..., ge=0, description="Salary amount (required, must be >= 0)")
    created_at: Optional[datetime] = None
    
    @field_validator('company_name', 'khach_hang', 'diem_di', 'diem_den')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Validate that string fields are not empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Trường này không được để trống")
        
        return v.strip()
    
    @field_validator('gia_ca', 'khoan_luong')
    @classmethod
    def validate_positive_amount(cls, v: int) -> int:
        """
        Validate that monetary amounts are non-negative
        """
        if v < 0:
            raise ValueError("Số tiền không được âm")
        
        return v
