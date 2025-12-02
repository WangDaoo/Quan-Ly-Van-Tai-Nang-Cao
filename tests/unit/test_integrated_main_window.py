"""
Unit tests for Integrated Main Window
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.integrated_main_window import IntegratedMainWindow
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.department import Department


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_db_manager():
    """Create mock database manager"""
    db_manager = Mock(spec=EnhancedDatabaseManager)
    
    # Mock fetch_all for departments
    db_manager.fetch_all.return_value = [
        (1, "sales", "Kinh Doanh", "Phòng Kinh Doanh", 1, "2024-01-01"),
        (2, "processing", "Điều Hành", "Phòng Điều Hành", 1, "2024-01-01"),
        (3, "accounting", "Kế Toán", "Phòng Kế Toán", 1, "2024-01-01"),
    ]
    
    return db_manager


class TestIntegratedMainWindow:
    """Test cases for IntegratedMainWindow"""
    
    def test_window_creation(self, qapp, mock_db_manager):
        """Test that window can be created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window is not None
        assert window.windowTitle() == "Hệ Thống Quản Lý Vận Tải Toàn Diện"
        assert window.minimumSize().width() == 1200
        assert window.minimumSize().height() == 800
    
    def test_menu_bar_exists(self, qapp, mock_db_manager):
        """Test that menu bar is created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        menubar = window.menuBar()
        assert menubar is not None
        
        # Check menu titles
        menus = [action.text() for action in menubar.actions()]
        assert "&File" in menus
        assert "&Edit" in menus
        assert "&View" in menus
        assert "&Tools" in menus
        assert "&Department" in menus
        assert "&Help" in menus
    
    def test_toolbar_exists(self, qapp, mock_db_manager):
        """Test that toolbar is created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.toolbar is not None
        assert not window.toolbar.isMovable()
    
    def test_status_bar_exists(self, qapp, mock_db_manager):
        """Test that status bar is created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        statusbar = window.statusBar()
        assert statusbar is not None
        assert window.record_count_label is not None
        assert window.department_label is not None
    
    def test_employee_tabs_created(self, qapp, mock_db_manager):
        """Test that employee tabs widget is created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.employee_tabs is not None
        assert window.employee_tabs.get_tab_count() == 3  # 3 departments
    
    def test_pagination_widget_created(self, qapp, mock_db_manager):
        """Test that pagination widget is created"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.pagination_widget is not None
    
    def test_departments_loaded(self, qapp, mock_db_manager):
        """Test that departments are loaded"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert len(window.departments) == 3
        assert window.departments[0].name == "sales"
        assert window.departments[1].name == "processing"
        assert window.departments[2].name == "accounting"
    
    def test_services_initialized(self, qapp, mock_db_manager):
        """Test that services are initialized"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.trip_service is not None
        assert window.field_config_service is not None
        assert window.company_price_service is not None
        assert window.excel_service is not None
    
    def test_file_menu_actions(self, qapp, mock_db_manager):
        """Test file menu actions exist"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.new_action is not None
        assert window.import_action is not None
        assert window.export_action is not None
        assert window.exit_action is not None
    
    def test_edit_menu_actions(self, qapp, mock_db_manager):
        """Test edit menu actions exist"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.copy_action is not None
        assert window.paste_action is not None
        assert window.delete_action is not None
    
    def test_view_menu_actions(self, qapp, mock_db_manager):
        """Test view menu actions exist"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.column_visibility_action is not None
        assert window.filters_action is not None
        assert window.refresh_action is not None
    
    def test_tools_menu_actions(self, qapp, mock_db_manager):
        """Test tools menu actions exist"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.field_manager_action is not None
        assert window.formula_builder_action is not None
        assert window.push_conditions_action is not None
        assert window.workspace_manager_action is not None
        assert window.statistics_action is not None
        assert window.workflow_history_action is not None
    
    def test_help_menu_actions(self, qapp, mock_db_manager):
        """Test help menu actions exist"""
        window = IntegratedMainWindow(mock_db_manager)
        
        assert window.user_manual_action is not None
        assert window.about_action is not None
    
    def test_window_state_persistence(self, qapp, mock_db_manager):
        """Test window state can be saved and restored"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Save state
        window._save_window_state()
        
        # Settings should be saved
        assert window.settings is not None
    
    def test_department_change_signal(self, qapp, mock_db_manager):
        """Test department change updates status bar"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Trigger department change
        window._on_department_changed(1)
        
        # Check department label updated
        assert "Kinh Doanh" in window.department_label.text()
    
    def test_refresh_action(self, qapp, mock_db_manager):
        """Test refresh action"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Mock the refresh method
        window.employee_tabs.refresh_current_department = Mock()
        
        # Trigger refresh
        window._on_refresh()
        
        # Verify refresh was called
        window.employee_tabs.refresh_current_department.assert_called_once()
    
    def test_new_record_action(self, qapp, mock_db_manager):
        """Test new record action"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Get current department widget
        dept_widget = window.employee_tabs.get_current_department_widget()
        if dept_widget:
            # Mock clear_form
            dept_widget.input_form.clear_form = Mock()
            
            # Trigger new record
            window._on_new_record()
            
            # Verify clear_form was called
            dept_widget.input_form.clear_form.assert_called_once()
    
    def test_about_dialog(self, qapp, mock_db_manager):
        """Test about dialog can be shown"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Mock QMessageBox.about
        with patch('src.gui.integrated_main_window.QMessageBox.about') as mock_about:
            window._on_about()
            mock_about.assert_called_once()
    
    def test_window_close_saves_state(self, qapp, mock_db_manager):
        """Test window close saves state"""
        window = IntegratedMainWindow(mock_db_manager)
        
        # Mock save method
        window._save_window_state = Mock()
        
        # Create close event
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        
        # Trigger close
        window.closeEvent(event)
        
        # Verify save was called
        window._save_window_state.assert_called_once()
        assert event.isAccepted()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
