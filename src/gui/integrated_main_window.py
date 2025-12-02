"""
Integrated Main Window Module
Main application window integrating all components with menu bar, toolbar, and status bar
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox, QFileDialog,
    QLabel, QApplication
)
from PyQt6.QtCore import Qt, QSettings, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService
from src.services.company_price_service import CompanyPriceService
from src.services.excel_service import ExcelService
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.department import Department
from src.gui.widgets.employee_tab_widget import EmployeeTabWidget
from src.gui.widgets.pagination_widget import PaginationWidget


class IntegratedMainWindow(QMainWindow):
    """
    Integrated main window for the Transport Management System
    
    Features:
    - Menu bar with File, Edit, View, Tools, Department, Help menus
    - Toolbar with common actions
    - Status bar with record counts
    - Responsive layout with QSplitter
    - Window state persistence
    - Multi-department support via tabs
    """
    
    # Signals
    windowClosing = pyqtSignal()
    
    def __init__(self, db_manager: EnhancedDatabaseManager, parent=None):
        """
        Initialize integrated main window
        
        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        
        # Initialize services
        self.trip_service = TripService(db_manager)
        self.field_config_service = FieldConfigService(db_manager)
        self.company_price_service = CompanyPriceService(db_manager)
        self.excel_service = ExcelService(db_manager)
        
        # Load departments
        self.departments = self._load_departments()
        
        # Settings for window state persistence
        self.settings = QSettings("TransportApp", "MainWindow")
        
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._setup_connections()
        self._restore_window_state()
        
        # Set window properties
        self.setWindowTitle("Hệ Thống Quản Lý Vận Tải Toàn Diện")
        self.setMinimumSize(1200, 800)
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Employee tab widget (multi-department)
        self.employee_tabs = EmployeeTabWidget(
            departments=self.departments,
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            company_price_service=self.company_price_service
        )
        main_layout.addWidget(self.employee_tabs)
        
        # Pagination widget
        self.pagination_widget = PaginationWidget()
        main_layout.addWidget(self.pagination_widget)
    
    def _load_departments(self) -> List[Department]:
        """Load departments from database"""
        try:
            query = """
                SELECT id, name, display_name, description, is_active, created_at
                FROM departments
                WHERE is_active = 1
                ORDER BY id
            """
            rows = self.db_manager.fetch_all(query)
            
            departments = []
            for row in rows:
                dept = Department(
                    id=row[0],
                    name=row[1],
                    display_name=row[2],
                    description=row[3],
                    is_active=bool(row[4]),
                    created_at=row[5]
                )
                departments.append(dept)
            
            return departments if departments else self._get_default_departments()
            
        except Exception as e:
            print(f"Error loading departments: {e}")
            return self._get_default_departments()
    
    def _get_default_departments(self) -> List[Department]:
        """Get default departments if none exist"""
        return [
            Department(
                id=1,
                name="sales",
                display_name="Kinh Doanh",
                description="Phòng Kinh Doanh",
                is_active=True
            ),
            Department(
                id=2,
                name="processing",
                display_name="Điều Hành",
                description="Phòng Điều Hành",
                is_active=True
            ),
            Department(
                id=3,
                name="accounting",
                display_name="Kế Toán",
                description="Phòng Kế Toán",
                is_active=True
            )
        ]
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setStatusTip("Create new record")
        self.new_action.triggered.connect(self._on_new_record)
        file_menu.addAction(self.new_action)
        
        file_menu.addSeparator()
        
        self.import_action = QAction("&Import Excel...", self)
        self.import_action.setShortcut(QKeySequence("Ctrl+I"))
        self.import_action.setStatusTip("Import data from Excel")
        self.import_action.triggered.connect(self._on_import_excel)
        file_menu.addAction(self.import_action)
        
        self.export_action = QAction("&Export Excel...", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.setStatusTip("Export data to Excel")
        self.export_action.triggered.connect(self._on_export_excel)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit application")
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Copy selected cells")
        self.copy_action.triggered.connect(self._on_copy)
        edit_menu.addAction(self.copy_action)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setStatusTip("Paste cells")
        self.paste_action.triggered.connect(self._on_paste)
        edit_menu.addAction(self.paste_action)
        
        edit_menu.addSeparator()
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Delete selected rows")
        self.delete_action.triggered.connect(self._on_delete)
        edit_menu.addAction(self.delete_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        self.column_visibility_action = QAction("Column &Visibility...", self)
        self.column_visibility_action.setStatusTip("Show/hide columns")
        self.column_visibility_action.triggered.connect(self._on_column_visibility)
        view_menu.addAction(self.column_visibility_action)
        
        self.filters_action = QAction("&Filters", self)
        self.filters_action.setCheckable(True)
        self.filters_action.setChecked(True)
        self.filters_action.setStatusTip("Show/hide filters")
        self.filters_action.triggered.connect(self._on_toggle_filters)
        view_menu.addAction(self.filters_action)
        
        view_menu.addSeparator()
        
        self.refresh_action = QAction("&Refresh", self)
        self.refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.refresh_action.setStatusTip("Refresh data")
        self.refresh_action.triggered.connect(self._on_refresh)
        view_menu.addAction(self.refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        self.field_manager_action = QAction("&Field Manager...", self)
        self.field_manager_action.setStatusTip("Manage field configurations")
        self.field_manager_action.triggered.connect(self._on_field_manager)
        tools_menu.addAction(self.field_manager_action)
        
        self.formula_builder_action = QAction("F&ormula Builder...", self)
        self.formula_builder_action.setStatusTip("Build and test formulas")
        self.formula_builder_action.triggered.connect(self._on_formula_builder)
        tools_menu.addAction(self.formula_builder_action)
        
        self.push_conditions_action = QAction("&Push Conditions...", self)
        self.push_conditions_action.setStatusTip("Configure push conditions")
        self.push_conditions_action.triggered.connect(self._on_push_conditions)
        tools_menu.addAction(self.push_conditions_action)
        
        tools_menu.addSeparator()
        
        self.workspace_manager_action = QAction("&Workspace Manager...", self)
        self.workspace_manager_action.setStatusTip("Manage workspaces")
        self.workspace_manager_action.triggered.connect(self._on_workspace_manager)
        tools_menu.addAction(self.workspace_manager_action)
        
        tools_menu.addSeparator()
        
        self.preset_export_import_action = QAction("Preset Export/&Import...", self)
        self.preset_export_import_action.setStatusTip("Export/Import presets")
        self.preset_export_import_action.triggered.connect(self._on_preset_export_import)
        tools_menu.addAction(self.preset_export_import_action)
        
        tools_menu.addSeparator()
        
        self.statistics_action = QAction("&Statistics...", self)
        self.statistics_action.setStatusTip("View statistics")
        self.statistics_action.triggered.connect(self._on_statistics)
        tools_menu.addAction(self.statistics_action)
        
        self.workflow_history_action = QAction("Workflow &History...", self)
        self.workflow_history_action.setStatusTip("View workflow history")
        self.workflow_history_action.triggered.connect(self._on_workflow_history)
        tools_menu.addAction(self.workflow_history_action)
        
        # Department menu
        department_menu = menubar.addMenu("&Department")
        
        # Add action for each department
        for dept in self.departments:
            action = QAction(dept.display_name or dept.name, self)
            action.setStatusTip(f"Switch to {dept.display_name or dept.name}")
            action.triggered.connect(
                lambda checked, dept_id=dept.id: self._on_switch_department(dept_id)
            )
            department_menu.addAction(action)
        
        department_menu.addSeparator()
        
        self.department_settings_action = QAction("Department &Settings...", self)
        self.department_settings_action.setStatusTip("Configure department settings")
        self.department_settings_action.triggered.connect(self._on_department_settings)
        department_menu.addAction(self.department_settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.user_manual_action = QAction("&User Manual", self)
        self.user_manual_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.user_manual_action.setStatusTip("Open user manual")
        self.user_manual_action.triggered.connect(self._on_user_manual)
        help_menu.addAction(self.user_manual_action)
        
        help_menu.addSeparator()
        
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("About this application")
        self.about_action.triggered.connect(self._on_about)
        help_menu.addAction(self.about_action)
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # New record button
        new_button = QAction("New", self)
        new_button.setStatusTip("Create new record")
        new_button.triggered.connect(self._on_new_record)
        toolbar.addAction(new_button)
        
        toolbar.addSeparator()
        
        # Import button
        import_button = QAction("Import", self)
        import_button.setStatusTip("Import from Excel")
        import_button.triggered.connect(self._on_import_excel)
        toolbar.addAction(import_button)
        
        # Export button
        export_button = QAction("Export", self)
        export_button.setStatusTip("Export to Excel")
        export_button.triggered.connect(self._on_export_excel)
        toolbar.addAction(export_button)
        
        toolbar.addSeparator()
        
        # Filter toggle button
        filter_button = QAction("Filters", self)
        filter_button.setCheckable(True)
        filter_button.setChecked(True)
        filter_button.setStatusTip("Toggle filters")
        filter_button.triggered.connect(self._on_toggle_filters)
        toolbar.addAction(filter_button)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_button = QAction("Settings", self)
        settings_button.setStatusTip("Open settings")
        settings_button.triggered.connect(self._on_settings)
        toolbar.addAction(settings_button)
        
        # Refresh button
        refresh_button = QAction("Refresh", self)
        refresh_button.setStatusTip("Refresh data")
        refresh_button.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_button)
        
        self.toolbar = toolbar
    
    def _create_status_bar(self):
        """Create status bar"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        # Record count label
        self.record_count_label = QLabel("Records: 0")
        statusbar.addPermanentWidget(self.record_count_label)
        
        # Department label
        self.department_label = QLabel("")
        statusbar.addPermanentWidget(self.department_label)
        
        # Status message
        statusbar.showMessage("Ready")
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Employee tabs signals
        self.employee_tabs.departmentChanged.connect(self._on_department_changed)
        self.employee_tabs.tripCreated.connect(self._on_trip_created)
        self.employee_tabs.tripUpdated.connect(self._on_trip_updated)
        
        # Pagination signals
        self.pagination_widget.pageChanged.connect(self._on_page_changed)
        self.pagination_widget.pageSizeChanged.connect(self._on_page_size_changed)
    
    def _on_department_changed(self, department_id: int):
        """Handle department change"""
        # Find department
        dept = next((d for d in self.departments if d.id == department_id), None)
        if dept:
            self.department_label.setText(f"Department: {dept.display_name or dept.name}")
            self._update_record_count()
    
    def _on_trip_created(self, dept_id: int, trip_data: Dict[str, Any]):
        """Handle trip creation"""
        self.statusBar().showMessage(f"Created trip: {trip_data.get('ma_chuyen', '')}", 3000)
        self._update_record_count()
    
    def _on_trip_updated(self, dept_id: int, trip_data: Dict[str, Any]):
        """Handle trip update"""
        self.statusBar().showMessage(f"Updated trip: {trip_data.get('ma_chuyen', '')}", 3000)
    
    def _on_page_changed(self, page: int):
        """Handle page change"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.main_table.load_data(page=page)
    
    def _on_page_size_changed(self, page_size: int):
        """Handle page size change"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.main_table.set_page_size(page_size)
            self._update_pagination()
    
    def _update_record_count(self):
        """Update record count in status bar"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            total = current_widget.main_table.get_total_records()
            self.record_count_label.setText(f"Records: {total}")
            self._update_pagination()
    
    def _update_pagination(self):
        """Update pagination widget"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            total = current_widget.main_table.get_total_records()
            page_size = current_widget.main_table.get_page_size()
            current_page = current_widget.main_table.get_current_page()
            
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
            self.pagination_widget.set_total_pages(total_pages)
            self.pagination_widget.set_current_page(current_page)
    
    # Menu action handlers
    def _on_new_record(self):
        """Handle new record action"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.input_form.clear_form()
            current_widget.input_form.setFocus()
    
    def _on_import_excel(self):
        """Handle import Excel action"""
        from src.gui.dialogs.excel_import_dialog import ExcelImportDialog
        
        try:
            dialog = ExcelImportDialog(self.excel_service, self)
            dialog.importCompleted.connect(self._on_import_completed)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))
    
    def _on_export_excel(self):
        """Handle export Excel action"""
        from src.gui.dialogs.excel_export_dialog import ExcelExportDialog
        
        try:
            # Get current department widget
            current_widget = self.employee_tabs.get_current_department_widget()
            if not current_widget:
                QMessageBox.warning(self, "No Data", "No department selected.")
                return
            
            # Get all trips
            all_trips = current_widget.main_table.get_all_trips()
            
            # Get filtered trips (if any filters applied)
            filtered_trips = current_widget.main_table.get_filtered_trips()
            
            # Get selected trips
            selected_trips = current_widget.main_table.get_selected_trips()
            
            # Show export dialog
            dialog = ExcelExportDialog(
                self.excel_service,
                all_trips,
                filtered_trips,
                selected_trips,
                self
            )
            dialog.exportCompleted.connect(self._on_export_completed)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
    
    def _on_copy(self):
        """Handle copy action"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.main_table.table.copy_selected_cells()
    
    def _on_paste(self):
        """Handle paste action"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.main_table.table.paste_cells()
    
    def _on_delete(self):
        """Handle delete action"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            selected_rows = current_widget.main_table.table.get_selected_rows()
            if selected_rows:
                current_widget.main_table._on_row_deleted(selected_rows)
    
    def _on_column_visibility(self):
        """Handle column visibility action"""
        current_widget = self.employee_tabs.get_current_department_widget()
        if current_widget:
            current_widget.main_table.table.show_column_visibility_dialog()
    
    def _on_toggle_filters(self, checked: bool):
        """Handle toggle filters action"""
        # TODO: Implement filter panel toggle
        pass
    
    def _on_refresh(self):
        """Handle refresh action"""
        self.employee_tabs.refresh_current_department()
        self._update_record_count()
        self.statusBar().showMessage("Data refreshed", 2000)
    
    def _on_field_manager(self):
        """Handle field manager action"""
        from src.gui.dialogs.field_manager_dialog import FieldManagerDialog
        
        dept_id = self.employee_tabs.get_current_department_id()
        if dept_id:
            dialog = FieldManagerDialog(self.field_config_service, dept_id, self)
            if dialog.exec():
                # Reload field configurations
                current_widget = self.employee_tabs.get_current_department_widget()
                if current_widget:
                    current_widget.input_form.reload_field_configurations()
    
    def _on_formula_builder(self):
        """Handle formula builder action"""
        from src.gui.dialogs.formula_builder_dialog import FormulaBuilderDialog
        
        dept_id = self.employee_tabs.get_current_department_id()
        if dept_id:
            dialog = FormulaBuilderDialog(self.db_manager, dept_id, self)
            dialog.exec()
    
    def _on_push_conditions(self):
        """Handle push conditions action"""
        from src.gui.dialogs.push_conditions_dialog import PushConditionsDialog
        
        dept_id = self.employee_tabs.get_current_department_id()
        if dept_id:
            dialog = PushConditionsDialog(self.db_manager, dept_id, self)
            dialog.exec()
    
    def _on_workspace_manager(self):
        """Handle workspace manager action"""
        from src.gui.dialogs.workspace_manager_dialog import WorkspaceManagerDialog
        
        dialog = WorkspaceManagerDialog(self.db_manager, self)
        dialog.exec()
    
    def _on_preset_export_import(self):
        """Handle preset export/import action"""
        from src.gui.dialogs.preset_export_import_dialog import PresetExportImportDialog
        
        dept_id = self.employee_tabs.get_current_department_id()
        if dept_id:
            dialog = PresetExportImportDialog(self.db_manager, dept_id, self)
            dialog.presetImported.connect(self._on_preset_imported)
            dialog.exec()
    
    def _on_preset_imported(self, imported_counts: Dict[str, int]):
        """Handle preset import completion"""
        # Refresh current department to reflect imported configurations
        self.employee_tabs.refresh_current_department()
        self.statusBar().showMessage("Preset imported successfully", 5000)
    
    def _on_statistics(self):
        """Handle statistics action"""
        from src.gui.dialogs.statistics_dialog import StatisticsDialog
        
        dialog = StatisticsDialog(self.db_manager, self)
        dialog.exec()
    
    def _on_workflow_history(self):
        """Handle workflow history action"""
        from src.gui.dialogs.workflow_history_dialog import WorkflowHistoryDialog
        
        dialog = WorkflowHistoryDialog(self.db_manager, self)
        dialog.exec()
    
    def _on_switch_department(self, department_id: int):
        """Handle switch department action"""
        self.employee_tabs.switch_to_department(department_id)
    
    def _on_department_settings(self):
        """Handle department settings action"""
        QMessageBox.information(
            self,
            "Department Settings",
            "Department settings dialog (to be implemented)"
        )
    
    def _on_settings(self):
        """Handle settings action"""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog (to be implemented)"
        )
    
    def _on_user_manual(self):
        """Handle user manual action"""
        QMessageBox.information(
            self,
            "User Manual",
            "User manual (to be implemented)"
        )
    
    def _on_about(self):
        """Handle about action"""
        QMessageBox.about(
            self,
            "About Transport Management System",
            "<h3>Hệ Thống Quản Lý Vận Tải Toàn Diện</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A comprehensive transport management system with dynamic forms, "
            "formula engine, and workflow automation.</p>"
            "<p>© 2024 Transport Management System</p>"
        )
    
    def _on_import_completed(self, result: Dict[str, Any]):
        """Handle import completion"""
        # Refresh current department data
        self.employee_tabs.refresh_current_department()
        self._update_record_count()
        
        # Show status message
        success_count = result.get('success_count', 0)
        self.statusBar().showMessage(f"Imported {success_count} records", 5000)
    
    def _on_export_completed(self, file_path: str):
        """Handle export completion"""
        self.statusBar().showMessage(f"Exported to {file_path}", 5000)
    
    def _restore_window_state(self):
        """Restore window state from settings"""
        # Restore geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore window state
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        
        # Restore last department
        last_dept_id = self.settings.value("lastDepartmentId", type=int)
        if last_dept_id:
            self.employee_tabs.switch_to_department(last_dept_id)
    
    def _save_window_state(self):
        """Save window state to settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save current department
        dept_id = self.employee_tabs.get_current_department_id()
        if dept_id:
            self.settings.setValue("lastDepartmentId", dept_id)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self._save_window_state()
        
        # Emit signal
        self.windowClosing.emit()
        
        # Accept event
        event.accept()
    
    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        
        # Load initial data
        if not hasattr(self, '_initial_load_done'):
            self._initial_load_done = True
            self._update_record_count()
            
            # Set initial department label
            dept_id = self.employee_tabs.get_current_department_id()
            if dept_id:
                dept = next((d for d in self.departments if d.id == dept_id), None)
                if dept:
                    self.department_label.setText(f"Department: {dept.display_name or dept.name}")
