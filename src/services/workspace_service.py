"""
Workspace Service - Manages employee workspaces
Provides workspace CRUD, switching, configuration export/import, and data isolation
"""

import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from src.models.employee_workspace import EmployeeWorkspace
from src.database.enhanced_db_manager import EnhancedDatabaseManager


logger = logging.getLogger(__name__)


class WorkspaceService:
    """
    Service for managing employee workspaces
    
    Features:
    - Create, read, update, delete workspaces
    - Switch between workspaces
    - Export/import workspace configurations
    - Data isolation between workspaces
    
    Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize workspace service
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self._active_workspaces: Dict[int, int] = {}  # employee_id -> workspace_id
    
    # ========================================================================
    # Workspace CRUD Operations
    # ========================================================================
    
    def create_workspace(
        self,
        employee_id: int,
        workspace_name: str,
        configuration: Optional[Dict[str, Any]] = None
    ) -> EmployeeWorkspace:
        """
        Create a new workspace for an employee
        
        Args:
            employee_id: Employee ID
            workspace_name: Name of the workspace
            configuration: Optional workspace configuration
            
        Returns:
            Created workspace
            
        Raises:
            ValueError: If workspace name already exists for employee
            
        Validates: Requirement 9.1
        """
        # Validate input using Pydantic model
        workspace = EmployeeWorkspace(
            employee_id=employee_id,
            workspace_name=workspace_name,
            configuration=configuration or {}
        )
        
        # Check if workspace name already exists for this employee
        existing = self.get_workspace_by_name(employee_id, workspace_name)
        if existing:
            raise ValueError(f"Workspace '{workspace_name}' đã tồn tại cho nhân viên này")
        
        # Serialize configuration to JSON string for database
        config_json = json.dumps(workspace.configuration) if workspace.configuration else None
        
        # Insert into database
        workspace_data = {
            'employee_id': workspace.employee_id,
            'workspace_name': workspace.workspace_name,
            'is_active': workspace.is_active,
            'configuration': config_json
        }
        
        workspace_id = self.db.execute_insert(
            """
            INSERT INTO employee_workspaces (employee_id, workspace_name, is_active, configuration)
            VALUES (?, ?, ?, ?)
            """,
            (
                workspace_data['employee_id'],
                workspace_data['workspace_name'],
                workspace_data['is_active'],
                workspace_data['configuration']
            )
        )
        
        workspace.id = workspace_id
        
        logger.info(f"Created workspace '{workspace_name}' (ID: {workspace_id}) for employee {employee_id}")
        
        return workspace
    
    def get_workspace_by_id(self, workspace_id: int) -> Optional[EmployeeWorkspace]:
        """
        Get workspace by ID
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace or None if not found
        """
        results = self.db.execute_query(
            "SELECT * FROM employee_workspaces WHERE id = ?",
            (workspace_id,)
        )
        
        if not results:
            return None
        
        return self._row_to_workspace(results[0])
    
    def get_workspace_by_name(
        self,
        employee_id: int,
        workspace_name: str
    ) -> Optional[EmployeeWorkspace]:
        """
        Get workspace by employee ID and name
        
        Args:
            employee_id: Employee ID
            workspace_name: Workspace name
            
        Returns:
            Workspace or None if not found
        """
        results = self.db.execute_query(
            "SELECT * FROM employee_workspaces WHERE employee_id = ? AND workspace_name = ?",
            (employee_id, workspace_name)
        )
        
        if not results:
            return None
        
        return self._row_to_workspace(results[0])
    
    def get_workspaces_for_employee(
        self,
        employee_id: int,
        active_only: bool = True
    ) -> List[EmployeeWorkspace]:
        """
        Get all workspaces for an employee
        
        Args:
            employee_id: Employee ID
            active_only: Only return active workspaces
            
        Returns:
            List of workspaces
            
        Validates: Requirement 9.2
        """
        query = "SELECT * FROM employee_workspaces WHERE employee_id = ?"
        params = [employee_id]
        
        if active_only:
            query += " AND is_active = 1"
        
        query += " ORDER BY workspace_name"
        
        results = self.db.execute_query(query, tuple(params))
        
        return [self._row_to_workspace(row) for row in results]
    
    def update_workspace(
        self,
        workspace_id: int,
        workspace_name: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> EmployeeWorkspace:
        """
        Update workspace properties
        
        Args:
            workspace_id: Workspace ID
            workspace_name: New workspace name (optional)
            configuration: New configuration (optional)
            is_active: New active status (optional)
            
        Returns:
            Updated workspace
            
        Raises:
            ValueError: If workspace not found or name already exists
        """
        # Get existing workspace
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace ID {workspace_id} không tồn tại")
        
        # Update fields
        if workspace_name is not None:
            # Check if new name conflicts with existing workspace
            existing = self.get_workspace_by_name(workspace.employee_id, workspace_name)
            if existing and existing.id != workspace_id:
                raise ValueError(f"Workspace '{workspace_name}' đã tồn tại cho nhân viên này")
            workspace.workspace_name = workspace_name
        
        if configuration is not None:
            workspace.configuration = configuration
        
        if is_active is not None:
            workspace.is_active = is_active
        
        # Serialize configuration
        config_json = json.dumps(workspace.configuration) if workspace.configuration else None
        
        # Update database
        self.db.execute_update(
            """
            UPDATE employee_workspaces 
            SET workspace_name = ?, configuration = ?, is_active = ?
            WHERE id = ?
            """,
            (workspace.workspace_name, config_json, workspace.is_active, workspace_id)
        )
        
        logger.info(f"Updated workspace ID {workspace_id}")
        
        return workspace
    
    def delete_workspace(self, workspace_id: int) -> bool:
        """
        Delete a workspace
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            True if deleted, False if not found
        """
        rows_affected = self.db.execute_update(
            "DELETE FROM employee_workspaces WHERE id = ?",
            (workspace_id,)
        )
        
        if rows_affected > 0:
            # Remove from active workspaces if it was active
            for emp_id, ws_id in list(self._active_workspaces.items()):
                if ws_id == workspace_id:
                    del self._active_workspaces[emp_id]
            
            logger.info(f"Deleted workspace ID {workspace_id}")
            return True
        
        return False
    
    # ========================================================================
    # Workspace Switching
    # ========================================================================
    
    def switch_workspace(self, employee_id: int, workspace_id: int) -> EmployeeWorkspace:
        """
        Switch to a different workspace for an employee
        
        Args:
            employee_id: Employee ID
            workspace_id: Workspace ID to switch to
            
        Returns:
            The activated workspace
            
        Raises:
            ValueError: If workspace not found or doesn't belong to employee
            
        Validates: Requirement 9.3
        """
        # Verify workspace exists and belongs to employee
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace ID {workspace_id} không tồn tại")
        
        if workspace.employee_id != employee_id:
            raise ValueError(f"Workspace ID {workspace_id} không thuộc về nhân viên {employee_id}")
        
        if not workspace.is_active:
            raise ValueError(f"Workspace '{workspace.workspace_name}' không hoạt động")
        
        # Set as active workspace for this employee
        self._active_workspaces[employee_id] = workspace_id
        
        logger.info(f"Employee {employee_id} switched to workspace '{workspace.workspace_name}' (ID: {workspace_id})")
        
        return workspace
    
    def get_active_workspace(self, employee_id: int) -> Optional[EmployeeWorkspace]:
        """
        Get the currently active workspace for an employee
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Active workspace or None
            
        Validates: Requirement 9.3
        """
        workspace_id = self._active_workspaces.get(employee_id)
        if workspace_id:
            return self.get_workspace_by_id(workspace_id)
        
        return None
    
    # ========================================================================
    # Configuration Export/Import
    # ========================================================================
    
    def export_workspace_configuration(self, workspace_id: int) -> Dict[str, Any]:
        """
        Export workspace configuration to a dictionary
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace configuration as dictionary
            
        Raises:
            ValueError: If workspace not found
            
        Validates: Requirement 9.5
        """
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace ID {workspace_id} không tồn tại")
        
        export_data = {
            'workspace_name': workspace.workspace_name,
            'configuration': workspace.configuration or {},
            'is_active': workspace.is_active,
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        logger.info(f"Exported configuration for workspace ID {workspace_id}")
        
        return export_data
    
    def import_workspace_configuration(
        self,
        employee_id: int,
        import_data: Dict[str, Any],
        overwrite_existing: bool = False
    ) -> EmployeeWorkspace:
        """
        Import workspace configuration from a dictionary
        
        Args:
            employee_id: Employee ID to import for
            import_data: Configuration data to import
            overwrite_existing: If True, overwrite existing workspace with same name
            
        Returns:
            Created or updated workspace
            
        Raises:
            ValueError: If import data is invalid
            
        Validates: Requirement 9.5
        """
        # Validate import data structure
        if 'workspace_name' not in import_data:
            raise ValueError("Import data phải chứa 'workspace_name'")
        
        workspace_name = import_data['workspace_name']
        configuration = import_data.get('configuration', {})
        is_active = import_data.get('is_active', True)
        
        # Check if workspace already exists
        existing = self.get_workspace_by_name(employee_id, workspace_name)
        
        if existing:
            if overwrite_existing:
                # Update existing workspace
                workspace = self.update_workspace(
                    existing.id,
                    configuration=configuration,
                    is_active=is_active
                )
                logger.info(f"Imported configuration overwrote workspace '{workspace_name}' (ID: {existing.id})")
            else:
                raise ValueError(f"Workspace '{workspace_name}' đã tồn tại. Sử dụng overwrite_existing=True để ghi đè")
        else:
            # Create new workspace
            workspace = self.create_workspace(
                employee_id=employee_id,
                workspace_name=workspace_name,
                configuration=configuration
            )
            if not is_active:
                workspace = self.update_workspace(workspace.id, is_active=False)
            
            logger.info(f"Imported configuration created new workspace '{workspace_name}' (ID: {workspace.id})")
        
        return workspace
    
    def export_workspace_to_json(self, workspace_id: int) -> str:
        """
        Export workspace configuration to JSON string
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            JSON string of workspace configuration
            
        Validates: Requirement 9.5
        """
        config = self.export_workspace_configuration(workspace_id)
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def import_workspace_from_json(
        self,
        employee_id: int,
        json_string: str,
        overwrite_existing: bool = False
    ) -> EmployeeWorkspace:
        """
        Import workspace configuration from JSON string
        
        Args:
            employee_id: Employee ID
            json_string: JSON string containing configuration
            overwrite_existing: If True, overwrite existing workspace
            
        Returns:
            Created or updated workspace
            
        Raises:
            ValueError: If JSON is invalid
            
        Validates: Requirement 9.5
        """
        try:
            import_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON không hợp lệ: {str(e)}")
        
        return self.import_workspace_configuration(employee_id, import_data, overwrite_existing)
    
    # ========================================================================
    # Data Isolation
    # ========================================================================
    
    def get_workspace_records(
        self,
        workspace_id: int,
        department_id: Optional[int] = None,
        status: str = 'active'
    ) -> List[Dict[str, Any]]:
        """
        Get business records for a specific workspace
        
        Args:
            workspace_id: Workspace ID
            department_id: Optional department filter
            status: Record status filter
            
        Returns:
            List of business records
            
        Validates: Requirement 9.4 (Data isolation)
        """
        query = "SELECT * FROM business_records WHERE workspace_id = ? AND status = ?"
        params = [workspace_id, status]
        
        if department_id is not None:
            query += " AND department_id = ?"
            params.append(department_id)
        
        query += " ORDER BY created_at DESC"
        
        results = self.db.execute_query(query, tuple(params))
        
        return results
    
    def create_workspace_record(
        self,
        workspace_id: int,
        department_id: int,
        employee_id: int,
        record_data: Dict[str, Any]
    ) -> int:
        """
        Create a business record in a specific workspace
        
        Args:
            workspace_id: Workspace ID
            department_id: Department ID
            employee_id: Employee ID
            record_data: Record data as dictionary
            
        Returns:
            Created record ID
            
        Validates: Requirement 9.4 (Data isolation)
        """
        # Verify workspace exists and belongs to employee
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace ID {workspace_id} không tồn tại")
        
        if workspace.employee_id != employee_id:
            raise ValueError(f"Workspace ID {workspace_id} không thuộc về nhân viên {employee_id}")
        
        # Serialize record data
        record_json = json.dumps(record_data, ensure_ascii=False)
        
        # Insert record
        record_id = self.db.execute_insert(
            """
            INSERT INTO business_records 
            (department_id, employee_id, workspace_id, record_data, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (department_id, employee_id, workspace_id, record_json, 'active')
        )
        
        logger.info(f"Created record ID {record_id} in workspace {workspace_id}")
        
        return record_id
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _row_to_workspace(self, row: Dict[str, Any]) -> EmployeeWorkspace:
        """
        Convert database row to EmployeeWorkspace model
        
        Args:
            row: Database row as dictionary
            
        Returns:
            EmployeeWorkspace instance
        """
        # Parse configuration JSON
        configuration = None
        if row.get('configuration'):
            try:
                configuration = json.loads(row['configuration'])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse configuration for workspace ID {row['id']}")
                configuration = {}
        
        return EmployeeWorkspace(
            id=row['id'],
            employee_id=row['employee_id'],
            workspace_name=row['workspace_name'],
            is_active=bool(row['is_active']),
            configuration=configuration,
            created_at=row.get('created_at')
        )
