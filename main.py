"""
Main entry point for Transport Management System
Hệ Thống Quản Lý Vận Tải Toàn Diện
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

import config
from src.utils.logger import setup_logging, get_logger


def main():
    """
    Main application entry point
    """
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info("=" * 60)

    try:
        # Create Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName(config.APP_NAME)
        app.setApplicationVersion(config.APP_VERSION)
        app.setOrganizationName(config.APP_ORGANIZATION)

        # Note: High DPI scaling is enabled by default in PyQt6
        # AA_UseHighDpiPixmaps has been removed in PyQt6

        logger.info("Application initialized successfully")

        # Initialize database manager
        from src.database.enhanced_db_manager import EnhancedDatabaseManager
        db_manager = EnhancedDatabaseManager(config.DATABASE_PATH)
        logger.info("Database manager initialized")

        # Create and show main window
        from src.gui.integrated_main_window import IntegratedMainWindow
        main_window = IntegratedMainWindow(db_manager)
        main_window.show()

        logger.info("Main window created and displayed")
        logger.info("Application ready")

        # Start event loop
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
