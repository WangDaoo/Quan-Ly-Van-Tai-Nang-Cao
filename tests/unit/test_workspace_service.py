"""
Unit tests for WorkspaceService
Tests workspace CRUD, switching, export/import, and data isolation
"""

import pytest
import json
import tempfile
import os
from datetime import datetime

from src.services.workspace_service import WorkspaceService
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.employee_workspace import EmployeeWorkspace


@pytest.fixture
def db_manager():
    """Create a temporary database for testing"""
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = EnhancedDatabaseManager(temp_db.name, pool_size=2)
    
    # Insert test employee
    db.execute_insert(
        "INSERT INTO departments (name, display_name) VALUES (?, ?)",
        ('sales', 'Sales Department')
    )
    
    db.execute_insert(
        "INSERT INTO employees (username, full_name, department_id) VALUES (?, ?, ?)",
        ('testuser', 'Test User', 1)
    )
    
    yield db
    
    # Cleanup
    db.close()
    os.unlink(temp_db.name)


@pytest.fixture
def workspace_service(db_manager):
    """Create WorkspaceService instance"""
    return WorkspaceService(db_manager)


class TestWorkspaceCRUD:
    """Test workspace CRUD operations"""
    
    def test_create_workspace_basic(self, workspace_service):
        """Test creating a basic workspace"""
        workspace = workspace_service.create_workspace(
            employee_id=1,
            workspace_name="Project A"
        )
        
        assert workspace.id is not None
        assert workspace.employee_id == 1
        assert workspace.workspace_name == "Project A"
        assert workspace.is_active is True
        assert workspace.configuration == {}
    
    def test_create_workspace_with_configuration(self, workspace_service):
        """Test creating workspace with configuration"""
        config = {
            'theme': 'dark',
            'layout': 'grid',
            'filters': {'status': 'active'}
        }
        
        workspace = workspace_service.create_workspace(
            employee_id=1,
            workspace_name="Project B",
            configuration=config
        )
        
        assert workspace.configuration == config
    
    def test_create_workspace_duplicate_name(self, workspace_service):
        """Test creating workspace with duplicate name fails"""
        workspace_service.create_workspace(
            employee_id=1,
            workspace_name="Duplicate"
        )
        
        with pytest.raises(ValueError, match="đã tồn tại"):
            workspace_service.create_workspace(
                employee_id=1,
                workspace_name="Duplicate"
            )
    
    def test_create_workspace_invalid_employee_id(self, workspace_service):
        """Test creating workspace with invalid employee ID"""
        with pytest.raises(ValueError, match="số dương"):
            workspace_service.create_workspace(
                employee_id=0,
                workspace_name="Invalid"
            )
    
    def test_create_workspace_empty_name(self, workspace_service):
        """Test creating workspace with empty name"""
        # Pydantic will raise ValidationError which gets caught as ValueError
        with pytest.raises(Exception):  # Can be ValidationError or ValueError
            workspace_service.create_workspace(
                employee_id=1,
                workspace_name=""
            )
    
    def test_get_workspace_by_id(self, workspace_service):
        """Test retrieving workspace by ID"""
        created = workspace_service.create_workspace(
            employee_id=1,
            workspace_name="Test Workspace"
        )
        
        retrieved = workspace_service.get_workspace_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.workspace_name == "Test Workspace"
    
    def test_get_workspace_by_id_not_found(self, workspace_service):
        """Test retrieving non-existent workspace"""
        result = workspace_service.get_workspace_by_id(9999)
        assert result is None
    
    def test_get_workspace_by_name(self, workspace_service):
        """Test retrieving workspace by name"""
        workspace_service.create_workspace(
            employee_id=1,
            workspace_name="Named Workspace"
        )
        
        retrieved = workspace_service.get_workspace_by_name(1, "Named Workspace")
        
        assert retrieved is not None
        assert retrieved.workspace_name == "Named Workspace"
    
    def test_get_workspaces_for_employee(self, workspace_service):
        """Test retrieving all workspaces for an employee"""
        workspace_service.create_workspace(1, "Workspace 1")
        workspace_service.create_workspace(1, "Workspace 2")
        workspace_service.create_workspace(1, "Workspace 3")
        
        workspaces = workspace_service.get_workspaces_for_employee(1)
        
        assert len(workspaces) == 3
        names = [ws.workspace_name for ws in workspaces]
        assert "Workspace 1" in names
        assert "Workspace 2" in names
        assert "Workspace 3" in names
    
    def test_get_workspaces_active_only(self, workspace_service):
        """Test retrieving only active workspaces"""
        ws1 = workspace_service.create_workspace(1, "Active")
        ws2 = workspace_service.create_workspace(1, "Inactive")
        
        # Deactivate one workspace
        workspace_service.update_workspace(ws2.id, is_active=False)
        
        active_workspaces = workspace_service.get_workspaces_for_employee(1, active_only=True)
        all_workspaces = workspace_service.get_workspaces_for_employee(1, active_only=False)
        
        assert len(active_workspaces) == 1
        assert len(all_workspaces) == 2
        assert active_workspaces[0].workspace_name == "Active"
    
    def test_update_workspace_name(self, workspace_service):
        """Test updating workspace name"""
        workspace = workspace_service.create_workspace(1, "Old Name")
        
        updated = workspace_service.update_workspace(
            workspace.id,
            workspace_name="New Name"
        )
        
        assert updated.workspace_name == "New Name"
        
        # Verify in database
        retrieved = workspace_service.get_workspace_by_id(workspace.id)
        assert retrieved.workspace_name == "New Name"
    
    def test_update_workspace_configuration(self, workspace_service):
        """Test updating workspace configuration"""
        workspace = workspace_service.create_workspace(1, "Config Test")
        
        new_config = {'setting1': 'value1', 'setting2': 42}
        updated = workspace_service.update_workspace(
            workspace.id,
            configuration=new_config
        )
        
        assert updated.configuration == new_config
    
    def test_update_workspace_active_status(self, workspace_service):
        """Test updating workspace active status"""
        workspace = workspace_service.create_workspace(1, "Status Test")
        
        updated = workspace_service.update_workspace(
            workspace.id,
            is_active=False
        )
        
        assert updated.is_active is False
    
    def test_update_workspace_not_found(self, workspace_service):
        """Test updating non-existent workspace"""
        with pytest.raises(ValueError, match="không tồn tại"):
            workspace_service.update_workspace(9999, workspace_name="New Name")
    
    def test_update_workspace_duplicate_name(self, workspace_service):
        """Test updating workspace to duplicate name"""
        workspace_service.create_workspace(1, "Workspace A")
        ws2 = workspace_service.create_workspace(1, "Workspace B")
        
        with pytest.raises(ValueError, match="đã tồn tại"):
            workspace_service.update_workspace(ws2.id, workspace_name="Workspace A")
    
    def test_delete_workspace(self, workspace_service):
        """Test deleting a workspace"""
        workspace = workspace_service.create_workspace(1, "To Delete")
        
        result = workspace_service.delete_workspace(workspace.id)
        
        assert result is True
        
        # Verify deletion
        retrieved = workspace_service.get_workspace_by_id(workspace.id)
        assert retrieved is None
    
    def test_delete_workspace_not_found(self, workspace_service):
        """Test deleting non-existent workspace"""
        result = workspace_service.delete_workspace(9999)
        assert result is False


class TestWorkspaceSwitching:
    """Test workspace switching functionality"""
    
    def test_switch_workspace(self, workspace_service):
        """Test switching to a workspace"""
        ws1 = workspace_service.create_workspace(1, "Workspace 1")
        ws2 = workspace_service.create_workspace(1, "Workspace 2")
        
        # Switch to workspace 1
        active = workspace_service.switch_workspace(1, ws1.id)
        
        assert active.id == ws1.id
        assert active.workspace_name == "Workspace 1"
    
    def test_get_active_workspace(self, workspace_service):
        """Test getting active workspace"""
        ws1 = workspace_service.create_workspace(1, "Active WS")
        
        # Initially no active workspace
        active = workspace_service.get_active_workspace(1)
        assert active is None
        
        # Switch and check
        workspace_service.switch_workspace(1, ws1.id)
        active = workspace_service.get_active_workspace(1)
        
        assert active is not None
        assert active.id == ws1.id
    
    def test_switch_workspace_not_found(self, workspace_service):
        """Test switching to non-existent workspace"""
        with pytest.raises(ValueError, match="không tồn tại"):
            workspace_service.switch_workspace(1, 9999)
    
    def test_switch_workspace_wrong_employee(self, workspace_service, db_manager):
        """Test switching to workspace of different employee"""
        # Create second employee
        db_manager.execute_insert(
            "INSERT INTO employees (username, full_name, department_id) VALUES (?, ?, ?)",
            ('user2', 'User 2', 1)
        )
        
        # Create workspace for employee 1
        ws1 = workspace_service.create_workspace(1, "Employee 1 WS")
        
        # Try to switch employee 2 to employee 1's workspace
        with pytest.raises(ValueError, match="không thuộc về nhân viên"):
            workspace_service.switch_workspace(2, ws1.id)
    
    def test_switch_workspace_inactive(self, workspace_service):
        """Test switching to inactive workspace"""
        ws = workspace_service.create_workspace(1, "Inactive WS")
        workspace_service.update_workspace(ws.id, is_active=False)
        
        with pytest.raises(ValueError, match="không hoạt động"):
            workspace_service.switch_workspace(1, ws.id)
    
    def test_switch_between_workspaces(self, workspace_service):
        """Test switching between multiple workspaces"""
        ws1 = workspace_service.create_workspace(1, "WS 1")
        ws2 = workspace_service.create_workspace(1, "WS 2")
        ws3 = workspace_service.create_workspace(1, "WS 3")
        
        # Switch to WS 1
        workspace_service.switch_workspace(1, ws1.id)
        assert workspace_service.get_active_workspace(1).id == ws1.id
        
        # Switch to WS 2
        workspace_service.switch_workspace(1, ws2.id)
        assert workspace_service.get_active_workspace(1).id == ws2.id
        
        # Switch to WS 3
        workspace_service.switch_workspace(1, ws3.id)
        assert workspace_service.get_active_workspace(1).id == ws3.id


class TestConfigurationExportImport:
    """Test workspace configuration export/import"""
    
    def test_export_workspace_configuration(self, workspace_service):
        """Test exporting workspace configuration"""
        config = {
            'theme': 'dark',
            'columns': ['col1', 'col2'],
            'filters': {'status': 'active'}
        }
        
        workspace = workspace_service.create_workspace(
            1,
            "Export Test",
            configuration=config
        )
        
        exported = workspace_service.export_workspace_configuration(workspace.id)
        
        assert 'workspace_name' in exported
        assert exported['workspace_name'] == "Export Test"
        assert 'configuration' in exported
        assert exported['configuration'] == config
        assert 'is_active' in exported
        assert 'exported_at' in exported
        assert 'version' in exported
    
    def test_export_workspace_not_found(self, workspace_service):
        """Test exporting non-existent workspace"""
        with pytest.raises(ValueError, match="không tồn tại"):
            workspace_service.export_workspace_configuration(9999)
    
    def test_import_workspace_configuration(self, workspace_service):
        """Test importing workspace configuration"""
        import_data = {
            'workspace_name': 'Imported WS',
            'configuration': {'key': 'value'},
            'is_active': True
        }
        
        workspace = workspace_service.import_workspace_configuration(1, import_data)
        
        assert workspace.workspace_name == 'Imported WS'
        assert workspace.configuration == {'key': 'value'}
        assert workspace.is_active is True
    
    def test_import_workspace_overwrite(self, workspace_service):
        """Test importing with overwrite"""
        # Create existing workspace
        workspace_service.create_workspace(
            1,
            "Existing",
            configuration={'old': 'config'}
        )
        
        # Import with same name
        import_data = {
            'workspace_name': 'Existing',
            'configuration': {'new': 'config'},
            'is_active': True
        }
        
        # Should fail without overwrite
        with pytest.raises(ValueError, match="đã tồn tại"):
            workspace_service.import_workspace_configuration(1, import_data, overwrite_existing=False)
        
        # Should succeed with overwrite
        workspace = workspace_service.import_workspace_configuration(1, import_data, overwrite_existing=True)
        assert workspace.configuration == {'new': 'config'}
    
    def test_import_workspace_invalid_data(self, workspace_service):
        """Test importing invalid data"""
        with pytest.raises(ValueError, match="workspace_name"):
            workspace_service.import_workspace_configuration(1, {})
    
    def test_export_import_roundtrip(self, workspace_service):
        """Test export then import produces same configuration"""
        original_config = {
            'theme': 'light',
            'layout': 'list',
            'settings': {
                'auto_save': True,
                'page_size': 50
            }
        }
        
        # Create and export
        ws1 = workspace_service.create_workspace(
            1,
            "Original",
            configuration=original_config
        )
        exported = workspace_service.export_workspace_configuration(ws1.id)
        
        # Import as new workspace
        exported['workspace_name'] = "Imported Copy"
        ws2 = workspace_service.import_workspace_configuration(1, exported)
        
        assert ws2.configuration == original_config
    
    def test_export_to_json(self, workspace_service):
        """Test exporting to JSON string"""
        workspace = workspace_service.create_workspace(
            1,
            "JSON Test",
            configuration={'test': 'data'}
        )
        
        json_string = workspace_service.export_workspace_to_json(workspace.id)
        
        # Verify it's valid JSON
        parsed = json.loads(json_string)
        assert parsed['workspace_name'] == "JSON Test"
        assert parsed['configuration'] == {'test': 'data'}
    
    def test_import_from_json(self, workspace_service):
        """Test importing from JSON string"""
        json_data = json.dumps({
            'workspace_name': 'From JSON',
            'configuration': {'imported': True},
            'is_active': True
        })
        
        workspace = workspace_service.import_workspace_from_json(1, json_data)
        
        assert workspace.workspace_name == 'From JSON'
        assert workspace.configuration == {'imported': True}
    
    def test_import_from_invalid_json(self, workspace_service):
        """Test importing from invalid JSON"""
        with pytest.raises(ValueError, match="JSON không hợp lệ"):
            workspace_service.import_workspace_from_json(1, "not valid json{")


class TestDataIsolation:
    """Test data isolation between workspaces"""
    
    def test_create_workspace_record(self, workspace_service):
        """Test creating record in workspace"""
        workspace = workspace_service.create_workspace(1, "Data WS")
        
        record_data = {
            'field1': 'value1',
            'field2': 42
        }
        
        record_id = workspace_service.create_workspace_record(
            workspace_id=workspace.id,
            department_id=1,
            employee_id=1,
            record_data=record_data
        )
        
        assert record_id > 0
    
    def test_get_workspace_records(self, workspace_service):
        """Test retrieving records for workspace"""
        workspace = workspace_service.create_workspace(1, "Records WS")
        
        # Create multiple records
        for i in range(3):
            workspace_service.create_workspace_record(
                workspace_id=workspace.id,
                department_id=1,
                employee_id=1,
                record_data={'index': i}
            )
        
        records = workspace_service.get_workspace_records(workspace.id)
        
        assert len(records) == 3
    
    def test_workspace_record_isolation(self, workspace_service):
        """Test that records are isolated between workspaces"""
        ws1 = workspace_service.create_workspace(1, "WS 1")
        ws2 = workspace_service.create_workspace(1, "WS 2")
        
        # Create records in WS 1
        workspace_service.create_workspace_record(
            ws1.id, 1, 1, {'workspace': 'ws1', 'data': 'A'}
        )
        workspace_service.create_workspace_record(
            ws1.id, 1, 1, {'workspace': 'ws1', 'data': 'B'}
        )
        
        # Create records in WS 2
        workspace_service.create_workspace_record(
            ws2.id, 1, 1, {'workspace': 'ws2', 'data': 'C'}
        )
        
        # Verify isolation
        ws1_records = workspace_service.get_workspace_records(ws1.id)
        ws2_records = workspace_service.get_workspace_records(ws2.id)
        
        assert len(ws1_records) == 2
        assert len(ws2_records) == 1
    
    def test_create_record_wrong_employee(self, workspace_service, db_manager):
        """Test creating record in workspace of different employee"""
        # Create second employee
        db_manager.execute_insert(
            "INSERT INTO employees (username, full_name, department_id) VALUES (?, ?, ?)",
            ('user2', 'User 2', 1)
        )
        
        # Create workspace for employee 1
        ws = workspace_service.create_workspace(1, "Employee 1 WS")
        
        # Try to create record as employee 2
        with pytest.raises(ValueError, match="không thuộc về nhân viên"):
            workspace_service.create_workspace_record(
                ws.id, 1, 2, {'data': 'test'}
            )
    
    def test_create_record_invalid_workspace(self, workspace_service):
        """Test creating record in non-existent workspace"""
        with pytest.raises(ValueError, match="không tồn tại"):
            workspace_service.create_workspace_record(
                9999, 1, 1, {'data': 'test'}
            )


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_workspace_with_special_characters(self, workspace_service):
        """Test workspace name with special characters"""
        workspace = workspace_service.create_workspace(
            1,
            "Dự án #1 - Test (2024)"
        )
        
        assert workspace.workspace_name == "Dự án #1 - Test (2024)"
    
    def test_workspace_with_unicode(self, workspace_service):
        """Test workspace with Vietnamese characters"""
        workspace = workspace_service.create_workspace(
            1,
            "Không gian làm việc tiếng Việt"
        )
        
        assert workspace.workspace_name == "Không gian làm việc tiếng Việt"
    
    def test_large_configuration(self, workspace_service):
        """Test workspace with large configuration"""
        large_config = {
            f'key_{i}': f'value_{i}' for i in range(100)
        }
        
        workspace = workspace_service.create_workspace(
            1,
            "Large Config",
            configuration=large_config
        )
        
        retrieved = workspace_service.get_workspace_by_id(workspace.id)
        assert len(retrieved.configuration) == 100
    
    def test_nested_configuration(self, workspace_service):
        """Test workspace with nested configuration"""
        nested_config = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep'
                    }
                }
            }
        }
        
        workspace = workspace_service.create_workspace(
            1,
            "Nested Config",
            configuration=nested_config
        )
        
        retrieved = workspace_service.get_workspace_by_id(workspace.id)
        assert retrieved.configuration['level1']['level2']['level3']['value'] == 'deep'
    
    def test_delete_active_workspace(self, workspace_service):
        """Test deleting currently active workspace"""
        ws = workspace_service.create_workspace(1, "Active to Delete")
        workspace_service.switch_workspace(1, ws.id)
        
        # Delete should succeed
        result = workspace_service.delete_workspace(ws.id)
        assert result is True
        
        # Active workspace should be cleared
        active = workspace_service.get_active_workspace(1)
        assert active is None
