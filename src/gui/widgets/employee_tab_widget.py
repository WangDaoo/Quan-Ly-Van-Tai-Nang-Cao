"""
Employee Tab Widget Module
Tab widget for multi-department support with independent forms and tables
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QSplitter, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from typing import List, Dict, Any, Optional

from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService
from src.services.company_price_service import CompanyPriceService
from src.services.filtering_service import FilteringService
from src.models.department import Department
from .input_form_widget import InputFormWidget
from .main_table_widget import MainTableWidget
from .suggestion_tab_widget import SuggestionTabWidget


class DepartmentWidget(QWidget):
    """
    Widget for a single department containing form, table, and suggestions
    """
    
    # Signals
    tripCreated = pyqtSignal(dict)
    tripUpdated = pyqtSignal(dict)
    dataChanged = pyqtSignal(int, dict)
    
    def __init__(self,
                 department: Department,
                 trip_service: TripService,
                 field_config_service: FieldConfigService,
                 company_price_service: CompanyPriceService,
                 parent=None):
        """
        Initialize department widget
        
        Args:
            department: Department model
            trip_service: TripService instance
            field_config_service: FieldConfigService instance
            company_price_service: CompanyPriceService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.department = department
        self.trip_service = trip_service
        self.field_config_service = field_config_service
        self.company_price_service = company_price_service
        self.filtering_service = FilteringService(debounce_ms=300)
        
        # Debounce timer for filtering
        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(300)  # 300ms debounce
        self._filter_timer.timeout.connect(self._perform_filtering)
        self._pending_filters = {}
        
        self._setup_ui()
        self._setup_connections()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for form and table
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Input form
        self.input_form = InputFormWidget(
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            department_id=self.department.id
        )
        main_splitter.addWidget(self.input_form)
        
        # Right side: Table and suggestions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main table
        self.main_table = MainTableWidget(trip_service=self.trip_service)
        right_layout.addWidget(self.main_table, stretch=2)
        
        # Suggestion tabs
        self.suggestion_tabs = SuggestionTabWidget(
            trip_service=self.trip_service,
            company_price_service=self.company_price_service
        )
        right_layout.addWidget(self.suggestion_tabs, stretch=1)
        
        main_splitter.addWidget(right_widget)
        
        # Set splitter sizes (30% form, 70% table+suggestions)
        main_splitter.setSizes([300, 700])
        
        main_layout.addWidget(main_splitter)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Form signals
        self.input_form.tripCreated.connect(self._on_trip_created)
        self.input_form.tripUpdated.connect(self._on_trip_updated)
        # Connect to underlying form widget's signal
        self.input_form.form_widget.formDataChanged.connect(self._on_form_data_changed)
        
        # Table signals
        self.main_table.rowSelected.connect(self._on_row_selected)
        self.main_table.dataChanged.connect(self._on_data_changed)
        
        # Suggestion signals
        self.suggestion_tabs.suggestionSelected.connect(self._on_suggestion_selected)
    
    def _load_initial_data(self):
        """Load initial data"""
        # Load table data
        self.main_table.load_data()
        
        # Load company prices
        self.suggestion_tabs.load_all_company_prices()
    
    def _on_trip_created(self, trip_data: Dict[str, Any]):
        """Handle trip creation"""
        # Refresh table
        self.main_table.refresh_data()
        
        # Emit signal
        self.tripCreated.emit(trip_data)
    
    def _on_trip_updated(self, trip_data: Dict[str, Any]):
        """Handle trip update"""
        # Refresh table
        self.main_table.refresh_data()
        
        # Emit signal
        self.tripUpdated.emit(trip_data)
    
    def _on_form_data_changed(self, data: Dict[str, Any]):
        """
        Handle form data changes - update suggestions with debouncing
        
        Implements:
        - Debounced filtering (300ms) (Requirement 2.4)
        - Real-time update of suggestion tables (Requirement 3.1, 3.5)
        """
        # Extract filter criteria
        filters = {}
        
        if 'khach_hang' in data and data['khach_hang']:
            filters['khach_hang'] = data['khach_hang']
        if 'diem_di' in data and data['diem_di']:
            filters['diem_di'] = data['diem_di']
        if 'diem_den' in data and data['diem_den']:
            filters['diem_den'] = data['diem_den']
        
        # Store pending filters
        self._pending_filters = filters
        
        # Restart debounce timer
        self._filter_timer.stop()
        
        # If filters are empty, clear immediately
        if not filters:
            self.suggestion_tabs.clear_all_tabs()
            self.suggestion_tabs.load_all_company_prices()
        else:
            self._filter_timer.start()
    
    def _perform_filtering(self):
        """Perform the actual filtering after debounce"""
        if self._pending_filters:
            self.suggestion_tabs.update_filtered_results(self._pending_filters)
    
    def clear_filters(self):
        """Clear all filters"""
        self._pending_filters = {}
        self._filter_timer.stop()
        self.suggestion_tabs.clear_all_tabs()
        self.suggestion_tabs.load_all_company_prices()
    
    def _on_row_selected(self, row_data: Dict[str, Any]):
        """Handle table row selection - load into form"""
        self.input_form.load_trip_data(row_data)
    
    def _on_data_changed(self, trip_id: int, data: Dict[str, Any]):
        """Handle data change in table"""
        self.dataChanged.emit(trip_id, data)
    
    def _on_suggestion_selected(self, suggestion_data: Dict[str, Any]):
        """Handle suggestion selection - fill form"""
        # Fill form with suggestion data
        for field_name, value in suggestion_data.items():
            self.input_form.set_field_value(field_name, value)
    
    def refresh_data(self):
        """Refresh all data"""
        self.main_table.refresh_data()
        self.suggestion_tabs.load_all_company_prices()
    
    def get_department(self) -> Department:
        """Get the department"""
        return self.department


class EmployeeTabWidget(QWidget):
    """
    Employee tab widget for multi-department support
    Each department has its own tab with independent form and table
    
    Features:
    - Tab per department
    - Independent form and table for each tab
    - Tab switching with data persistence
    - Department-specific field configurations
    """
    
    # Signals
    departmentChanged = pyqtSignal(int)  # Emitted when department tab changes
    tripCreated = pyqtSignal(int, dict)  # Emitted when trip is created (dept_id, data)
    tripUpdated = pyqtSignal(int, dict)  # Emitted when trip is updated (dept_id, data)
    
    def __init__(self,
                 departments: List[Department],
                 trip_service: TripService,
                 field_config_service: FieldConfigService,
                 company_price_service: CompanyPriceService,
                 parent=None):
        """
        Initialize employee tab widget
        
        Args:
            departments: List of Department models
            trip_service: TripService instance
            field_config_service: FieldConfigService instance
            company_price_service: CompanyPriceService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.departments = departments
        self.trip_service = trip_service
        self.field_config_service = field_config_service
        self.company_price_service = company_price_service
        
        self._department_widgets: Dict[int, DepartmentWidget] = {}
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tab for each department
        for department in self.departments:
            if department.is_active:
                self._add_department_tab(department)
        
        main_layout.addWidget(self.tab_widget)
    
    def _add_department_tab(self, department: Department):
        """Add a tab for a department"""
        # Create department widget
        dept_widget = DepartmentWidget(
            department=department,
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            company_price_service=self.company_price_service
        )
        
        # Store reference
        self._department_widgets[department.id] = dept_widget
        
        # Add tab
        tab_name = department.display_name or department.name
        self.tab_widget.addTab(dept_widget, tab_name)
        
        # Connect signals
        dept_widget.tripCreated.connect(
            lambda data, dept_id=department.id: self.tripCreated.emit(dept_id, data)
        )
        dept_widget.tripUpdated.connect(
            lambda data, dept_id=department.id: self.tripUpdated.emit(dept_id, data)
        )
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        if index >= 0:
            # Get department ID for current tab
            dept_widget = self.tab_widget.widget(index)
            if isinstance(dept_widget, DepartmentWidget):
                self.departmentChanged.emit(dept_widget.department.id)
    
    def get_current_department_id(self) -> Optional[int]:
        """Get current department ID"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, DepartmentWidget):
            return current_widget.department.id
        return None
    
    def get_current_department_widget(self) -> Optional[DepartmentWidget]:
        """Get current department widget"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, DepartmentWidget):
            return current_widget
        return None
    
    def get_department_widget(self, department_id: int) -> Optional[DepartmentWidget]:
        """Get department widget by ID"""
        return self._department_widgets.get(department_id)
    
    def switch_to_department(self, department_id: int):
        """
        Switch to a specific department tab
        
        Args:
            department_id: Department ID to switch to
        """
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, DepartmentWidget) and widget.department.id == department_id:
                self.tab_widget.setCurrentIndex(i)
                break
    
    def refresh_current_department(self):
        """Refresh data for current department"""
        current_widget = self.get_current_department_widget()
        if current_widget:
            current_widget.refresh_data()
    
    def refresh_all_departments(self):
        """Refresh data for all departments"""
        for dept_widget in self._department_widgets.values():
            dept_widget.refresh_data()
    
    def add_department(self, department: Department):
        """
        Add a new department tab
        
        Args:
            department: Department model
        """
        if department.id not in self._department_widgets:
            self._add_department_tab(department)
            self.departments.append(department)
    
    def remove_department(self, department_id: int):
        """
        Remove a department tab
        
        Args:
            department_id: Department ID to remove
        """
        if department_id in self._department_widgets:
            # Find and remove tab
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if isinstance(widget, DepartmentWidget) and widget.department.id == department_id:
                    self.tab_widget.removeTab(i)
                    break
            
            # Remove from dictionary
            del self._department_widgets[department_id]
            
            # Remove from departments list
            self.departments = [d for d in self.departments if d.id != department_id]
    
    def get_all_department_ids(self) -> List[int]:
        """Get list of all department IDs"""
        return list(self._department_widgets.keys())
    
    def get_tab_count(self) -> int:
        """Get number of tabs"""
        return self.tab_widget.count()
