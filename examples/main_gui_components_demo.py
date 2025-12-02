"""
Demo script for Main GUI Components
Demonstrates InputFormWidget, MainTableWidget, SuggestionTabWidget, 
EmployeeTabWidget, and PaginationWidget
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService
from src.services.company_price_service import CompanyPriceService
from src.models.department import Department
from src.gui.widgets import (
    InputFormWidget,
    MainTableWidget,
    SuggestionTabWidget,
    EmployeeTabWidget,
    PaginationWidget
)


class MainGUIDemo(QMainWindow):
    """Demo window for main GUI components"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Main GUI Components Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize services
        self.db_manager = EnhancedDatabaseManager("data/demo_performance.db")
        self.trip_service = TripService(self.db_manager)
        self.field_config_service = FieldConfigService(self.db_manager)
        self.company_price_service = CompanyPriceService(self.db_manager)
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for form and table
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Input Form
        self.input_form = InputFormWidget(
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            department_id=1
        )
        splitter.addWidget(self.input_form)
        
        # Right: Table and suggestions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main table
        self.main_table = MainTableWidget(trip_service=self.trip_service)
        right_layout.addWidget(self.main_table, stretch=2)
        
        # Pagination
        self.pagination = PaginationWidget(
            page_sizes=[50, 100, 200],
            default_page_size=100
        )
        right_layout.addWidget(self.pagination)
        
        # Suggestion tabs
        self.suggestion_tabs = SuggestionTabWidget(
            trip_service=self.trip_service,
            company_price_service=self.company_price_service
        )
        right_layout.addWidget(self.suggestion_tabs, stretch=1)
        
        splitter.addWidget(right_widget)
        
        # Set splitter sizes
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
        # Setup connections
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Form signals
        self.input_form.tripCreated.connect(self._on_trip_created)
        self.input_form.formDataChanged.connect(self._on_form_data_changed)
        
        # Table signals
        self.main_table.rowSelected.connect(self._on_row_selected)
        self.main_table.dataLoaded.connect(self._on_data_loaded)
        
        # Pagination signals
        self.pagination.pageChanged.connect(self._on_page_changed)
        self.pagination.pageSizeChanged.connect(self._on_page_size_changed)
        
        # Suggestion signals
        self.suggestion_tabs.suggestionSelected.connect(self._on_suggestion_selected)
    
    def _load_initial_data(self):
        """Load initial data"""
        # Load first page
        self.main_table.load_data(page=1, page_size=100)
        
        # Load company prices
        self.suggestion_tabs.load_all_company_prices()
    
    def _on_trip_created(self, trip_data):
        """Handle trip creation"""
        print(f"Trip created: {trip_data.get('ma_chuyen')}")
        # Reload table
        self.main_table.refresh_data()
        # Update pagination
        self._update_pagination()
    
    def _on_form_data_changed(self, data):
        """Handle form data changes"""
        # Update suggestions based on form data
        filters = {}
        if data.get('khach_hang'):
            filters['khach_hang'] = data['khach_hang']
        if data.get('diem_di'):
            filters['diem_di'] = data['diem_di']
        if data.get('diem_den'):
            filters['diem_den'] = data['diem_den']
        
        if filters:
            self.suggestion_tabs.update_filtered_results(filters)
    
    def _on_row_selected(self, row_data):
        """Handle table row selection"""
        print(f"Row selected: {row_data.get('ma_chuyen')}")
        # Load into form for editing
        self.input_form.load_trip_data(row_data)
    
    def _on_data_loaded(self, row_count):
        """Handle data loaded"""
        print(f"Data loaded: {row_count} rows")
        self._update_pagination()
    
    def _on_page_changed(self, page):
        """Handle page change"""
        print(f"Page changed to: {page}")
        page_size = self.pagination.get_page_size()
        self.main_table.load_data(page=page, page_size=page_size)
    
    def _on_page_size_changed(self, page_size):
        """Handle page size change"""
        print(f"Page size changed to: {page_size}")
        self.main_table.load_data(page=1, page_size=page_size)
    
    def _on_suggestion_selected(self, suggestion_data):
        """Handle suggestion selection"""
        print(f"Suggestion selected: {suggestion_data}")
        # Fill form with suggestion
        for field_name, value in suggestion_data.items():
            self.input_form.set_field_value(field_name, value)
    
    def _update_pagination(self):
        """Update pagination widget"""
        total_records = self.main_table.get_total_records()
        self.pagination.set_total_records(total_records)


class EmployeeTabDemo(QMainWindow):
    """Demo window for employee tab widget"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Employee Tab Widget Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize services
        self.db_manager = EnhancedDatabaseManager("data/demo_performance.db")
        self.trip_service = TripService(self.db_manager)
        self.field_config_service = FieldConfigService(self.db_manager)
        self.company_price_service = CompanyPriceService(self.db_manager)
        
        # Create sample departments
        self.departments = [
            Department(id=1, name="sales", display_name="Phòng Kinh Doanh", is_active=True),
            Department(id=2, name="processing", display_name="Phòng Xử Lý", is_active=True),
            Department(id=3, name="accounting", display_name="Phòng Kế Toán", is_active=True),
        ]
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Employee tab widget
        self.employee_tabs = EmployeeTabWidget(
            departments=self.departments,
            trip_service=self.trip_service,
            field_config_service=self.field_config_service,
            company_price_service=self.company_price_service
        )
        
        main_layout.addWidget(self.employee_tabs)
        
        # Setup connections
        self.employee_tabs.departmentChanged.connect(self._on_department_changed)
        self.employee_tabs.tripCreated.connect(self._on_trip_created)
    
    def _on_department_changed(self, department_id):
        """Handle department change"""
        print(f"Department changed to: {department_id}")
    
    def _on_trip_created(self, dept_id, trip_data):
        """Handle trip creation"""
        print(f"Trip created in department {dept_id}: {trip_data.get('ma_chuyen')}")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Show main GUI demo
    demo1 = MainGUIDemo()
    demo1.show()
    
    # Show employee tab demo
    demo2 = EmployeeTabDemo()
    demo2.move(demo1.x() + demo1.width() + 20, demo1.y())
    demo2.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
