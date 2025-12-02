"""
Integrated Main Window Demo
Demonstrates the complete integrated main window with all features
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.gui.integrated_main_window import IntegratedMainWindow
from config import DATABASE_PATH


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Transport Management System")
    app.setOrganizationName("TransportApp")
    
    # Initialize database manager
    db_manager = EnhancedDatabaseManager(DATABASE_PATH)
    
    # Create and show main window
    window = IntegratedMainWindow(db_manager)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
