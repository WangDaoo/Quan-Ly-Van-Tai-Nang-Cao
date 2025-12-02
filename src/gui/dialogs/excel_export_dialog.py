"""
Excel Export Dialog Module
Provides export options dialog with formatting preservation,
auto-fit columns, header styling, and progress bar
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox,
    QRadioButton, QButtonGroup, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from typing import Dict, Any, List, Optional
import logging

from src.services.excel_service import ExcelService
from src.models.trip import Trip


logger = logging.getLogger(__name__)


class ExportWorker(QThread):
    """Worker thread for Excel export operation"""
    
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(bool)  # success
    error = pyqtSignal(str)  # error message
    
    def __init__(self, excel_service: ExcelService, file_path: str, 
                 trips: List[Trip], include_formatting: bool):
        super().__init__()
        self.excel_service = excel_service
        self.file_path = file_path
        self.trips = trips
        self.include_formatting = include_formatting
    
    def run(self):
        """Run export operation"""
        try:
            success = self.excel_service.export_to_excel(
                self.file_path,
                self.trips,
                self.include_formatting,
                self.progress.emit
            )
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(str(e))


class ExcelExportDialog(QDialog):
    """
    Excel Export Dialog with options
    
    Features:
    - Export options: all records, filtered records, selected rows
    - Formatting preservation option
    - Auto-fit columns
    - Header styling
    - Progress bar for export
    """
    
    # Signal emitted when export is successful
    exportCompleted = pyqtSignal(str)  # file path
    
    def __init__(self, excel_service: ExcelService, 
                 all_trips: List[Trip],
                 filtered_trips: Optional[List[Trip]] = None,
                 selected_trips: Optional[List[Trip]] = None,
                 parent=None):
        """
        Initialize Excel Export Dialog
        
        Args:
            excel_service: Excel service instance
            all_trips: List of all trips
            filtered_trips: List of filtered trips (optional)
            selected_trips: List of selected trips (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.excel_service = excel_service
        self.all_trips = all_trips
        self.filtered_trips = filtered_trips or []
        self.selected_trips = selected_trips or []
        self.file_path = None
        self.export_worker = None
        
        self._setup_ui()
        self._setup_connections()
        
        self.setWindowTitle("Export to Excel")
        self.resize(500, 400)
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Export scope section
        scope_group = QGroupBox("Export Scope")
        scope_layout = QVBoxLayout(scope_group)
        
        self.scope_button_group = QButtonGroup(self)
        
        self.all_radio = QRadioButton(f"All records ({len(self.all_trips)} records)")
        self.all_radio.setChecked(True)
        self.scope_button_group.addButton(self.all_radio, 0)
        scope_layout.addWidget(self.all_radio)
        
        self.filtered_radio = QRadioButton(
            f"Filtered records ({len(self.filtered_trips)} records)"
        )
        self.filtered_radio.setEnabled(len(self.filtered_trips) > 0)
        self.scope_button_group.addButton(self.filtered_radio, 1)
        scope_layout.addWidget(self.filtered_radio)
        
        self.selected_radio = QRadioButton(
            f"Selected rows ({len(self.selected_trips)} records)"
        )
        self.selected_radio.setEnabled(len(self.selected_trips) > 0)
        self.scope_button_group.addButton(self.selected_radio, 2)
        scope_layout.addWidget(self.selected_radio)
        
        layout.addWidget(scope_group)
        
        # Formatting options section
        format_group = QGroupBox("Formatting Options")
        format_layout = QVBoxLayout(format_group)
        
        self.formatting_checkbox = QCheckBox("Include formatting (colors, borders, fonts)")
        self.formatting_checkbox.setChecked(True)
        format_layout.addWidget(self.formatting_checkbox)
        
        info_label = QLabel(
            "• Auto-fit columns\n"
            "• Header styling with colors\n"
            "• Alternating row colors\n"
            "• Number formatting with thousand separators\n"
            "• Freeze header row"
        )
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        format_layout.addWidget(info_label)
        
        layout.addWidget(format_group)
        
        # File selection section
        file_group = QGroupBox("Output File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setFixedWidth(100)
        file_layout.addWidget(self.browse_button)
        
        layout.addWidget(file_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_button = QPushButton("Export")
        self.export_button.setEnabled(False)
        self.export_button.setFixedWidth(100)
        button_layout.addWidget(self.export_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.browse_button.clicked.connect(self._on_browse)
        self.export_button.clicked.connect(self._on_export)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_browse(self):
        """Handle browse button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            # Ensure .xlsx extension
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            self.file_path = file_path
            self.file_label.setText(file_path)
            self.export_button.setEnabled(True)
    
    def _on_export(self):
        """Handle export button click"""
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please select a file to export.")
            return
        
        # Get trips to export
        trips = self._get_trips_to_export()
        
        if not trips:
            QMessageBox.warning(self, "No Data", "No records to export.")
            return
        
        # Get formatting option
        include_formatting = self.formatting_checkbox.isChecked()
        
        # Confirm export
        reply = QMessageBox.question(
            self,
            "Confirm Export",
            f"Export {len(trips)} records to Excel?\n\n"
            f"File: {self.file_path}\n"
            f"Formatting: {'Yes' if include_formatting else 'No'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable buttons during export
        self.export_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.all_radio.setEnabled(False)
        self.filtered_radio.setEnabled(False)
        self.selected_radio.setEnabled(False)
        self.formatting_checkbox.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting export...")
        
        # Start export worker
        self.export_worker = ExportWorker(
            self.excel_service,
            self.file_path,
            trips,
            include_formatting
        )
        self.export_worker.progress.connect(self._on_export_progress)
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.start()
    
    def _get_trips_to_export(self) -> List[Trip]:
        """Get trips to export based on selected scope"""
        if self.all_radio.isChecked():
            return self.all_trips
        elif self.filtered_radio.isChecked():
            return self.filtered_trips
        elif self.selected_radio.isChecked():
            return self.selected_trips
        return []
    
    def _on_export_progress(self, current: int, total: int, message: str):
        """Handle export progress update"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(message)
    
    def _on_export_finished(self, success: bool):
        """Handle export completion"""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data exported successfully to:\n{self.file_path}"
            )
            
            # Emit signal
            self.exportCompleted.emit(self.file_path)
            
            # Close dialog
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Export Failed",
                "Export operation failed. Please try again."
            )
            
            # Re-enable buttons
            self._enable_controls()
    
    def _on_export_error(self, error_message: str):
        """Handle export error"""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Show error message
        QMessageBox.critical(self, "Export Error", f"Export failed:\n{error_message}")
        
        # Re-enable buttons
        self._enable_controls()
    
    def _enable_controls(self):
        """Re-enable all controls"""
        self.export_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.all_radio.setEnabled(True)
        self.filtered_radio.setEnabled(len(self.filtered_trips) > 0)
        self.selected_radio.setEnabled(len(self.selected_trips) > 0)
        self.formatting_checkbox.setEnabled(True)
