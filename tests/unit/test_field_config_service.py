"""
Unit tests for Field Configuration Service
"""
import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.field_config_service import FieldConfigService
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.field_configuration import FieldType, WidgetType


@pytest.fixture
def db_manager():
    """Create a test database manager"""
    db = EnhancedDatabaseManager("data/test_transport.db")
    yield db
    db.close()


@pytest.fixture
def field_config_service(db_manager):
    """Create a field config service instance"""
    return FieldConfigService(db_manager)


@pytest.fixture
def sample_department_id(db_manager):
    """Create a sample department and return its ID"""
    dept_data = {
        'name': 'test_dept',
        'display_name': 'Test Department',
        'description': 'Test department for field config tests'
    }
    dept_id = db_manager.insert_department(dept_data)
    return dept_id


class TestFieldConfigService:
    """Test suite for Field Configuration Service"""
    
    def test_create_field_config(self, field_config_service, sample_department_id):
        """Test creating a field configuration"""
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'test_field',
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX,
            'is_required': True,
            'display_order': 0,
            'category': 'Test Category'
        }
        
        config = field_config_service.create_field_config(config_data)
        
        assert config is not None
        assert config.id is not None
        assert config.field_name == 'test_field'
        assert config.field_type == FieldType.TEXT
        assert config.is_required is True
        assert config.category == 'Test Category'
    
    def test_create_field_config_with_validation_rules(self, field_config_service, sample_department_id):
        """Test creating a field configuration with validation rules"""
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'email_field',
            'field_type': FieldType.EMAIL,
            'widget_type': WidgetType.EMAIL_WIDGET,
            'is_required': True,
            'validation_rules': {
                'required': True,
                'email_format': True
            },
            'display_order': 1
        }
        
        config = field_config_service.create_field_config(config_data)
        
        assert config is not None
        assert config.validation_rules is not None
        assert config.validation_rules['email_format'] is True
    
    def test_create_dropdown_field_with_options(self, field_config_service, sample_department_id):
        """Test creating a dropdown field with options"""
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'status_field',
            'field_type': FieldType.DROPDOWN,
            'widget_type': WidgetType.COMBOBOX,
            'options': ['Active', 'Inactive', 'Pending'],
            'display_order': 2
        }
        
        config = field_config_service.create_field_config(config_data)
        
        assert config is not None
        assert config.options is not None
        assert len(config.options) == 3
        assert 'Active' in config.options
    
    def test_get_field_config_by_id(self, field_config_service, sample_department_id):
        """Test retrieving a field configuration by ID"""
        # Create a config
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'retrieve_test',
            'field_type': FieldType.NUMBER,
            'widget_type': WidgetType.NUMBER_WIDGET,
            'display_order': 0
        }
        created_config = field_config_service.create_field_config(config_data)
        
        # Retrieve it
        retrieved_config = field_config_service.get_field_config_by_id(created_config.id)
        
        assert retrieved_config is not None
        assert retrieved_config.id == created_config.id
        assert retrieved_config.field_name == 'retrieve_test'
    
    def test_update_field_config(self, field_config_service, sample_department_id):
        """Test updating a field configuration"""
        # Create a config
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'update_test',
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX,
            'is_required': False,
            'display_order': 0
        }
        created_config = field_config_service.create_field_config(config_data)
        
        # Update it
        update_data = {
            'is_required': True,
            'category': 'Updated Category'
        }
        updated_config = field_config_service.update_field_config(created_config.id, update_data)
        
        assert updated_config.is_required is True
        assert updated_config.category == 'Updated Category'
        assert updated_config.field_name == 'update_test'  # Unchanged
    
    def test_delete_field_config_soft(self, field_config_service, sample_department_id):
        """Test soft deleting a field configuration"""
        # Create a config
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'delete_test',
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX,
            'display_order': 0
        }
        created_config = field_config_service.create_field_config(config_data)
        
        # Soft delete it
        result = field_config_service.delete_field_config(created_config.id, soft_delete=True)
        
        assert result is True
        
        # Should still exist but be inactive
        deleted_config = field_config_service.get_field_config_by_id(created_config.id)
        assert deleted_config is not None
        assert deleted_config.is_active is False
    
    def test_get_field_configs_by_department(self, field_config_service, sample_department_id):
        """Test retrieving all field configs for a department"""
        # Create multiple configs
        for i in range(3):
            config_data = {
                'department_id': sample_department_id,
                'field_name': f'field_{i}',
                'field_type': FieldType.TEXT,
                'widget_type': WidgetType.TEXTBOX,
                'display_order': i
            }
            field_config_service.create_field_config(config_data)
        
        # Retrieve all
        configs = field_config_service.get_field_configs_by_department(sample_department_id)
        
        assert len(configs) >= 3
        # Check ordering
        for i in range(len(configs) - 1):
            assert configs[i].display_order <= configs[i + 1].display_order
    
    def test_get_grouped_field_configs(self, field_config_service, sample_department_id):
        """Test grouping field configs by category"""
        # Create configs in different categories
        categories = ['Category A', 'Category B', 'Category A']
        for i, category in enumerate(categories):
            config_data = {
                'department_id': sample_department_id,
                'field_name': f'grouped_field_{i}',
                'field_type': FieldType.TEXT,
                'widget_type': WidgetType.TEXTBOX,
                'category': category,
                'display_order': i
            }
            field_config_service.create_field_config(config_data)
        
        # Get grouped configs
        grouped = field_config_service.get_grouped_field_configs(sample_department_id)
        
        assert 'Category A' in grouped
        assert 'Category B' in grouped
        assert len(grouped['Category A']) >= 2
        assert len(grouped['Category B']) >= 1
    
    def test_reorder_field_configs(self, field_config_service, sample_department_id):
        """Test reordering field configurations"""
        # Create configs
        config_ids = []
        for i in range(3):
            config_data = {
                'department_id': sample_department_id,
                'field_name': f'reorder_field_{i}',
                'field_type': FieldType.TEXT,
                'widget_type': WidgetType.TEXTBOX,
                'display_order': i
            }
            config = field_config_service.create_field_config(config_data)
            config_ids.append(config.id)
        
        # Reorder them (reverse order)
        reorder_data = [
            {'id': config_ids[0], 'display_order': 2},
            {'id': config_ids[1], 'display_order': 1},
            {'id': config_ids[2], 'display_order': 0}
        ]
        result = field_config_service.reorder_field_configs(reorder_data)
        
        assert result is True
        
        # Verify new order
        config_0 = field_config_service.get_field_config_by_id(config_ids[0])
        config_2 = field_config_service.get_field_config_by_id(config_ids[2])
        assert config_0.display_order == 2
        assert config_2.display_order == 0
    
    def test_validate_field_config_data(self, field_config_service, sample_department_id):
        """Test validation of field config data"""
        # Valid data
        valid_data = {
            'department_id': sample_department_id,
            'field_name': 'valid_field',
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX,
            'display_order': 0
        }
        result = field_config_service.validate_field_config_data(valid_data)
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        
        # Invalid data (missing required field)
        invalid_data = {
            'department_id': sample_department_id,
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX
        }
        result = field_config_service.validate_field_config_data(invalid_data)
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
    
    def test_get_available_field_types(self, field_config_service):
        """Test getting available field types"""
        field_types = field_config_service.get_available_field_types()
        
        assert len(field_types) == 10
        assert any(ft['value'] == FieldType.TEXT for ft in field_types)
        assert any(ft['value'] == FieldType.EMAIL for ft in field_types)
        assert any(ft['value'] == FieldType.DROPDOWN for ft in field_types)
    
    def test_get_widget_type_for_field_type(self, field_config_service):
        """Test getting widget type for field type"""
        assert field_config_service.get_widget_type_for_field_type(FieldType.TEXT) == WidgetType.TEXTBOX
        assert field_config_service.get_widget_type_for_field_type(FieldType.EMAIL) == WidgetType.EMAIL_WIDGET
        assert field_config_service.get_widget_type_for_field_type(FieldType.DROPDOWN) == WidgetType.COMBOBOX
    
    def test_duplicate_field_config(self, field_config_service, sample_department_id):
        """Test duplicating a field configuration"""
        # Create original config
        config_data = {
            'department_id': sample_department_id,
            'field_name': 'original_field',
            'field_type': FieldType.TEXT,
            'widget_type': WidgetType.TEXTBOX,
            'category': 'Test',
            'display_order': 0
        }
        original_config = field_config_service.create_field_config(config_data)
        
        # Duplicate it
        duplicated_config = field_config_service.duplicate_field_config(original_config.id)
        
        assert duplicated_config is not None
        assert duplicated_config.id != original_config.id
        assert duplicated_config.field_name == 'original_field_copy'
        assert duplicated_config.field_type == original_config.field_type
        assert duplicated_config.category == original_config.category
        assert duplicated_config.display_order > original_config.display_order


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
