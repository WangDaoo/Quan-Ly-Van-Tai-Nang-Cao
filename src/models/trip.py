"""
Trip Model - Core model for managing transportation trips
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class Trip(BaseModel):
    """
    Model representing a transportation trip with validation rules.
    
    Validates:
    - Trip code format (C001, C002, etc.)
    - Required fields (customer, price)
    - Numeric fields (price, salary, other costs)
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    ma_chuyen: str = Field(..., description="Trip code in format C001, C002, etc.")
    khach_hang: str = Field(..., min_length=1, description="Customer name (required)")
    diem_di: Optional[str] = Field(default="", description="Departure location")
    diem_den: Optional[str] = Field(default="", description="Destination location")
    gia_ca: int = Field(..., ge=0, description="Price (required, must be >= 0)")
    khoan_luong: int = Field(default=0, ge=0, description="Salary amount (must be >= 0)")
    chi_phi_khac: int = Field(default=0, ge=0, description="Other costs (must be >= 0)")
    ghi_chu: Optional[str] = Field(default="", description="Notes")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('ma_chuyen')
    @classmethod
    def validate_ma_chuyen(cls, v: str) -> str:
        """
        Validate trip code format: C followed by digits (C001, C002, etc.)
        """
        if not v:
            raise ValueError("Mã chuyến không được để trống")
        
        pattern = r'^C\d+$'
        if not re.match(pattern, v):
            raise ValueError(
                "Mã chuyến phải có định dạng C theo sau bởi số (ví dụ: C001, C002)"
            )
        
        return v
    
    @field_validator('khach_hang')
    @classmethod
    def validate_khach_hang(cls, v: str) -> str:
        """
        Validate customer name is not empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Tên khách hàng không được để trống")
        
        return v.strip()
    
    @field_validator('gia_ca', 'khoan_luong', 'chi_phi_khac')
    @classmethod
    def validate_positive_amount(cls, v: int) -> int:
        """
        Validate that monetary amounts are non-negative
        """
        if v < 0:
            raise ValueError("Số tiền không được âm")
        
        return v
