"""
Push Conditions Service - Service for managing workflow push conditions
"""
import logging
from typing import List, Dict, Any, Optional
from src.models.push_condition import PushCondition, ConditionOperator, LogicOperator
from src.database.enhanced_db_manager import EnhancedDatabaseManager


logger = logging.getLogger(__name__)


class PushConditionsService:
    """
    Service for managing push conditions for workflow automation.
    
    Provides:
    - CRUD operations for push conditions
    - Condition evaluation with 12 operators
    - Support for AND/OR logic operators
    - Validation of conditions
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize push conditions service
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def create_push_condition(self, condition: PushCondition) -> int:
        """
        Create a new push condition
        
        Args:
            condition: PushCondition model instance
            
        Returns:
            ID of created condition
            
        Raises:
            ValueError: If validation fails
        """
        try:
            condition_data = {
                'source_department_id': condition.source_department_id,
                'target_department_id': condition.target_department_id,
                'field_name': condition.field_name,
                'operator': condition.operator,
                'value': condition.value,
                'logic_operator': condition.logic_operator,
                'condition_order': condition.condition_order,
                'is_active': condition.is_active
            }
            
            condition_id = self.db_manager.insert_push_condition(condition_data)
            logger.info(f"Created push condition {condition_id} from dept {condition.source_department_id} to {condition.target_department_id}")
            
            return condition_id
            
        except Exception as e:
            logger.error(f"Failed to create push condition: {e}")
            raise
    
    def get_push_conditions(
        self, 
        source_department_id: int, 
        target_department_id: int
    ) -> List[PushCondition]:
        """
        Get all active push conditions between two departments
        
        Args:
            source_department_id: Source department ID
            target_department_id: Target department ID
            
        Returns:
            List of PushCondition instances ordered by condition_order
        """
        try:
            conditions_data = self.db_manager.get_push_conditions(
                source_department_id, 
                target_department_id
            )
            
            conditions = [
                PushCondition(**data) 
                for data in conditions_data
            ]
            
            logger.debug(f"Retrieved {len(conditions)} push conditions from dept {source_department_id} to {target_department_id}")
            
            return conditions
            
        except Exception as e:
            logger.error(f"Failed to get push conditions: {e}")
            raise
    
    def update_push_condition(
        self, 
        condition_id: int, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a push condition
        
        Args:
            condition_id: ID of condition to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful
        """
        try:
            # Build update query dynamically
            set_clauses = []
            params = []
            
            allowed_fields = {
                'field_name', 'operator', 'value', 'logic_operator', 
                'condition_order', 'is_active'
            }
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            params.append(condition_id)
            query = f"UPDATE push_conditions SET {', '.join(set_clauses)} WHERE id = ?"
            
            rows_affected = self.db_manager.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Updated push condition {condition_id}")
                return True
            else:
                logger.warning(f"No push condition found with id {condition_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update push condition: {e}")
            raise
    
    def delete_push_condition(self, condition_id: int) -> bool:
        """
        Delete a push condition (soft delete by setting is_active = 0)
        
        Args:
            condition_id: ID of condition to delete
            
        Returns:
            True if deletion successful
        """
        try:
            query = "UPDATE push_conditions SET is_active = 0 WHERE id = ?"
            rows_affected = self.db_manager.execute_update(query, (condition_id,))
            
            if rows_affected > 0:
                logger.info(f"Deleted push condition {condition_id}")
                return True
            else:
                logger.warning(f"No push condition found with id {condition_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete push condition: {e}")
            raise
    
    def evaluate_conditions(
        self, 
        conditions: List[PushCondition], 
        record_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate all conditions against a record
        
        Supports AND/OR logic operators:
        - AND: All conditions must be true
        - OR: At least one condition must be true
        
        Args:
            conditions: List of PushCondition instances
            record_data: Dictionary of field values
            
        Returns:
            True if conditions are met, False otherwise
        """
        if not conditions:
            logger.debug("No conditions to evaluate, returning True")
            return True
        
        # Group conditions by logic operator
        and_conditions = []
        or_conditions = []
        
        for condition in conditions:
            if condition.logic_operator == LogicOperator.AND:
                and_conditions.append(condition)
            else:
                or_conditions.append(condition)
        
        # Evaluate AND conditions (all must be true)
        and_result = True
        if and_conditions:
            and_results = []
            for condition in and_conditions:
                field_value = record_data.get(condition.field_name)
                result = condition.evaluate(field_value)
                and_results.append(result)
                logger.debug(
                    f"AND condition: {condition.field_name} {condition.operator} {condition.value} = {result}"
                )
            and_result = all(and_results)
        
        # Evaluate OR conditions (at least one must be true)
        or_result = False
        if or_conditions:
            or_results = []
            for condition in or_conditions:
                field_value = record_data.get(condition.field_name)
                result = condition.evaluate(field_value)
                or_results.append(result)
                logger.debug(
                    f"OR condition: {condition.field_name} {condition.operator} {condition.value} = {result}"
                )
            or_result = any(or_results)
        
        # Combine results
        if and_conditions and or_conditions:
            # Both AND and OR conditions exist
            final_result = and_result and or_result
        elif and_conditions:
            # Only AND conditions
            final_result = and_result
        else:
            # Only OR conditions
            final_result = or_result
        
        logger.info(f"Condition evaluation result: {final_result}")
        return final_result
    
    def validate_condition(self, condition: PushCondition) -> List[str]:
        """
        Validate a push condition
        
        Args:
            condition: PushCondition to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            # Pydantic validation will catch most issues
            # Additional business logic validation can go here
            
            # Check that source and target departments are different
            if condition.source_department_id == condition.target_department_id:
                errors.append("Source and target departments must be different")
            
            # Check that value is provided for operators that need it
            no_value_operators = {
                ConditionOperator.IS_EMPTY,
                ConditionOperator.IS_NOT_EMPTY
            }
            
            if condition.operator not in no_value_operators:
                if not condition.value:
                    errors.append(f"Value is required for operator {condition.operator}")
            
        except Exception as e:
            errors.append(str(e))
        
        return errors
