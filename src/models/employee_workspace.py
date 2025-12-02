"""
Employee Workspace Model - Model for managing employee workspaces
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import json


class EmployeeWorkspace(BaseModel):
    """
    Model representing an employee's workspace configuration.
    
    Workspaces allow employees to:
    - Organize work by project or task
    - Have different configurations per workspace
    - Switch between workspaces easily
    - Isolate data between workspaces
    
    Validates:
    - Employee ID is positive
    - Workspace name is not empty
    - Configuration is valid JSON
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    employee_id: int = Field(..., description="Employee ID who owns this workspace")
    workspace_name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    is_active: bool = Field(default=True, description="Whether workspace is active")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Workspace configuration as JSON")
    created_at: Optional[datetime] = None
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v: int) -> int:
        """
        Validate employee ID is positive
        """
        if v <= 0:
            raise ValueError("Employee ID phải là số dương")
        
        return v
    
    @field_validator('workspace_name')
    @classmethod
    def validate_workspace_name(cls, v: str) -> str:
        """
        Validate workspace name is not empty
        """
        if not v or not v.strip():
            raise ValueError("Tên workspace không được để trống")
        
        return v.strip()
    
    @field_validator('configuration')
    @classmethod
    def validate_configuration(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate that configuration is a valid dictionary
        """
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("Configuration phải là một dictionary")
        
        # Try to serialize to ensure it's JSON-serializable
        try:
            json.dumps(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Configuration phải có thể serialize thành JSON: {str(e)}")
        
        return v
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self.configuration is None:
            return default
        
        return self.configuration.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        if self.configuration is None:
            self.configuration = {}
        
        self.configuration[key] = value
