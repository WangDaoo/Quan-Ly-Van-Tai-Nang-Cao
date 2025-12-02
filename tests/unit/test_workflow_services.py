"""
Unit tests for Workflow Services
Tests PushConditionsService and WorkflowService
"""
import pytest
import json
from datetime import datetime
from src.services.push_conditions_service import PushConditionsService
from src.services.workflow_service import WorkflowService
from src.models.push_condition import PushCondition, ConditionOperator, LogicOperator
from src.models.workflow_history import WorkflowHistory, WorkflowStatus
from src.database.enhanced_db_manager import EnhancedDatabaseManager


@pytest.fixture
def db_manager():
    """Create a test database manager"""
    import tempfile
    import os
    
    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    try:
        db = EnhancedDatabaseManager(database_path=db_path)
        
        # Create test departments
        db.insert_department({
            'name': 'sales',
            'display_name': 'Sales Department',
            'description': 'Sales team',
            'is_active': 1
        })
        
        db.insert_department({
            'name': 'processing',
            'display_name': 'Processing Department',
            'description': 'Processing team',
            'is_active': 1
        })
        
        db.insert_department({
            'name': 'accounting',
            'display_name': 'Accounting Department',
            'description': 'Accounting team',
            'is_active': 1
        })
        
        # Create test employees
        db.insert_employee({
            'username': 'testuser1',
            'full_name': 'Test User 1',
            'email': 'test1@example.com',
            'department_id': 1,
            'is_active': 1
        })
        
        yield db
        db.close()
    finally:
        # Clean up temporary database file
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def push_conditions_service(db_manager):
    """Create push conditions service"""
    return PushConditionsService(db_manager)


@pytest.fixture
def workflow_service(db_manager):
    """Create workflow service"""
    return WorkflowService(db_manager)


class TestPushConditionsService:
    """Test PushConditionsService"""
    
    def test_create_push_condition(self, push_conditions_service):
        """Test creating a push condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND,
            condition_order=0
        )
        
        condition_id = push_conditions_service.create_push_condition(condition)
        
        assert condition_id > 0
    
    def test_get_push_conditions(self, push_conditions_service):
        """Test retrieving push conditions"""
        # Create test conditions
        condition1 = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND,
            condition_order=0
        )
        
        condition2 = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='amount',
            operator=ConditionOperator.GREATER_THAN,
            value='1000',
            logic_operator=LogicOperator.AND,
            condition_order=1
        )
        
        push_conditions_service.create_push_condition(condition1)
        push_conditions_service.create_push_condition(condition2)
        
        # Retrieve conditions
        conditions = push_conditions_service.get_push_conditions(1, 2)
        
        assert len(conditions) == 2
        assert conditions[0].field_name == 'status'
        assert conditions[1].field_name == 'amount'
    
    def test_update_push_condition(self, push_conditions_service):
        """Test updating a push condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND
        )
        
        condition_id = push_conditions_service.create_push_condition(condition)
        
        # Update condition
        result = push_conditions_service.update_push_condition(
            condition_id,
            {'value': 'approved', 'operator': 'not_equals'}
        )
        
        assert result is True
        
        # Verify update
        conditions = push_conditions_service.get_push_conditions(1, 2)
        assert conditions[0].value == 'approved'
        assert conditions[0].operator == ConditionOperator.NOT_EQUALS
    
    def test_delete_push_condition(self, push_conditions_service):
        """Test deleting a push condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND
        )
        
        condition_id = push_conditions_service.create_push_condition(condition)
        
        # Delete condition
        result = push_conditions_service.delete_push_condition(condition_id)
        
        assert result is True
        
        # Verify deletion (should not appear in active conditions)
        conditions = push_conditions_service.get_push_conditions(1, 2)
        assert len(conditions) == 0
    
    def test_evaluate_conditions_all_and(self, push_conditions_service):
        """Test evaluating conditions with AND logic"""
        conditions = [
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='status',
                operator=ConditionOperator.EQUALS,
                value='completed',
                logic_operator=LogicOperator.AND
            ),
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='amount',
                operator=ConditionOperator.GREATER_THAN,
                value='1000',
                logic_operator=LogicOperator.AND
            )
        ]
        
        # Test data that meets all conditions
        record_data = {
            'status': 'completed',
            'amount': 1500
        }
        
        result = push_conditions_service.evaluate_conditions(conditions, record_data)
        assert result is True
        
        # Test data that fails one condition
        record_data_fail = {
            'status': 'completed',
            'amount': 500
        }
        
        result_fail = push_conditions_service.evaluate_conditions(conditions, record_data_fail)
        assert result_fail is False
    
    def test_evaluate_conditions_with_or(self, push_conditions_service):
        """Test evaluating conditions with OR logic"""
        conditions = [
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='status',
                operator=ConditionOperator.EQUALS,
                value='completed',
                logic_operator=LogicOperator.OR
            ),
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='status',
                operator=ConditionOperator.EQUALS,
                value='approved',
                logic_operator=LogicOperator.OR
            )
        ]
        
        # Test data that meets one condition
        record_data = {
            'status': 'completed'
        }
        
        result = push_conditions_service.evaluate_conditions(conditions, record_data)
        assert result is True
        
        # Test data that meets another condition
        record_data2 = {
            'status': 'approved'
        }
        
        result2 = push_conditions_service.evaluate_conditions(conditions, record_data2)
        assert result2 is True
        
        # Test data that meets no conditions
        record_data_fail = {
            'status': 'pending'
        }
        
        result_fail = push_conditions_service.evaluate_conditions(conditions, record_data_fail)
        assert result_fail is False
    
    def test_evaluate_conditions_mixed_and_or(self, push_conditions_service):
        """Test evaluating conditions with mixed AND/OR logic"""
        conditions = [
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='amount',
                operator=ConditionOperator.GREATER_THAN,
                value='1000',
                logic_operator=LogicOperator.AND
            ),
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='status',
                operator=ConditionOperator.EQUALS,
                value='completed',
                logic_operator=LogicOperator.OR
            ),
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='status',
                operator=ConditionOperator.EQUALS,
                value='approved',
                logic_operator=LogicOperator.OR
            )
        ]
        
        # Test: AND condition true, at least one OR condition true
        record_data = {
            'amount': 1500,
            'status': 'completed'
        }
        
        result = push_conditions_service.evaluate_conditions(conditions, record_data)
        assert result is True
        
        # Test: AND condition true, no OR conditions true
        record_data_fail = {
            'amount': 1500,
            'status': 'pending'
        }
        
        result_fail = push_conditions_service.evaluate_conditions(conditions, record_data_fail)
        assert result_fail is False
    
    def test_evaluate_all_12_operators(self, push_conditions_service):
        """Test all 12 condition operators"""
        test_cases = [
            # equals
            (ConditionOperator.EQUALS, 'test', 'test', True),
            (ConditionOperator.EQUALS, 'test', 'other', False),
            
            # not_equals
            (ConditionOperator.NOT_EQUALS, 'test', 'other', True),
            (ConditionOperator.NOT_EQUALS, 'test', 'test', False),
            
            # contains
            (ConditionOperator.CONTAINS, 'hello world', 'world', True),
            (ConditionOperator.CONTAINS, 'hello world', 'xyz', False),
            
            # not_contains
            (ConditionOperator.NOT_CONTAINS, 'hello world', 'xyz', True),
            (ConditionOperator.NOT_CONTAINS, 'hello world', 'world', False),
            
            # starts_with
            (ConditionOperator.STARTS_WITH, 'hello world', 'hello', True),
            (ConditionOperator.STARTS_WITH, 'hello world', 'world', False),
            
            # ends_with
            (ConditionOperator.ENDS_WITH, 'hello world', 'world', True),
            (ConditionOperator.ENDS_WITH, 'hello world', 'hello', False),
            
            # greater_than
            (ConditionOperator.GREATER_THAN, '100', '50', True),
            (ConditionOperator.GREATER_THAN, '50', '100', False),
            
            # less_than
            (ConditionOperator.LESS_THAN, '50', '100', True),
            (ConditionOperator.LESS_THAN, '100', '50', False),
            
            # greater_or_equal
            (ConditionOperator.GREATER_OR_EQUAL, '100', '100', True),
            (ConditionOperator.GREATER_OR_EQUAL, '100', '50', True),
            (ConditionOperator.GREATER_OR_EQUAL, '50', '100', False),
            
            # less_or_equal
            (ConditionOperator.LESS_OR_EQUAL, '100', '100', True),
            (ConditionOperator.LESS_OR_EQUAL, '50', '100', True),
            (ConditionOperator.LESS_OR_EQUAL, '100', '50', False),
            
            # is_empty
            (ConditionOperator.IS_EMPTY, '', None, True),
            (ConditionOperator.IS_EMPTY, None, None, True),
            (ConditionOperator.IS_EMPTY, 'test', None, False),
            
            # is_not_empty
            (ConditionOperator.IS_NOT_EMPTY, 'test', None, True),
            (ConditionOperator.IS_NOT_EMPTY, '', None, False),
            (ConditionOperator.IS_NOT_EMPTY, None, None, False),
        ]
        
        for operator, field_value, condition_value, expected in test_cases:
            condition = PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name='test_field',
                operator=operator,
                value=condition_value,
                logic_operator=LogicOperator.AND
            )
            
            record_data = {'test_field': field_value}
            result = push_conditions_service.evaluate_conditions([condition], record_data)
            
            assert result == expected, f"Failed for operator {operator} with field_value={field_value}, condition_value={condition_value}"
    
    def test_validate_condition(self, push_conditions_service):
        """Test condition validation"""
        # Valid condition
        valid_condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND
        )
        
        errors = push_conditions_service.validate_condition(valid_condition)
        assert len(errors) == 0
        
        # Invalid: same source and target
        invalid_condition = PushCondition(
            source_department_id=1,
            target_department_id=1,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND
        )
        
        errors = push_conditions_service.validate_condition(invalid_condition)
        assert len(errors) > 0
        assert any('different' in err.lower() for err in errors)


class TestWorkflowService:
    """Test WorkflowService"""
    
    def test_push_record(self, workflow_service):
        """Test pushing a record"""
        record_data = {
            'ma_chuyen': 'C001',
            'khach_hang': 'Customer A',
            'diem_di': 'Hanoi',
            'diem_den': 'HCMC',
            'gia_ca': 5000000,
            'status': 'completed'
        }
        
        result = workflow_service.push_record(
            record_id=1,
            record_data=record_data,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1
        )
        
        assert result is True
        
        # Verify workflow history was logged
        history = workflow_service.get_workflow_history(record_id=1)
        assert len(history) == 1
        assert history[0].status == WorkflowStatus.SUCCESS
    
    def test_push_record_with_field_mapping(self, workflow_service):
        """Test pushing a record with field mapping"""
        record_data = {
            'ma_chuyen': 'C001',
            'khach_hang': 'Customer A',
            'gia_ca': 5000000
        }
        
        field_mapping = {
            'ma_chuyen': 'trip_code',
            'khach_hang': 'customer_name',
            'gia_ca': 'price'
        }
        
        result = workflow_service.push_record(
            record_id=1,
            record_data=record_data,
            source_department_id=1,
            target_department_id=2,
            field_mapping=field_mapping
        )
        
        assert result is True
    
    def test_auto_push_if_conditions_met(self, workflow_service, push_conditions_service):
        """Test automatic push when conditions are met"""
        # Create push condition
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name='status',
            operator=ConditionOperator.EQUALS,
            value='completed',
            logic_operator=LogicOperator.AND
        )
        
        push_conditions_service.create_push_condition(condition)
        
        # Test with data that meets condition
        record_data = {
            'ma_chuyen': 'C001',
            'status': 'completed'
        }
        
        result = workflow_service.auto_push_if_conditions_met(
            record_id=1,
            record_data=record_data,
            source_department_id=1,
            target_department_id=2
        )
        
        assert result is True
        
        # Test with data that doesn't meet condition
        record_data_fail = {
            'ma_chuyen': 'C002',
            'status': 'pending'
        }
        
        result_fail = workflow_service.auto_push_if_conditions_met(
            record_id=2,
            record_data=record_data_fail,
            source_department_id=1,
            target_department_id=2
        )
        
        assert result_fail is False
    
    def test_transform_data(self, workflow_service):
        """Test data transformation"""
        source_data = {
            'ma_chuyen': 'C001',
            'khach_hang': 'Customer A',
            'gia_ca': 5000000,
            'extra_field': 'extra'
        }
        
        field_mapping = {
            'ma_chuyen': 'trip_code',
            'khach_hang': 'customer_name',
            'gia_ca': 'price'
        }
        
        transformed = workflow_service.transform_data(source_data, field_mapping)
        
        assert 'trip_code' in transformed
        assert transformed['trip_code'] == 'C001'
        assert 'customer_name' in transformed
        assert transformed['customer_name'] == 'Customer A'
        assert 'price' in transformed
        assert transformed['price'] == 5000000
        assert 'extra_field' in transformed  # Unmapped fields included
    
    def test_log_workflow(self, workflow_service):
        """Test workflow logging"""
        history_id = workflow_service.log_workflow(
            record_id=1,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS,
            error_message=None
        )
        
        assert history_id > 0
        
        # Retrieve and verify
        history = workflow_service.get_workflow_history(record_id=1)
        assert len(history) == 1
        assert history[0].status == WorkflowStatus.SUCCESS
    
    def test_get_workflow_history_with_filters(self, workflow_service):
        """Test retrieving workflow history with filters"""
        # Create multiple history records
        workflow_service.log_workflow(
            record_id=1,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS
        )
        
        workflow_service.log_workflow(
            record_id=2,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.FAILED,
            error_message='Test error'
        )
        
        workflow_service.log_workflow(
            record_id=3,
            source_department_id=2,
            target_department_id=3,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS
        )
        
        # Filter by source department
        history = workflow_service.get_workflow_history(source_department_id=1)
        assert len(history) == 2
        
        # Filter by status
        history_success = workflow_service.get_workflow_history(status=WorkflowStatus.SUCCESS)
        assert len(history_success) == 2
        
        history_failed = workflow_service.get_workflow_history(status=WorkflowStatus.FAILED)
        assert len(history_failed) == 1
    
    def test_get_workflow_statistics(self, workflow_service):
        """Test workflow statistics"""
        # Create test history
        workflow_service.log_workflow(
            record_id=1,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS
        )
        
        workflow_service.log_workflow(
            record_id=2,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS
        )
        
        workflow_service.log_workflow(
            record_id=3,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.FAILED,
            error_message='Test error'
        )
        
        stats = workflow_service.get_workflow_statistics(
            source_department_id=1,
            target_department_id=2
        )
        
        assert stats['total_pushes'] == 3
        assert stats['successful_pushes'] == 2
        assert stats['failed_pushes'] == 1
        assert stats['success_rate'] == 66.67
