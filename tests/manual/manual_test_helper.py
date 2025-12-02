"""
Manual Testing Helper Script
Provides automated checks and utilities for manual testing
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.integrated_main_window import IntegratedMainWindow
from src.database.enhanced_db_manager import EnhancedDatabaseManager

# Use test database for manual testing
TEST_DATABASE_PATH = str(Path(__file__).parent.parent.parent / "data" / "test_transport.db")


class ManualTestHelper:
    """Helper class for manual testing verification"""
    
    def __init__(self):
        self.test_results = []
        self.db_manager = None
        
    def setup_database(self) -> bool:
        """Setup test database"""
        try:
            self.db_manager = EnhancedDatabaseManager(TEST_DATABASE_PATH)
            return True
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def verify_gui_components(self, window: IntegratedMainWindow) -> List[Tuple[str, bool, str]]:
        """Verify GUI components are present and accessible"""
        results = []
        
        # Check menu bar
        menu_bar = window.menuBar()
        results.append(("Menu Bar exists", menu_bar is not None, "Menu bar should be present"))
        
        if menu_bar:
            menus = [menu_bar.actions()[i].text() for i in range(len(menu_bar.actions()))]
            expected_menus = ["&File", "&Edit", "&View", "&Tools", "&Department", "&Help"]
            for expected in expected_menus:
                found = any(expected in menu for menu in menus)
                results.append((f"Menu '{expected}' exists", found, f"Menu {expected} should be in menu bar"))
        
        # Check toolbar
        toolbar = window.toolbar if hasattr(window, 'toolbar') else None
        results.append(("Toolbar exists", toolbar is not None, "Toolbar should be present"))
        
        # Check status bar
        status_bar = window.statusBar()
        results.append(("Status Bar exists", status_bar is not None, "Status bar should be present"))
        
        # Check central widget
        central_widget = window.centralWidget()
        results.append(("Central Widget exists", central_widget is not None, "Central widget should be present"))
        
        # Check tab widget for departments
        if hasattr(window, 'department_tabs'):
            results.append(("Department Tabs exist", True, "Department tabs should be present"))
            tab_count = window.department_tabs.count()
            results.append((f"Department Tabs count >= 1", tab_count >= 1, "At least one department tab should exist"))
        else:
            results.append(("Department Tabs exist", False, "Department tabs should be present"))
        
        return results
    
    def verify_keyboard_shortcuts(self, window: IntegratedMainWindow) -> List[Tuple[str, bool, str]]:
        """Verify keyboard shortcuts are registered"""
        results = []
        
        # Expected shortcuts
        expected_shortcuts = {
            "Ctrl+N": "New",
            "Ctrl+S": "Save",
            "Ctrl+O": "Open",
            "Ctrl+Z": "Undo",
            "Ctrl+Y": "Redo",
            "Ctrl+C": "Copy",
            "Ctrl+V": "Paste",
            "Delete": "Delete",
            "F2": "Edit",
            "F5": "Refresh",
        }
        
        # Get all shortcuts from window
        shortcuts = window.findChildren(QShortcut)
        registered_keys = [shortcut.key().toString() for shortcut in shortcuts]
        
        for key, action in expected_shortcuts.items():
            found = key in registered_keys
            results.append((f"Shortcut {key} ({action})", found, f"Shortcut {key} should be registered"))
        
        return results
    
    def verify_database_structure(self) -> List[Tuple[str, bool, str]]:
        """Verify database tables and structure"""
        results = []
        
        if not self.db_manager:
            results.append(("Database Manager", False, "Database manager should be initialized"))
            return results
        
        expected_tables = [
            "trips",
            "company_prices",
            "departments",
            "employees",
            "field_configurations",
            "formulas",
            "push_conditions",
            "workflow_history",
            "employee_workspaces",
            "business_records"
        ]
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                for table in expected_tables:
                    exists = table in existing_tables
                    results.append((f"Table '{table}' exists", exists, f"Table {table} should exist in database"))
        except Exception as e:
            results.append(("Database query", False, f"Error querying database: {e}"))
        
        return results
    
    def verify_sample_data(self) -> List[Tuple[str, bool, str]]:
        """Verify sample data exists"""
        results = []
        
        if not self.db_manager:
            results.append(("Database Manager", False, "Database manager should be initialized"))
            return results
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check trips
                cursor.execute("SELECT COUNT(*) FROM trips")
                trip_count = cursor.fetchone()[0]
                results.append((f"Trips data exists ({trip_count} records)", trip_count > 0, "Should have sample trip data"))
                
                # Check company prices
                cursor.execute("SELECT COUNT(*) FROM company_prices")
                price_count = cursor.fetchone()[0]
                results.append((f"Company prices exist ({price_count} records)", price_count > 0, "Should have sample price data"))
                
                # Check departments
                cursor.execute("SELECT COUNT(*) FROM departments")
                dept_count = cursor.fetchone()[0]
                results.append((f"Departments exist ({dept_count} records)", dept_count >= 3, "Should have at least 3 departments"))
        except Exception as e:
            results.append(("Sample data query", False, f"Error querying sample data: {e}"))
        
        return results
    
    def verify_responsive_design(self, window: IntegratedMainWindow) -> List[Tuple[str, bool, str]]:
        """Verify responsive design capabilities"""
        results = []
        
        # Check minimum size
        min_size = window.minimumSize()
        results.append(("Minimum size set", min_size.width() > 0 and min_size.height() > 0, "Window should have minimum size"))
        
        # Check if window is resizable
        results.append(("Window resizable", not window.isMaximized(), "Window should be resizable"))
        
        # Check for splitters
        from PyQt6.QtWidgets import QSplitter
        splitters = window.findChildren(QSplitter)
        results.append((f"Splitters exist ({len(splitters)} found)", len(splitters) > 0, "Should have splitters for responsive layout"))
        
        return results
    
    def run_all_verifications(self, window: IntegratedMainWindow = None) -> Dict[str, List[Tuple[str, bool, str]]]:
        """Run all verification checks"""
        all_results = {}
        
        # Database checks
        if self.setup_database():
            all_results["Database Structure"] = self.verify_database_structure()
            all_results["Sample Data"] = self.verify_sample_data()
        
        # GUI checks (if window provided)
        if window:
            all_results["GUI Components"] = self.verify_gui_components(window)
            all_results["Keyboard Shortcuts"] = self.verify_keyboard_shortcuts(window)
            all_results["Responsive Design"] = self.verify_responsive_design(window)
        
        return all_results
    
    def print_results(self, results: Dict[str, List[Tuple[str, bool, str]]]):
        """Print verification results"""
        print("\n" + "="*80)
        print("MANUAL TESTING VERIFICATION RESULTS")
        print("="*80 + "\n")
        
        total_tests = 0
        total_passed = 0
        
        for category, tests in results.items():
            print(f"\n{category}")
            print("-" * 80)
            
            for test_name, passed, description in tests:
                total_tests += 1
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} | {test_name}")
                if not passed:
                    print(f"       Expected: {description}")
                else:
                    total_passed += 1
        
        print("\n" + "="*80)
        print(f"SUMMARY: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
        print("="*80 + "\n")
        
        return total_passed, total_tests


def main():
    """Main function to run manual test helper"""
    print("Manual Testing Helper - Hệ Thống Quản Lý Vận Tải")
    print("="*80)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create helper
    helper = ManualTestHelper()
    
    # Run database checks first
    print("\nRunning database verification...")
    db_results = {}
    if helper.setup_database():
        db_results["Database Structure"] = helper.verify_database_structure()
        db_results["Sample Data"] = helper.verify_sample_data()
    
    helper.print_results(db_results)
    
    # Ask if user wants to test GUI
    print("\nDo you want to launch the application for GUI testing? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        print("\nLaunching application...")
        try:
            window = IntegratedMainWindow()
            window.show()
            
            # Run GUI checks after a short delay
            def run_gui_checks():
                print("\nRunning GUI verification...")
                gui_results = helper.run_all_verifications(window)
                helper.print_results(gui_results)
                
                # Show results in message box
                passed, total = 0, 0
                for tests in gui_results.values():
                    for _, p, _ in tests:
                        total += 1
                        if p:
                            passed += 1
                
                msg = f"Verification Complete\n\n{passed}/{total} tests passed ({passed/total*100:.1f}%)\n\nSee console for details."
                QMessageBox.information(window, "Test Results", msg)
            
            QTimer.singleShot(2000, run_gui_checks)
            
            sys.exit(app.exec())
        except Exception as e:
            print(f"\n❌ Error launching application: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nGUI testing skipped. Run with 'y' to test GUI components.")


if __name__ == "__main__":
    main()
