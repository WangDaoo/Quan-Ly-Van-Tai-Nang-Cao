"""
Unit tests for Pydantic models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models import (
    Trip, CompanyPrice, Department, Employee,
    FieldConfiguration, FieldType, WidgetType,
    Formula, PushCondition, ConditionOperator, LogicOperator,
    WorkflowHistory, WorkflowStatus, EmployeeWorkspace
)


class TestTripModel:
    """Tests for Trip model"""
    
    def test_valid_trip(self):
        """Test creating a valid trip"""
        trip = Trip(
            ma_chuyen="C001",
            khach_hang="Công ty ABC",
            diem_di="Hà Nội",
            diem_den="TP.HCM",
            gia_ca=5000000,
            khoan_luong=1000000,
            chi_phi_khac=500000,
            ghi_chu="Test trip"
        )
        
        assert trip.ma_chuyen == "C001"
        assert trip.khach_hang == "Công ty ABC"
        assert trip.gia_ca == 5000000
    
    def test_invalid_ma_chuyen_format(self):
        """Test invalid trip code format"""
        with pytest.raises(ValidationError) as exc_info:
            Trip(
                ma_chuyen="ABC001",  # Invalid format
                khach_hang="Công ty ABC",
                gia_ca=5000000
            )
        
        assert "Mã chuyến phải có định dạng" in str(exc_info.value)
    
    def test_empty_khach_hang(self):
        """Test empty customer name"""
        with pytest.raises(ValidationError) as exc_info:
            Trip(
                ma_chuyen="C001",
                khach_hang="   ",  # Empty after strip
                gia_ca=5000000
            )
        
        assert "không được để trống" in str(exc_info.value)
    
    def test_negative_price(self):
        """Test negative price"""
        with pytest.raises(ValidationError) as exc_info:
            Trip(
                ma_chuyen="C001",
                khach_hang="Công ty ABC",
                gia_ca=-1000  # Negative price
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestCompanyPriceModel:
    """Tests for CompanyPrice model"""
    
    def test_valid_company_price(self):
        """Test creating a valid company price"""
        price = CompanyPrice(
            company_name="Công ty A",
            khach_hang="Khách hàng 1",
            diem_di="Hà Nội",
            diem_den="Đà Nẵng",
            gia_ca=3000000,
            khoan_luong=800000
        )
        
        assert price.company_name == "Công ty A"
        assert price.gia_ca == 3000000


class TestDepartmentModel:
    """Tests for Department model"""
    
    def test_valid_department(self):
        """Test creating a valid department"""
        dept = Department(
            name="sales",
            display_name="Phòng Kinh Doanh",
            description="Sales department"
        )
        
        assert dept.name == "sales"
        assert dept.is_active is True
    
    def test_invalid_department_name(self):
        """Test invalid department name with special characters"""
        with pytest.raises(ValidationError) as exc_info:
            Department(
                name="sales-dept!",  # Invalid characters
                display_name="Sales"
            )
        
        assert "chỉ được chứa" in str(exc_info.value)


class TestEmployeeModel:
    """Tests for Employee model"""
    
    def test_valid_employee(self):
        """Test creating a valid employee"""
        emp = Employee(
            username="john_doe",
            full_name="John Doe",
            email="john@example.com",
            phone="0123456789",
            department_id=1
        )
        
        assert emp.username == "john_doe"
        assert emp.email == "john@example.com"
    
    def test_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError):
            Employee(
                username="john_doe",
                full_name="John Doe",
                email="invalid-email"  # Invalid email
            )
    
    def test_invalid_phone(self):
        """Test invalid phone format"""
        with pytest.raises(ValidationError) as exc_info:
            Employee(
                username="john_doe",
                full_name="John Doe",
                phone="123"  # Too short
            )
        
        assert "Số điện thoại không hợp lệ" in str(exc_info.value)
    
    def test_valid_phone_formats(self):
        """Test various valid phone formats"""
        valid_phones = ["0123456789", "+84123456789", "84123456789"]
        
        for phone in valid_phones:
            emp = Employee(
                username="john_doe",
                full_name="John Doe",
                phone=phone
            )
            assert emp.phone is not None


class TestFieldConfigurationModel:
    """Tests for FieldConfiguration model"""
    
    def test_valid_field_config(self):
        """Test creating a valid field configuration"""
        config = FieldConfiguration(
            department_id=1,
            field_name="customer_name",
            field_type=FieldType.TEXT,
            widget_type=WidgetType.TEXTBOX,
            is_required=True,
            display_order=1
        )
        
        assert config.field_type == "text"
        assert config.is_required is True
    
    def test_dropdown_without_options(self):
        """Test dropdown field without options"""
        with pytest.raises(ValidationError) as exc_info:
            FieldConfiguration(
                department_id=1,
                field_name="status",
                field_type=FieldType.DROPDOWN,
                widget_type=WidgetType.COMBOBOX,
                options=[]  # Empty options
            )
        
        assert "phải có ít nhất một tùy chọn" in str(exc_info.value)


class TestFormulaModel:
    """Tests for Formula model"""
    
    def test_valid_formula(self):
        """Test creating a valid formula"""
        formula = Formula(
            department_id=1,
            target_field="total",
            formula_expression="[price] * [quantity] - [discount]",
            description="Calculate total"
        )
        
        assert formula.target_field == "total"
        assert len(formula.get_field_references()) == 3
    
    def test_unbalanced_parentheses(self):
        """Test formula with unbalanced parentheses"""
        with pytest.raises(ValidationError) as exc_info:
            Formula(
                department_id=1,
                target_field="total",
                formula_expression="([price] * [quantity]"  # Missing closing )
            )
        
        assert "không cân bằng" in str(exc_info.value)
    
    def test_invalid_operator_sequence(self):
        """Test formula with invalid operator sequence"""
        with pytest.raises(ValidationError) as exc_info:
            Formula(
                department_id=1,
                target_field="total",
                formula_expression="[price] ++ [quantity]"  # Invalid ++
            )
        
        assert "không hợp lệ" in str(exc_info.value)


class TestPushConditionModel:
    """Tests for PushCondition model"""
    
    def test_valid_push_condition(self):
        """Test creating a valid push condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name="status",
            operator=ConditionOperator.EQUALS,
            value="completed"
        )
        
        assert condition.operator == "equals"
        assert condition.logic_operator == "AND"
    
    def test_condition_without_value(self):
        """Test condition that requires value but none provided"""
        with pytest.raises(ValidationError) as exc_info:
            PushCondition(
                source_department_id=1,
                target_department_id=2,
                field_name="status",
                operator=ConditionOperator.EQUALS,
                value=""  # Empty value
            )
        
        assert "không được để trống" in str(exc_info.value)
    
    def test_is_empty_operator(self):
        """Test IS_EMPTY operator doesn't require value"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name="notes",
            operator=ConditionOperator.IS_EMPTY
        )
        
        assert condition.value is None
    
    def test_evaluate_equals(self):
        """Test evaluating EQUALS condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name="status",
            operator=ConditionOperator.EQUALS,
            value="completed"
        )
        
        assert condition.evaluate("completed") is True
        assert condition.evaluate("pending") is False
    
    def test_evaluate_greater_than(self):
        """Test evaluating GREATER_THAN condition"""
        condition = PushCondition(
            source_department_id=1,
            target_department_id=2,
            field_name="amount",
            operator=ConditionOperator.GREATER_THAN,
            value="1000"
        )
        
        assert condition.evaluate(1500) is True
        assert condition.evaluate(500) is False


class TestWorkflowHistoryModel:
    """Tests for WorkflowHistory model"""
    
    def test_valid_workflow_history(self):
        """Test creating a valid workflow history"""
        history = WorkflowHistory(
            record_id=1,
            source_department_id=1,
            target_department_id=2,
            pushed_by=1,
            status=WorkflowStatus.SUCCESS
        )
        
        assert history.status == "success"
    
    def test_failed_without_error_message(self):
        """Test failed status without error message"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowHistory(
                record_id=1,
                source_department_id=1,
                target_department_id=2,
                status=WorkflowStatus.FAILED
                # Missing error_message
            )
        
        assert "Error message phải được cung cấp" in str(exc_info.value)


class TestEmployeeWorkspaceModel:
    """Tests for EmployeeWorkspace model"""
    
    def test_valid_workspace(self):
        """Test creating a valid workspace"""
        workspace = EmployeeWorkspace(
            employee_id=1,
            workspace_name="Project A",
            configuration={"theme": "dark", "layout": "grid"}
        )
        
        assert workspace.workspace_name == "Project A"
        assert workspace.get_config_value("theme") == "dark"
    
    def test_set_config_value(self):
        """Test setting configuration values"""
        workspace = EmployeeWorkspace(
            employee_id=1,
            workspace_name="Project A"
        )
        
        workspace.set_config_value("theme", "light")
        assert workspace.get_config_value("theme") == "light"
