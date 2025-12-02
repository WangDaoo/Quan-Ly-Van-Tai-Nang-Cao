"""
Workflow Service - Service for executing workflow automation
"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.models.workflow_history import WorkflowHistory, WorkflowStatus
from src.models.push_condition import PushCondition
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.push_conditions_service import PushConditionsService


logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Service for executing workflow automation.
    
    Provides:
    - Automatic push operations based on conditions
    - Data transformation and field mapping
    - Workflow history logging
    - Manual push operations
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize workflow service
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.push_conditions_service = PushConditionsService(db_manager)
    
    def push_record(
        self,
        record_id: int,
        record_data: Dict[str, Any],
        source_department_id: int,
        target_department_id: int,
        pushed_by: Optional[int] = None,
        field_mapping: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Push a record from source department to target department
        
        Args:
            record_id: ID of the record being pushed
            record_data: Dictionary of record field values
            source_department_id: Source department ID
            target_department_id: Target department ID
            pushed_by: Employee ID who initiated the push (optional)
            field_mapping: Dictionary mapping source fields to target fields (optional)
            
        Returns:
            True if push successful, False otherwise
        """
        try:
            # Transform data if field mapping provided
            if field_mapping:
                transformed_data = self.transform_data(record_data, field_mapping)
            else:
                transformed_data = record_data.copy()
            
            # Insert record into target department's business_records table
            # Note: employee_id can be NULL in business_records table
            business_record_data = {
                'department_id': target_department_id,
                'employee_id': pushed_by if pushed_by else 1,  # Use employee ID 1 as default
                'workspace_id': None,
                'record_data': json.dumps(transformed_data),
                'status': 'active'
            }
            
            new_record_id = self.db_manager.insert_business_record(business_record_data)
            
            # Log successful workflow
            self.log_workflow(
                record_id=record_id,
                source_department_id=source_department_id,
                target_department_id=target_department_id,
                pushed_by=pushed_by,
                status=WorkflowStatus.SUCCESS,
                error_message=None
            )
            
            logger.info(
                f"Successfully pushed record {record_id} from dept {source_department_id} "
                f"to dept {target_department_id} (new record id: {new_record_id})"
            )
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to push record {record_id}: {error_msg}")
            
            # Log failed workflow
            self.log_workflow(
                record_id=record_id,
                source_department_id=source_department_id,
                target_department_id=target_department_id,
                pushed_by=pushed_by,
                status=WorkflowStatus.FAILED,
                error_message=error_msg
            )
            
            return False
    
    def auto_push_if_conditions_met(
        self,
        record_id: int,
        record_data: Dict[str, Any],
        source_department_id: int,
        target_department_id: int,
        pushed_by: Optional[int] = None,
        field_mapping: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Automatically push record if conditions are met
        
        Args:
            record_id: ID of the record
            record_data: Dictionary of record field values
            source_department_id: Source department ID
            target_department_id: Target department ID
            pushed_by: Employee ID who initiated the push (optional)
            field_mapping: Dictionary mapping source fields to target fields (optional)
            
        Returns:
            True if conditions met and push successful, False otherwise
        """
        try:
            # Get push conditions
            conditions = self.push_conditions_service.get_push_conditions(
                source_department_id,
                target_department_id
            )
            
            if not conditions:
                logger.debug(
                    f"No push conditions defined from dept {source_department_id} "
                    f"to dept {target_department_id}"
                )
                return False
            
            # Evaluate conditions
            conditions_met = self.push_conditions_service.evaluate_conditions(
                conditions,
                record_data
            )
            
            if not conditions_met:
                logger.debug(
                    f"Push conditions not met for record {record_id} "
                    f"from dept {source_department_id} to dept {target_department_id}"
                )
                return False
            
            # Push record
            return self.push_record(
                record_id=record_id,
                record_data=record_data,
                source_department_id=source_department_id,
                target_department_id=target_department_id,
                pushed_by=pushed_by,
                field_mapping=field_mapping
            )
            
        except Exception as e:
            logger.error(f"Failed to auto-push record {record_id}: {e}")
            return False
    
    def transform_data(
        self,
        source_data: Dict[str, Any],
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Transform data using field mapping
        
        Maps source field names to target field names.
        
        Args:
            source_data: Source record data
            field_mapping: Dictionary mapping source fields to target fields
                          Format: {'source_field': 'target_field'}
            
        Returns:
            Transformed data dictionary
        """
        transformed_data = {}
        
        for source_field, target_field in field_mapping.items():
            if source_field in source_data:
                transformed_data[target_field] = source_data[source_field]
                logger.debug(f"Mapped {source_field} -> {target_field}: {source_data[source_field]}")
            else:
                logger.warning(f"Source field {source_field} not found in data")
        
        # Include unmapped fields as-is
        for field, value in source_data.items():
            if field not in field_mapping and field not in transformed_data:
                transformed_data[field] = value
        
        return transformed_data
    
    def log_workflow(
        self,
        record_id: int,
        source_department_id: int,
        target_department_id: int,
        pushed_by: Optional[int],
        status: WorkflowStatus,
        error_message: Optional[str] = None
    ) -> int:
        """
        Log workflow execution to history
        
        Args:
            record_id: ID of the record
            source_department_id: Source department ID
            target_department_id: Target department ID
            pushed_by: Employee ID who initiated the push
            status: Workflow execution status
            error_message: Error message if failed
            
        Returns:
            ID of created workflow history record
        """
        try:
            history = WorkflowHistory(
                record_id=record_id,
                source_department_id=source_department_id,
                target_department_id=target_department_id,
                pushed_by=pushed_by,
                status=status,
                error_message=error_message
            )
            
            history_data = {
                'record_id': history.record_id,
                'source_department_id': history.source_department_id,
                'target_department_id': history.target_department_id,
                'pushed_by': history.pushed_by,
                'status': history.status,
                'error_message': history.error_message
            }
            
            history_id = self.db_manager.insert_workflow_history(history_data)
            
            logger.info(
                f"Logged workflow history {history_id}: record {record_id} "
                f"from dept {source_department_id} to dept {target_department_id} - {status}"
            )
            
            return history_id
            
        except Exception as e:
            logger.error(f"Failed to log workflow history: {e}")
            raise
    
    def get_workflow_history(
        self,
        record_id: Optional[int] = None,
        source_department_id: Optional[int] = None,
        target_department_id: Optional[int] = None,
        status: Optional[WorkflowStatus] = None,
        limit: int = 100
    ) -> List[WorkflowHistory]:
        """
        Get workflow history with filters
        
        Args:
            record_id: Filter by record ID (optional)
            source_department_id: Filter by source department (optional)
            target_department_id: Filter by target department (optional)
            status: Filter by status (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of WorkflowHistory instances
        """
        try:
            filters = {}
            
            if record_id is not None:
                filters['record_id'] = record_id
            
            if source_department_id is not None:
                filters['source_department_id'] = source_department_id
            
            if target_department_id is not None:
                filters['target_department_id'] = target_department_id
            
            if status is not None:
                filters['status'] = status
            
            history_data = self.db_manager.get_workflow_history(filters, limit)
            
            history_list = [
                WorkflowHistory(**data)
                for data in history_data
            ]
            
            logger.debug(f"Retrieved {len(history_list)} workflow history records")
            
            return history_list
            
        except Exception as e:
            logger.error(f"Failed to get workflow history: {e}")
            raise
    
    def get_workflow_statistics(
        self,
        source_department_id: Optional[int] = None,
        target_department_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get workflow statistics
        
        Args:
            source_department_id: Filter by source department (optional)
            target_department_id: Filter by target department (optional)
            
        Returns:
            Dictionary with statistics:
            - total_pushes: Total number of push operations
            - successful_pushes: Number of successful pushes
            - failed_pushes: Number of failed pushes
            - success_rate: Success rate percentage
        """
        try:
            filters = {}
            
            if source_department_id is not None:
                filters['source_department_id'] = source_department_id
            
            if target_department_id is not None:
                filters['target_department_id'] = target_department_id
            
            # Get all history records
            history_list = self.get_workflow_history(
                source_department_id=source_department_id,
                target_department_id=target_department_id,
                limit=10000  # Get all records
            )
            
            total_pushes = len(history_list)
            successful_pushes = sum(
                1 for h in history_list 
                if h.status == WorkflowStatus.SUCCESS
            )
            failed_pushes = sum(
                1 for h in history_list 
                if h.status == WorkflowStatus.FAILED
            )
            
            success_rate = (
                (successful_pushes / total_pushes * 100) 
                if total_pushes > 0 
                else 0.0
            )
            
            statistics = {
                'total_pushes': total_pushes,
                'successful_pushes': successful_pushes,
                'failed_pushes': failed_pushes,
                'success_rate': round(success_rate, 2)
            }
            
            logger.info(f"Workflow statistics: {statistics}")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            raise
