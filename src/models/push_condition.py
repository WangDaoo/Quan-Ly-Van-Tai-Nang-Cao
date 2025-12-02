"""
Push Condition Model - Model for workflow automation conditions
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class ConditionOperator(str, Enum):
    """Enumeration of 12 supported condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class LogicOperator(str, Enum):
    """Enumeration of logic operators for combining conditions"""
    AND = "AND"
    OR = "OR"


class PushCondition(BaseModel):
    """
    Model representing a push condition for workflow automation.
    
    Supports 12 operators:
    - equals, not_equals
    - contains, not_contains
    - starts_with, ends_with
    - greater_than, less_than, greater_or_equal, less_or_equal
    - is_empty, is_not_empty
    
    Supports logic operators: AND, OR
    
    Validates:
    - Operator is one of the 12 supported operators
    - Logic operator is AND or OR
    - Field name is not empty
    """
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: Optional[int] = None
    source_department_id: int = Field(..., description="Source department ID")
    target_department_id: int = Field(..., description="Target department ID")
    field_name: str = Field(..., min_length=1, max_length=100, description="Field name to check")
    operator: ConditionOperator = Field(..., description="Condition operator (one of 12)")
    value: Optional[str] = Field(default=None, description="Value to compare against")
    logic_operator: LogicOperator = Field(default=LogicOperator.AND, description="Logic operator (AND/OR)")
    condition_order: int = Field(default=0, ge=0, description="Order of condition evaluation")
    is_active: bool = Field(default=True, description="Whether condition is active")
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
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate that value is provided for operators that require it
        """
        operator = info.data.get('operator')
        
        # Operators that don't require a value
        no_value_operators = {
            ConditionOperator.IS_EMPTY,
            ConditionOperator.IS_NOT_EMPTY
        }
        
        if operator not in no_value_operators:
            if v is None or v == "":
                raise ValueError(
                    f"Giá trị không được để trống cho toán tử {operator}"
                )
        
        return v
    
    @field_validator('source_department_id', 'target_department_id')
    @classmethod
    def validate_department_ids(cls, v: int) -> int:
        """
        Validate department IDs are positive
        """
        if v <= 0:
            raise ValueError("Department ID phải là số dương")
        
        return v
    
    def evaluate(self, field_value: any) -> bool:
        """
        Evaluate the condition against a field value
        
        Args:
            field_value: The value to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        # Convert field_value to string for comparison
        field_str = str(field_value) if field_value is not None else ""
        value_str = self.value if self.value is not None else ""
        
        if self.operator == ConditionOperator.EQUALS:
            return field_str == value_str
        
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return field_str != value_str
        
        elif self.operator == ConditionOperator.CONTAINS:
            return value_str in field_str
        
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            return value_str not in field_str
        
        elif self.operator == ConditionOperator.STARTS_WITH:
            return field_str.startswith(value_str)
        
        elif self.operator == ConditionOperator.ENDS_WITH:
            return field_str.endswith(value_str)
        
        elif self.operator == ConditionOperator.GREATER_THAN:
            try:
                return float(field_str) > float(value_str)
            except (ValueError, TypeError):
                return False
        
        elif self.operator == ConditionOperator.LESS_THAN:
            try:
                return float(field_str) < float(value_str)
            except (ValueError, TypeError):
                return False
        
        elif self.operator == ConditionOperator.GREATER_OR_EQUAL:
            try:
                return float(field_str) >= float(value_str)
            except (ValueError, TypeError):
                return False
        
        elif self.operator == ConditionOperator.LESS_OR_EQUAL:
            try:
                return float(field_str) <= float(value_str)
            except (ValueError, TypeError):
                return False
        
        elif self.operator == ConditionOperator.IS_EMPTY:
            return field_value is None or field_str == ""
        
        elif self.operator == ConditionOperator.IS_NOT_EMPTY:
            return field_value is not None and field_str != ""
        
        return False
