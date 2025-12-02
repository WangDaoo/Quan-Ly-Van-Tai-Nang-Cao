"""
Workflow History Model - Model for tracking workflow automation history
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


class WorkflowStatus(str, Enum):
    """Enumeration of workflow execution statuses"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class WorkflowHistory(BaseModel):
    """
    Model representing a workflow execution history entry.
    
    Tracks:
    - Record that was pushed
    - Source and target departments
    - User who initiated the push
    - Status and error messages
    - Timestamp
    
    Validates:
    - Department IDs are positive
    - Status is one of the valid statuses
    - Error message required when status is FAILED
    """
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: Optional[int] = None
    record_id: int = Field(..., description="ID of the record that was pushed")
    source_department_id: int = Field(..., description="Source department ID")
    target_department_id: int = Field(..., description="Target department ID")
    pushed_by: Optional[int] = Field(default=None, description="Employee ID who initiated push")
    status: WorkflowStatus = Field(..., description="Workflow execution status")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: Optional[datetime] = None
    
    @field_validator('record_id', 'source_department_id', 'target_department_id')
    @classmethod
    def validate_positive_ids(cls, v: int) -> int:
        """
        Validate that IDs are positive
        """
        if v <= 0:
            raise ValueError("ID phải là số dương")
        
        return v
    
    @field_validator('pushed_by')
    @classmethod
    def validate_pushed_by(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate pushed_by ID if provided
        """
        if v is not None and v <= 0:
            raise ValueError("Employee ID phải là số dương")
        
        return v
    
    @model_validator(mode='after')
    def validate_error_message_for_failed_status(self):
        """
        Validate that error message is provided when status is FAILED
        """
        if self.status == WorkflowStatus.FAILED and not self.error_message:
            raise ValueError("Error message phải được cung cấp khi status là FAILED")
        
        return self
