"""
Excel Import Dialog Module
Provides preview dialog with data validation, duplicate handling options,
progress bar, and error reporting with line numbers
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QProgressBar, QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
    QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Dict, Any, List, Optional
import logging

from src.services.excel_service import ExcelService, DuplicateHandling


logger = logging.getLogger(__name__)


class ImportWorker(QThread):
    """Worker thread for Excel import operation"""
    
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(dict)  # result dictionary
    error = pyqtSignal(str)  # error message
    
    def __init__(self, excel_service: ExcelService, file_path: str, duplicate_handling: str):
        super().__init__()
        self.excel_service = excel_service
        self.file_path = file_path
        self.duplicate_handling = duplicate_handling
    
    def run(self):
        """Run import operation"""
        try:
            result = self.excel_service.import_excel_file(
                self.file_path,
                self.duplicate_handling,
                self.progress.emit
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ExcelImportDialog(QDialog):
    """
    Excel Import Dialog with preview and validation
    
    Features:
    - File selection dialog
    - Preview table with data validation
    - Duplicate handling options (skip, overwrite, create new)
    - Progress bar for import
    - Error reporting with line numbers
    """
    
    # Signal emitted when import is successful
    importCompleted = pyqtSignal(dict)  # result dictionary
    
    def __init__(self, excel_service: ExcelService, parent=None):
        """
        Initialize Excel Import Dialog
        
        Args:
            excel_service: Excel service instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.excel_service = excel_service
        self.file_path = None
        self.preview_data = None
        self.import_worker = None
        
        self._setup_ui()
        self._setup_connections()
        
        self.setWindowTitle("Import Excel File")
        self.resize(900, 700)
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setFixedWidth(100)
        file_layout.addWidget(self.browse_button)
        
        layout.addWidget(file_group)
        
        # Duplicate handling section
        duplicate_group = QGroupBox("Duplicate Handling")
        duplicate_layout = QVBoxLayout(duplicate_group)
        
        self.duplicate_button_group = QButtonGroup(self)
        
        self.skip_radio = QRadioButton("Skip duplicates (keep existing records)")
        self.skip_radio.setChecked(True)
        self.duplicate_button_group.addButton(self.skip_radio, 0)
        duplicate_layout.addWidget(self.skip_radio)
        
        self.overwrite_radio = QRadioButton("Overwrite duplicates (update existing records)")
        self.duplicate_button_group.addButton(self.overwrite_radio, 1)
        duplicate_layout.addWidget(self.overwrite_radio)
        
        self.create_new_radio = QRadioButton("Create new records (generate new trip codes)")
        self.duplicate_button_group.addButton(self.create_new_radio, 2)
        duplicate_layout.addWidget(self.create_new_radio)
        
        layout.addWidget(duplicate_group)
        
        # Preview section with splitter
        preview_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Preview table
        preview_group = QGroupBox("Preview (First 10 rows)")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        preview_layout.addWidget(self.preview_table)
        
        self.preview_info_label = QLabel("")
        preview_layout.addWidget(self.preview_info_label)
        
        preview_splitter.addWidget(preview_group)
        
        # Validation errors section
        errors_group = QGroupBox("Validation Errors")
        errors_layout = QVBoxLayout(errors_group)
        
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.errors_text.setMaximumHeight(150)
        errors_layout.addWidget(self.errors_text)
        
        preview_splitter.addWidget(errors_group)
        preview_splitter.setSizes([400, 150])
        
        layout.addWidget(preview_splitter, 1)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_button = QPushButton("Import")
        self.import_button.setEnabled(False)
        self.import_button.setFixedWidth(100)
        button_layout.addWidget(self.import_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.browse_button.clicked.connect(self._on_browse)
        self.import_button.clicked.connect(self._on_import)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_browse(self):
        """Handle browse button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path)
            self._load_preview()
    
    def _load_preview(self):
        """Load and display preview data"""
        if not self.file_path:
            return
        
        try:
            # Show loading message
            self.preview_info_label.setText("Loading preview...")
            self.errors_text.clear()
            
            # Load preview
            self.preview_data = self.excel_service.preview_excel_file(self.file_path, max_rows=10)
            
            # Display preview table
            self._display_preview_table()
            
            # Display validation errors
            self._display_validation_errors()
            
            # Update info label
            total_rows = self.preview_data['total_rows']
            error_count = len(self.preview_data['validation_errors'])
            self.preview_info_label.setText(
                f"Total rows: {total_rows} | "
                f"Preview rows: {len(self.preview_data['preview_data'])} | "
                f"Validation errors in preview: {error_count}"
            )
            
            # Enable import button if no critical errors
            self.import_button.setEnabled(True)
            
        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            QMessageBox.critical(self, "Preview Error", f"Failed to load preview:\n{str(e)}")
            self.import_button.setEnabled(False)
    
    def _display_preview_table(self):
        """Display preview data in table"""
        if not self.preview_data:
            return
        
        columns = self.preview_data['columns']
        preview_rows = self.preview_data['preview_data']
        
        # Setup table
        self.preview_table.setRowCount(len(preview_rows))
        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        
        # Populate table
        for row_idx, row_data in enumerate(preview_rows):
            for col_idx, col_name in enumerate(columns):
                value = row_data.get(col_name, "")
                item = QTableWidgetItem(str(value) if value is not None else "")
                
                # Highlight cells with validation errors
                if self._has_error_in_row(row_idx + 2):  # +2 for Excel row number
                    item.setBackground(QColor(255, 200, 200))
                
                self.preview_table.setItem(row_idx, col_idx, item)
        
        # Resize columns
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def _has_error_in_row(self, row_number: int) -> bool:
        """Check if row has validation errors"""
        if not self.preview_data:
            return False
        
        for error in self.preview_data['validation_errors']:
            if f"Row {row_number}:" in error:
                return True
        return False
    
    def _display_validation_errors(self):
        """Display validation errors"""
        if not self.preview_data:
            return
        
        errors = self.preview_data['validation_errors']
        
        if errors:
            error_text = "\n".join(errors)
            self.errors_text.setPlainText(error_text)
            self.errors_text.setStyleSheet("QTextEdit { color: red; }")
        else:
            self.errors_text.setPlainText("No validation errors found in preview.")
            self.errors_text.setStyleSheet("QTextEdit { color: green; }")
    
    def _on_import(self):
        """Handle import button click"""
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please select a file to import.")
            return
        
        # Get duplicate handling strategy
        duplicate_handling = self._get_duplicate_handling()
        
        # Confirm import
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import {self.preview_data['total_rows']} rows from Excel?\n\n"
            f"Duplicate handling: {duplicate_handling}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable buttons during import
        self.import_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.skip_radio.setEnabled(False)
        self.overwrite_radio.setEnabled(False)
        self.create_new_radio.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting import...")
        
        # Start import worker
        self.import_worker = ImportWorker(self.excel_service, self.file_path, duplicate_handling)
        self.import_worker.progress.connect(self._on_import_progress)
        self.import_worker.finished.connect(self._on_import_finished)
        self.import_worker.error.connect(self._on_import_error)
        self.import_worker.start()
    
    def _get_duplicate_handling(self) -> str:
        """Get selected duplicate handling strategy"""
        if self.skip_radio.isChecked():
            return DuplicateHandling.SKIP
        elif self.overwrite_radio.isChecked():
            return DuplicateHandling.OVERWRITE
        elif self.create_new_radio.isChecked():
            return DuplicateHandling.CREATE_NEW
        return DuplicateHandling.SKIP
    
    def _on_import_progress(self, current: int, total: int, message: str):
        """Handle import progress update"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(message)
    
    def _on_import_finished(self, result: Dict[str, Any]):
        """Handle import completion"""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Show result message
        success_count = result['success_count']
        skipped_count = result['skipped_count']
        error_count = result['error_count']
        errors = result['errors']
        
        message = (
            f"Import completed!\n\n"
            f"Successfully imported: {success_count}\n"
            f"Skipped: {skipped_count}\n"
            f"Errors: {error_count}"
        )
        
        if errors:
            message += f"\n\nErrors:\n" + "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                message += f"\n... and {len(errors) - 10} more errors"
        
        if error_count > 0:
            QMessageBox.warning(self, "Import Completed with Errors", message)
        else:
            QMessageBox.information(self, "Import Successful", message)
        
        # Emit signal
        self.importCompleted.emit(result)
        
        # Close dialog if successful
        if error_count == 0 or success_count > 0:
            self.accept()
        else:
            # Re-enable buttons for retry
            self.import_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.skip_radio.setEnabled(True)
            self.overwrite_radio.setEnabled(True)
            self.create_new_radio.setEnabled(True)
    
    def _on_import_error(self, error_message: str):
        """Handle import error"""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Show error message
        QMessageBox.critical(self, "Import Error", f"Import failed:\n{error_message}")
        
        # Re-enable buttons
        self.import_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.skip_radio.setEnabled(True)
        self.overwrite_radio.setEnabled(True)
        self.create_new_radio.setEnabled(True)
