"""
Verification script for Integrated Main Window
Tests basic functionality without running the full GUI
"""

import sys
from unittest.mock import Mock

# Mock QApplication before importing PyQt6
from PyQt6.QtWidgets import QApplication

# Create QApplication
app = QApplication(sys.argv)

from src.gui.integrated_main_window import IntegratedMainWindow
from src.database.enhanced_db_manager import EnhancedDatabaseManager

def verify_window_creation():
    """Verify window can be created"""
    print("Testing window creation...")
    
    # Mock database manager
    db_manager = Mock()
    db_manager.fetch_all = Mock(return_value=[
        (1, "sales", "Kinh Doanh", "Phòng Kinh Doanh", 1, "2024-01-01"),
        (2, "processing", "Điều Hành", "Phòng Điều Hành", 1, "2024-01-01"),
        (3, "accounting", "Kế Toán", "Phòng Kế Toán", 1, "2024-01-01"),
    ])
    
    # Create window
    window = IntegratedMainWindow(db_manager)
    
    # Verify basic properties
    assert window.windowTitle() == "Hệ Thống Quản Lý Vận Tải Toàn Diện"
    assert window.minimumSize().width() == 1200
    assert window.minimumSize().height() == 800
    
    print("✓ Window created successfully")
    return window

def verify_menu_bar(window):
    """Verify menu bar exists"""
    print("Testing menu bar...")
    
    menubar = window.menuBar()
    assert menubar is not None
    
    menus = [action.text() for action in menubar.actions()]
    assert "&File" in menus
    assert "&Edit" in menus
    assert "&View" in menus
    assert "&Tools" in menus
    assert "&Department" in menus
    assert "&Help" in menus
    
    print("✓ Menu bar created with all menus")

def verify_toolbar(window):
    """Verify toolbar exists"""
    print("Testing toolbar...")
    
    assert window.toolbar is not None
    assert not window.toolbar.isMovable()
    
    print("✓ Toolbar created")

def verify_status_bar(window):
    """Verify status bar exists"""
    print("Testing status bar...")
    
    statusbar = window.statusBar()
    assert statusbar is not None
    assert window.record_count_label is not None
    assert window.department_label is not None
    
    print("✓ Status bar created with labels")

def verify_components(window):
    """Verify main components exist"""
    print("Testing main components...")
    
    assert window.employee_tabs is not None
    assert window.pagination_widget is not None
    assert window.employee_tabs.get_tab_count() == 3
    
    print("✓ Main components created")

def verify_services(window):
    """Verify services are initialized"""
    print("Testing services...")
    
    assert window.trip_service is not None
    assert window.field_config_service is not None
    assert window.company_price_service is not None
    assert window.excel_service is not None
    
    print("✓ Services initialized")

def verify_actions(window):
    """Verify menu actions exist"""
    print("Testing menu actions...")
    
    # File menu
    assert window.new_action is not None
    assert window.import_action is not None
    assert window.export_action is not None
    assert window.exit_action is not None
    
    # Edit menu
    assert window.copy_action is not None
    assert window.paste_action is not None
    assert window.delete_action is not None
    
    # View menu
    assert window.column_visibility_action is not None
    assert window.filters_action is not None
    assert window.refresh_action is not None
    
    # Tools menu
    assert window.field_manager_action is not None
    assert window.formula_builder_action is not None
    assert window.push_conditions_action is not None
    
    # Help menu
    assert window.user_manual_action is not None
    assert window.about_action is not None
    
    print("✓ All menu actions created")

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Integrated Main Window Verification")
    print("=" * 60)
    print()
    
    try:
        window = verify_window_creation()
        verify_menu_bar(window)
        verify_toolbar(window)
        verify_status_bar(window)
        verify_components(window)
        verify_services(window)
        verify_actions(window)
        
        print()
        print("=" * 60)
        print("✓ All verification tests passed!")
        print("=" * 60)
        
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ Verification failed: {e}")
        print("=" * 60)
        return 1
    
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error during verification: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
