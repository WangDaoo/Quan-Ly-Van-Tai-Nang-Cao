"""
Autocomplete System Demo
Demonstrates the autocomplete functionality with fuzzy search, debouncing, and caching
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, '.')

from src.gui.widgets import AutocompleteComboBox, AutocompleteIntegration
from src.services import AutocompleteService
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from config import DATABASE_PATH


class AutocompleteDemo(QMainWindow):
    """Demo window for autocomplete functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autocomplete System Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize database and services
        self.db_manager = EnhancedDatabaseManager(DATABASE_PATH)
        self.autocomplete_service = AutocompleteService(self.db_manager)
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Autocomplete System Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "This demo shows the autocomplete functionality with:\n"
            "• Fuzzy search in dropdown\n"
            "• Keyboard navigation (Arrow keys, Enter, Escape)\n"
            "• Debounced search (300ms)\n"
            "• Caching for performance"
        )
        desc.setStyleSheet("color: #666;")
        main_layout.addWidget(desc)
        
        # Autocomplete fields group
        fields_group = QGroupBox("Autocomplete Fields")
        fields_layout = QFormLayout()
        fields_layout.setSpacing(15)
        
        # Customer autocomplete
        self.customer_combo = AutocompleteComboBox()
        self.customer_combo.set_data_loader(self.autocomplete_service.get_customers)
        self.customer_combo.set_debounce_delay(300)
        self.customer_combo.set_cache_enabled(True)
        self.customer_combo.textChanged.connect(
            lambda text: self.log_event(f"Customer text changed: {text}")
        )
        self.customer_combo.itemSelected.connect(
            lambda text: self.log_event(f"Customer selected: {text}")
        )
        fields_layout.addRow("Khách hàng:", self.customer_combo)
        
        # Departure location autocomplete
        self.departure_combo = AutocompleteComboBox()
        self.departure_combo.set_data_loader(self.autocomplete_service.get_departure_locations)
        self.departure_combo.set_debounce_delay(300)
        self.departure_combo.set_cache_enabled(True)
        self.departure_combo.textChanged.connect(
            lambda text: self.log_event(f"Departure text changed: {text}")
        )
        self.departure_combo.itemSelected.connect(
            lambda text: self.log_event(f"Departure selected: {text}")
        )
        fields_layout.addRow("Điểm đi:", self.departure_combo)
        
        # Destination location autocomplete
        self.destination_combo = AutocompleteComboBox()
        self.destination_combo.set_data_loader(self.autocomplete_service.get_destination_locations)
        self.destination_combo.set_debounce_delay(300)
        self.destination_combo.set_cache_enabled(True)
        self.destination_combo.textChanged.connect(
            lambda text: self.log_event(f"Destination text changed: {text}")
        )
        self.destination_combo.itemSelected.connect(
            lambda text: self.log_event(f"Destination selected: {text}")
        )
        fields_layout.addRow("Điểm đến:", self.destination_combo)
        
        fields_group.setLayout(fields_layout)
        main_layout.addWidget(fields_group)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(refresh_btn)
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        buttons_layout.addWidget(clear_cache_btn)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        buttons_layout.addWidget(clear_log_btn)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Event log
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "• Type in any field to see fuzzy search suggestions\n"
            "• Use Arrow keys to navigate, Enter to select, Escape to close\n"
            "• Notice the 300ms debounce delay for text changes\n"
            "• Data is cached for performance"
        )
        instructions.setStyleSheet("color: #666; font-size: 11px;")
        main_layout.addWidget(instructions)
    
    def load_data(self):
        """Load initial data into autocomplete widgets"""
        self.log_event("Loading data...")
        
        # Load data for each widget
        self.customer_combo.load_data()
        self.departure_combo.load_data()
        self.destination_combo.load_data()
        
        # Log statistics
        customer_count = len(self.customer_combo.get_cached_items())
        departure_count = len(self.departure_combo.get_cached_items())
        destination_count = len(self.destination_combo.get_cached_items())
        
        self.log_event(f"Loaded {customer_count} customers")
        self.log_event(f"Loaded {departure_count} departure locations")
        self.log_event(f"Loaded {destination_count} destination locations")
        self.log_event("Data loaded successfully!")
    
    def refresh_data(self):
        """Refresh data from database"""
        self.log_event("Refreshing data from database...")
        
        # Clear service cache
        self.autocomplete_service.clear_cache()
        
        # Clear widget caches
        self.customer_combo.clear_cache()
        self.departure_combo.clear_cache()
        self.destination_combo.clear_cache()
        
        # Reload data
        self.load_data()
    
    def clear_cache(self):
        """Clear all caches"""
        self.log_event("Clearing all caches...")
        
        self.autocomplete_service.clear_cache()
        self.customer_combo.clear_cache()
        self.departure_combo.clear_cache()
        self.destination_combo.clear_cache()
        
        self.log_event("Caches cleared!")
    
    def clear_log(self):
        """Clear the event log"""
        self.log_text.clear()
    
    def log_event(self, message: str):
        """Log an event to the log text area"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show demo window
    demo = AutocompleteDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
