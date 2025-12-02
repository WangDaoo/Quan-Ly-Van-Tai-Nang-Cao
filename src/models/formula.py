"""
Formula Model - Model for formula expressions with validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class Formula(BaseModel):
    """
    Model representing a formula for automatic calculations.
    
    Supports:
    - 4 arithmetic operators: +, -, *, /
    - Parentheses for grouping
    - Field references in [Field_Name] format
    
    Validates:
    - Formula expression syntax
    - Field references format
    - Operator usage
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    department_id: int = Field(..., description="Department ID this formula belongs to")
    target_field: str = Field(..., min_length=1, max_length=100, description="Target field for result")
    formula_expression: str = Field(..., min_length=1, description="Formula expression")
    description: Optional[str] = Field(default=None, description="Formula description")
    is_active: bool = Field(default=True, description="Whether formula is active")
    created_at: Optional[datetime] = None
    
    @field_validator('target_field')
    @classmethod
    def validate_target_field(cls, v: str) -> str:
        """
        Validate target field name is not empty
        """
        if not v or not v.strip():
            raise ValueError("Tên trường đích không được để trống")
        
        return v.strip()
    
    @field_validator('formula_expression')
    @classmethod
    def validate_formula_expression(cls, v: str) -> str:
        """
        Validate formula expression syntax:
        - Contains only allowed characters: digits, operators (+, -, *, /), parentheses, field references
        - Field references are in [Field_Name] format
        - Parentheses are balanced
        - No invalid operator sequences
        """
        if not v or not v.strip():
            raise ValueError("Biểu thức công thức không được để trống")
        
        v = v.strip()
        
        # Check for balanced parentheses
        if not cls._check_balanced_parentheses(v):
            raise ValueError("Dấu ngoặc đơn không cân bằng trong công thức")
        
        # Check for valid characters (digits, operators, spaces, brackets, parentheses)
        # Allow: numbers, +, -, *, /, (, ), [, ], spaces, letters (for field names)
        if not re.match(r'^[\d\+\-\*/\(\)\[\]\s\w]+$', v):
            raise ValueError(
                "Công thức chứa ký tự không hợp lệ. "
                "Chỉ cho phép: số, +, -, *, /, (, ), và [Tên_Trường]"
            )
        
        # Check field references format [Field_Name]
        field_refs = re.findall(r'\[([^\]]+)\]', v)
        for field_ref in field_refs:
            if not field_ref.strip():
                raise ValueError("Tham chiếu trường không được để trống: []")
        
        # Check for invalid operator sequences (e.g., ++, --, */, etc.)
        if re.search(r'[\+\-\*/]{2,}', v.replace('**', '')):
            raise ValueError("Công thức chứa chuỗi toán tử không hợp lệ")
        
        # Check that formula doesn't start or end with an operator
        if re.match(r'^[\+\-\*/]', v.strip()) or re.search(r'[\+\-\*/]$', v.strip()):
            raise ValueError("Công thức không được bắt đầu hoặc kết thúc bằng toán tử")
        
        return v
    
    @staticmethod
    def _check_balanced_parentheses(expression: str) -> bool:
        """
        Check if parentheses in expression are balanced
        """
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
            
            if count < 0:
                return False
        
        return count == 0
    
    def get_field_references(self) -> list[str]:
        """
        Extract all field references from the formula expression
        Returns list of field names referenced in [Field_Name] format
        """
        return re.findall(r'\[([^\]]+)\]', self.formula_expression)
