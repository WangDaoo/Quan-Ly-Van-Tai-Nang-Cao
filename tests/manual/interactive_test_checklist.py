"""
Interactive Manual Testing Checklist
GUI application to guide manual testing with interactive checklist
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QTextEdit, QLabel,
    QSplitter, QGroupBox, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestChecklistItem(QTreeWidgetItem):
    """Custom tree widget item for test cases"""
    
    def __init__(self, parent, test_name: str, description: str = ""):
        super().__init__(parent, [test_name])
        self.test_name = test_name
        self.description = description
        self.status = "Not Tested"  # Not Tested, Pass, Fail, Blocked
        self.notes = ""
        self.update_display()
    
    def set_status(self, status: str):
        """Set test status"""
        self.status = status
        self.update_display()
    
    def update_display(self):
        """Update visual display based on status"""
        if self.status == "Pass":
            self.setForeground(0, QColor(0, 150, 0))
            self.setText(0, f"✅ {self.test_name}")
        elif self.status == "Fail":
            self.setForeground(0, QColor(200, 0, 0))
            self.setText(0, f"❌ {self.test_name}")
        elif self.status == "Blocked":
            self.setForeground(0, QColor(150, 150, 0))
            self.setText(0, f"⚠️ {self.test_name}")
        else:
            self.setForeground(0, QColor(100, 100, 100))
            self.setText(0, f"⬜ {self.test_name}")


class InteractiveTestChecklist(QMainWindow):
    """Interactive manual testing checklist application"""
    
    def __init__(self):
        super().__init__()
        self.test_items = []
        self.current_item = None
        self.init_ui()
        self.load_test_cases()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Manual Testing Checklist - Hệ Thống Quản Lý Vận Tải")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🧪 Manual Testing Checklist")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Splitter for tree and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Test tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("Test Cases:"))
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Test Cases")
        self.tree.itemClicked.connect(self.on_item_clicked)
        left_layout.addWidget(self.tree)
        
        # Buttons for tree
        tree_buttons = QHBoxLayout()
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.tree.expandAll)
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.tree.collapseAll)
        tree_buttons.addWidget(self.expand_all_btn)
        tree_buttons.addWidget(self.collapse_all_btn)
        left_layout.addLayout(tree_buttons)
        
        splitter.addWidget(left_widget)
        
        # Right side - Test details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Test description
        desc_group = QGroupBox("Test Description")
        desc_layout = QVBoxLayout(desc_group)
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        desc_layout.addWidget(self.description_text)
        right_layout.addWidget(desc_group)
        
        # Test notes
        notes_group = QGroupBox("Test Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter test notes, observations, or issues found...")
        notes_layout.addWidget(self.notes_text)
        right_layout.addWidget(notes_group)
        
        # Status buttons
        status_group = QGroupBox("Test Status")
        status_layout = QHBoxLayout(status_group)
        
        self.pass_btn = QPushButton("✅ Pass")
        self.pass_btn.clicked.connect(lambda: self.set_current_status("Pass"))
        self.pass_btn.setStyleSheet("background-color: #90EE90;")
        
        self.fail_btn = QPushButton("❌ Fail")
        self.fail_btn.clicked.connect(lambda: self.set_current_status("Fail"))
        self.fail_btn.setStyleSheet("background-color: #FFB6C1;")
        
        self.blocked_btn = QPushButton("⚠️ Blocked")
        self.blocked_btn.clicked.connect(lambda: self.set_current_status("Blocked"))
        self.blocked_btn.setStyleSheet("background-color: #FFFFE0;")
        
        self.reset_btn = QPushButton("⬜ Reset")
        self.reset_btn.clicked.connect(lambda: self.set_current_status("Not Tested"))
        
        status_layout.addWidget(self.pass_btn)
        status_layout.addWidget(self.fail_btn)
        status_layout.addWidget(self.blocked_btn)
        status_layout.addWidget(self.reset_btn)
        right_layout.addWidget(status_group)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ Previous")
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self.go_to_next)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        right_layout.addLayout(nav_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📊 Export Results")
        self.export_btn.clicked.connect(self.export_results)
        
        self.summary_btn = QPushButton("📈 Show Summary")
        self.summary_btn.clicked.connect(self.show_summary)
        
        bottom_layout.addWidget(self.export_btn)
        bottom_layout.addWidget(self.summary_btn)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
        # Disable status buttons initially
        self.enable_status_buttons(False)
    
    def load_test_cases(self):
        """Load test cases into tree"""
        # 1. GUI Interactions
        gui_category = QTreeWidgetItem(self.tree, ["1. GUI Interactions"])
        gui_category.setExpanded(True)
        
        # 1.1 Main Window
        main_window = QTreeWidgetItem(gui_category, ["1.1 Main Window"])
        self.add_test_item(main_window, "Application starts without errors", 
                          "Launch the application and verify it starts successfully")
        self.add_test_item(main_window, "Menu bar displays correctly",
                          "Verify File, Edit, View, Tools, Department, Help menus are present")
        self.add_test_item(main_window, "Toolbar displays correctly",
                          "Verify New, Save, Import, Export, Filter, Settings buttons are present")
        self.add_test_item(main_window, "Status bar displays information",
                          "Verify status bar shows record counts and status messages")
        
        # 1.2 Input Form
        input_form = QTreeWidgetItem(gui_category, ["1.2 Input Form Widget"])
        self.add_test_item(input_form, "Form displays all fields",
                          "Verify all fields are visible: mã chuyến, khách hàng, điểm đi, điểm đến, giá cả, etc.")
        self.add_test_item(input_form, "Form submission works",
                          "Enter data and click 'Thêm' button, verify data is added to table")
        self.add_test_item(input_form, "Auto-generate mã chuyến",
                          "Submit form and verify mã chuyến is auto-generated (C001, C002, ...)")
        self.add_test_item(input_form, "Form validation works",
                          "Leave required fields empty and verify error messages")
        self.add_test_item(input_form, "Form reset after submission",
                          "Submit form and verify it resets to empty state")
        
        # 1.3 Autocomplete
        autocomplete = QTreeWidgetItem(gui_category, ["1.3 Autocomplete"])
        self.add_test_item(autocomplete, "Khách hàng autocomplete",
                          "Type in khách hàng field and verify dropdown suggestions appear")
        self.add_test_item(autocomplete, "Điểm đi autocomplete",
                          "Type in điểm đi field and verify dropdown suggestions appear")
        self.add_test_item(autocomplete, "Điểm đến autocomplete",
                          "Type in điểm đến field and verify dropdown suggestions appear")
        self.add_test_item(autocomplete, "Fuzzy search works",
                          "Type partial text and verify fuzzy matching works")
        self.add_test_item(autocomplete, "Click suggestion fills form",
                          "Click on a suggestion and verify it fills the form field")
        
        # 1.4 Main Table
        main_table = QTreeWidgetItem(gui_category, ["1.4 Main Table Widget"])
        self.add_test_item(main_table, "Table displays data",
                          "Verify table shows all records from database")
        self.add_test_item(main_table, "Cell editing works",
                          "Double-click or F2 to edit a cell, change value, verify auto-save")
        self.add_test_item(main_table, "Row selection works",
                          "Click to select row, Ctrl+Click for multi-select, Shift+Click for range")
        self.add_test_item(main_table, "Mã chuyến column read-only",
                          "Try to edit mã chuyến column, verify it's read-only")
        
        # 1.5 Excel-Like Features
        excel_features = QTreeWidgetItem(gui_category, ["1.5 Excel-Like Features"])
        self.add_test_item(excel_features, "Copy cells (Ctrl+C)",
                          "Select cells, press Ctrl+C, paste into Excel, verify format")
        self.add_test_item(excel_features, "Paste cells (Ctrl+V)",
                          "Copy from Excel, press Ctrl+V in table, verify data pasted")
        self.add_test_item(excel_features, "Paste as new rows (Ctrl+Shift+V)",
                          "Copy data, press Ctrl+Shift+V, verify new rows created")
        self.add_test_item(excel_features, "Context menu works",
                          "Right-click on row, verify menu shows insert/duplicate/delete options")
        self.add_test_item(excel_features, "Column management",
                          "Right-click header, verify show/hide, reorder, resize options")
        
        # 1.6 Filtering
        filtering = QTreeWidgetItem(gui_category, ["1.6 Advanced Filtering"])
        self.add_test_item(filtering, "Filter dialog opens",
                          "Click filter button on column header, verify dialog opens")
        self.add_test_item(filtering, "Checkbox filter works",
                          "Select/deselect items in filter dialog, apply, verify table updates")
        self.add_test_item(filtering, "Search in filter dialog",
                          "Use search box in filter dialog, verify items filtered")
        self.add_test_item(filtering, "Multi-column filtering",
                          "Apply filters on multiple columns, verify AND logic")
        self.add_test_item(filtering, "Clear filter works",
                          "Clear filter and verify all data shows again")
        
        # 2. Keyboard Shortcuts
        keyboard_category = QTreeWidgetItem(self.tree, ["2. Keyboard Shortcuts"])
        keyboard_category.setExpanded(True)
        
        shortcuts = [
            ("F2 - Edit cell", "Select cell, press F2, verify edit mode"),
            ("Enter - Move down", "Edit cell, press Enter, verify focus moves down"),
            ("Tab - Move right", "Edit cell, press Tab, verify focus moves right"),
            ("Shift+Tab - Move left", "Edit cell, press Shift+Tab, verify focus moves left"),
            ("Ctrl+C - Copy", "Select cells, press Ctrl+C, verify copied to clipboard"),
            ("Ctrl+V - Paste", "Press Ctrl+V, verify data pasted"),
            ("Ctrl+D - Duplicate row", "Select row, press Ctrl+D, verify row duplicated"),
            ("Delete - Delete rows", "Select rows, press Delete, verify confirmation and deletion"),
            ("Ctrl+Plus - Insert row below", "Select row, press Ctrl+Plus, verify row inserted below"),
            ("F5 - Refresh", "Press F5, verify data refreshed from database"),
        ]
        
        for shortcut, desc in shortcuts:
            self.add_test_item(keyboard_category, shortcut, desc)
        
        # 3. Responsive Design
        responsive_category = QTreeWidgetItem(self.tree, ["3. Responsive Design"])
        responsive_category.setExpanded(True)
        
        self.add_test_item(responsive_category, "Minimum window size",
                          "Resize window to minimum, verify UI doesn't break")
        self.add_test_item(responsive_category, "Maximum window size",
                          "Maximize window, verify UI scales correctly")
        self.add_test_item(responsive_category, "1024x768 resolution",
                          "Resize to 1024x768, verify all components visible")
        self.add_test_item(responsive_category, "1920x1080 resolution",
                          "Resize to 1920x1080, verify proper scaling")
        self.add_test_item(responsive_category, "Splitter behavior",
                          "Drag splitters, verify smooth resizing and minimum sizes respected")
        self.add_test_item(responsive_category, "Font scaling 125%",
                          "Set system font to 125%, verify UI scales correctly")
        
        # 4. Error Scenarios
        error_category = QTreeWidgetItem(self.tree, ["4. Error Scenarios"])
        error_category.setExpanded(True)
        
        # 4.1 Validation Errors
        validation = QTreeWidgetItem(error_category, ["4.1 Validation Errors"])
        self.add_test_item(validation, "Required field empty",
                          "Submit form with empty required field, verify error message")
        self.add_test_item(validation, "Invalid number",
                          "Enter text in number field, verify error message")
        self.add_test_item(validation, "Invalid email",
                          "Enter invalid email, verify error message")
        self.add_test_item(validation, "Visual feedback for errors",
                          "Trigger validation error, verify field highlighted in red")
        
        # 4.2 Database Errors
        database = QTreeWidgetItem(error_category, ["4.2 Database Errors"])
        self.add_test_item(database, "Database locked",
                          "Open two instances, perform operations, verify error handling")
        self.add_test_item(database, "Database missing",
                          "Delete database file, restart app, verify auto-creation")
        
        # 4.3 Import/Export Errors
        import_export = QTreeWidgetItem(error_category, ["4.3 Import/Export Errors"])
        self.add_test_item(import_export, "Invalid file format",
                          "Try to import non-Excel file, verify error message")
        self.add_test_item(import_export, "Empty file",
                          "Import empty Excel file, verify error message")
        self.add_test_item(import_export, "Invalid data in import",
                          "Import file with invalid data, verify error report with line numbers")
        self.add_test_item(import_export, "Export permission denied",
                          "Try to export to protected folder, verify error message")
        
        self.update_progress()
    
    def add_test_item(self, parent, name: str, description: str):
        """Add a test item to the tree"""
        item = TestChecklistItem(parent, name, description)
        self.test_items.append(item)
        return item
    
    def on_item_clicked(self, item, column):
        """Handle item click"""
        if isinstance(item, TestChecklistItem):
            self.current_item = item
            self.description_text.setText(item.description)
            self.notes_text.setText(item.notes)
            self.enable_status_buttons(True)
        else:
            self.current_item = None
            self.description_text.clear()
            self.notes_text.clear()
            self.enable_status_buttons(False)
    
    def enable_status_buttons(self, enabled: bool):
        """Enable or disable status buttons"""
        self.pass_btn.setEnabled(enabled)
        self.fail_btn.setEnabled(enabled)
        self.blocked_btn.setEnabled(enabled)
        self.reset_btn.setEnabled(enabled)
    
    def set_current_status(self, status: str):
        """Set status for current item"""
        if self.current_item:
            self.current_item.notes = self.notes_text.toPlainText()
            self.current_item.set_status(status)
            self.update_progress()
            
            # Auto-advance to next item
            if status in ["Pass", "Fail", "Blocked"]:
                self.go_to_next()
    
    def go_to_next(self):
        """Go to next test item"""
        if not self.current_item:
            return
        
        current_index = self.test_items.index(self.current_item)
        if current_index < len(self.test_items) - 1:
            next_item = self.test_items[current_index + 1]
            self.tree.setCurrentItem(next_item)
            self.on_item_clicked(next_item, 0)
    
    def go_to_previous(self):
        """Go to previous test item"""
        if not self.current_item:
            return
        
        current_index = self.test_items.index(self.current_item)
        if current_index > 0:
            prev_item = self.test_items[current_index - 1]
            self.tree.setCurrentItem(prev_item)
            self.on_item_clicked(prev_item, 0)
    
    def update_progress(self):
        """Update progress bar"""
        total = len(self.test_items)
        tested = sum(1 for item in self.test_items if item.status != "Not Tested")
        
        if total > 0:
            percentage = int((tested / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{tested}/{total} tests completed ({percentage}%)")
    
    def show_summary(self):
        """Show test summary"""
        total = len(self.test_items)
        passed = sum(1 for item in self.test_items if item.status == "Pass")
        failed = sum(1 for item in self.test_items if item.status == "Fail")
        blocked = sum(1 for item in self.test_items if item.status == "Blocked")
        not_tested = sum(1 for item in self.test_items if item.status == "Not Tested")
        
        summary = f"""
Test Summary
{'='*50}

Total Test Cases: {total}
✅ Passed: {passed} ({passed/total*100:.1f}%)
❌ Failed: {failed} ({failed/total*100:.1f}%)
⚠️ Blocked: {blocked} ({blocked/total*100:.1f}%)
⬜ Not Tested: {not_tested} ({not_tested/total*100:.1f}%)

{'='*50}
"""
        
        if failed > 0:
            summary += "\n\nFailed Tests:\n"
            for item in self.test_items:
                if item.status == "Fail":
                    summary += f"  • {item.test_name}\n"
                    if item.notes:
                        summary += f"    Notes: {item.notes}\n"
        
        QMessageBox.information(self, "Test Summary", summary)
    
    def export_results(self):
        """Export test results to file"""
        from datetime import datetime
        
        filename = f"manual_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = Path(__file__).parent / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("Manual Testing Results - Hệ Thống Quản Lý Vận Tải\n")
                f.write("="*80 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                # Summary
                total = len(self.test_items)
                passed = sum(1 for item in self.test_items if item.status == "Pass")
                failed = sum(1 for item in self.test_items if item.status == "Fail")
                blocked = sum(1 for item in self.test_items if item.status == "Blocked")
                not_tested = sum(1 for item in self.test_items if item.status == "Not Tested")
                
                f.write("SUMMARY\n")
                f.write("-"*80 + "\n")
                f.write(f"Total Test Cases: {total}\n")
                f.write(f"Passed: {passed} ({passed/total*100:.1f}%)\n")
                f.write(f"Failed: {failed} ({failed/total*100:.1f}%)\n")
                f.write(f"Blocked: {blocked} ({blocked/total*100:.1f}%)\n")
                f.write(f"Not Tested: {not_tested} ({not_tested/total*100:.1f}%)\n\n")
                
                # Detailed results
                f.write("DETAILED RESULTS\n")
                f.write("-"*80 + "\n\n")
                
                for item in self.test_items:
                    status_icon = {"Pass": "✅", "Fail": "❌", "Blocked": "⚠️", "Not Tested": "⬜"}
                    f.write(f"{status_icon[item.status]} {item.test_name}\n")
                    f.write(f"   Status: {item.status}\n")
                    if item.description:
                        f.write(f"   Description: {item.description}\n")
                    if item.notes:
                        f.write(f"   Notes: {item.notes}\n")
                    f.write("\n")
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Results exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting results:\n{str(e)}")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = InteractiveTestChecklist()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
