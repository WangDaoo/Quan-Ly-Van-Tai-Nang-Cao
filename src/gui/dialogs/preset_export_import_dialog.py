"""
Preset Export/Import Dialog Module
Provides export/import functionality for field configurations, formulas, and push conditions
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QGroupBox, QCheckBox, QTextEdit,
    QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, List, Optional
import json
import logging
from pathlib import Path
from datetime import datetime

from src.database.enhanced_db_manager import EnhancedDatabaseManager


logger = logging.getLogger(__name__)


class PresetExportImportDialog(QDialog):
    """
    Preset Export/Import Dialog
    
    Features:
    - Export field configurations to JSON
    - Export formulas to JSON
    - Export push conditions to JSON
    - Import with validation
    - Preset library management
    """
    
    # Signals
    presetImported = pyqtSignal(dict)  # Emitted when preset is imported
    
    def __init__(self, db_manager: EnhancedDatabaseManager, department_id: int, parent=None):
        """
        Initialize Preset Export/Import Dialog
        
        Args:
            db_manager: Database manager instance
            department_id: Current department ID
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.department_id = department_id
        
        self._setup_ui()
        self._setup_connections()
        
        self.setWindowTitle("Preset Export/Import")
        self.resize(800, 600)
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Create splitter for export and import sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Export section
        export_widget = self._create_export_section()
        splitter.addWidget(export_widget)
        
        # Import section
        import_widget = self._create_import_section()
        splitter.addWidget(import_widget)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.setFixedWidth(100)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _create_export_section(self) -> QGroupBox:
        """Create export section"""
        export_group = QGroupBox("Export Preset")
        export_layout = QVBoxLayout(export_group)
        
        # Export options
        options_label = QLabel("Select items to export:")
        export_layout.addWidget(options_label)
        
        self.export_fields_checkbox = QCheckBox("Field Configurations")
        self.export_fields_checkbox.setChecked(True)
        export_layout.addWidget(self.export_fields_checkbox)
        
        self.export_formulas_checkbox = QCheckBox("Formulas")
        self.export_formulas_checkbox.setChecked(True)
        export_layout.addWidget(self.export_formulas_checkbox)
        
        self.export_conditions_checkbox = QCheckBox("Push Conditions")
        self.export_conditions_checkbox.setChecked(True)
        export_layout.addWidget(self.export_conditions_checkbox)
        
        # Preview
        preview_label = QLabel("Export Preview:")
        export_layout.addWidget(preview_label)
        
        self.export_preview = QTextEdit()
        self.export_preview.setReadOnly(True)
        self.export_preview.setMaximumHeight(200)
        export_layout.addWidget(self.export_preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_export_button = QPushButton("Preview")
        self.preview_export_button.clicked.connect(self._on_preview_export)
        button_layout.addWidget(self.preview_export_button)
        
        self.export_button = QPushButton("Export to File...")
        self.export_button.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_button)
        
        export_layout.addLayout(button_layout)
        
        return export_group
    
    def _create_import_section(self) -> QGroupBox:
        """Create import section"""
        import_group = QGroupBox("Import Preset")
        import_layout = QVBoxLayout(import_group)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.import_file_label = QLabel("No file selected")
        file_layout.addWidget(self.import_file_label, 1)
        
        self.browse_import_button = QPushButton("Browse...")
        self.browse_import_button.clicked.connect(self._on_browse_import)
        file_layout.addWidget(self.browse_import_button)
        
        import_layout.addLayout(file_layout)
        
        # Preview
        preview_label = QLabel("Import Preview:")
        import_layout.addWidget(preview_label)
        
        self.import_preview = QTextEdit()
        self.import_preview.setReadOnly(True)
        self.import_preview.setMaximumHeight(200)
        import_layout.addWidget(self.import_preview)
        
        # Validation results
        validation_label = QLabel("Validation Results:")
        import_layout.addWidget(validation_label)
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(100)
        import_layout.addWidget(self.validation_text)
        
        # Import button
        self.import_button = QPushButton("Import")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self._on_import)
        import_layout.addWidget(self.import_button)
        
        return import_group
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.close_button.clicked.connect(self.accept)
    
    def _on_preview_export(self):
        """Handle preview export button click"""
        try:
            preset_data = self._collect_export_data()
            
            # Format as JSON for preview
            json_str = json.dumps(preset_data, indent=2, ensure_ascii=False)
            self.export_preview.setPlainText(json_str)
            
        except Exception as e:
            logger.error(f"Error previewing export: {e}")
            QMessageBox.critical(self, "Preview Error", f"Failed to preview:\n{str(e)}")
    
    def _collect_export_data(self) -> Dict[str, Any]:
        """Collect data for export"""
        preset_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'department_id': self.department_id,
            'data': {}
        }
        
        # Export field configurations
        if self.export_fields_checkbox.isChecked():
            field_configs = self._get_field_configurations()
            preset_data['data']['field_configurations'] = field_configs
        
        # Export formulas
        if self.export_formulas_checkbox.isChecked():
            formulas = self._get_formulas()
            preset_data['data']['formulas'] = formulas
        
        # Export push conditions
        if self.export_conditions_checkbox.isChecked():
            push_conditions = self._get_push_conditions()
            preset_data['data']['push_conditions'] = push_conditions
        
        return preset_data
    
    def _get_field_configurations(self) -> List[Dict[str, Any]]:
        """Get field configurations from database"""
        try:
            query = """
                SELECT field_name, field_type, widget_type, is_required,
                       validation_rules, default_value, options, display_order,
                       category, is_active
                FROM field_configurations
                WHERE department_id = ? AND is_active = 1
                ORDER BY display_order
            """
            rows = self.db_manager.fetch_all(query, (self.department_id,))
            
            field_configs = []
            for row in rows:
                config = {
                    'field_name': row[0],
                    'field_type': row[1],
                    'widget_type': row[2],
                    'is_required': bool(row[3]),
                    'validation_rules': row[4],
                    'default_value': row[5],
                    'options': row[6],
                    'display_order': row[7],
                    'category': row[8],
                    'is_active': bool(row[9])
                }
                field_configs.append(config)
            
            return field_configs
            
        except Exception as e:
            logger.error(f"Error getting field configurations: {e}")
            return []
    
    def _get_formulas(self) -> List[Dict[str, Any]]:
        """Get formulas from database"""
        try:
            query = """
                SELECT target_field, formula_expression, description, is_active
                FROM formulas
                WHERE department_id = ? AND is_active = 1
            """
            rows = self.db_manager.fetch_all(query, (self.department_id,))
            
            formulas = []
            for row in rows:
                formula = {
                    'target_field': row[0],
                    'formula_expression': row[1],
                    'description': row[2],
                    'is_active': bool(row[3])
                }
                formulas.append(formula)
            
            return formulas
            
        except Exception as e:
            logger.error(f"Error getting formulas: {e}")
            return []
    
    def _get_push_conditions(self) -> List[Dict[str, Any]]:
        """Get push conditions from database"""
        try:
            query = """
                SELECT source_department_id, target_department_id, field_name,
                       operator, value, logic_operator, condition_order, is_active
                FROM push_conditions
                WHERE source_department_id = ? AND is_active = 1
                ORDER BY condition_order
            """
            rows = self.db_manager.fetch_all(query, (self.department_id,))
            
            conditions = []
            for row in rows:
                condition = {
                    'source_department_id': row[0],
                    'target_department_id': row[1],
                    'field_name': row[2],
                    'operator': row[3],
                    'value': row[4],
                    'logic_operator': row[5],
                    'condition_order': row[6],
                    'is_active': bool(row[7])
                }
                conditions.append(condition)
            
            return conditions
            
        except Exception as e:
            logger.error(f"Error getting push conditions: {e}")
            return []
    
    def _on_export(self):
        """Handle export button click"""
        try:
            # Get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Preset",
                f"preset_{self.department_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            # Ensure .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            # Collect data
            preset_data = self._collect_export_data()
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Preset exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error exporting preset: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")
    
    def _on_browse_import(self):
        """Handle browse import button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Preset File",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            self.import_file_label.setText(file_path)
            self._load_import_preview(file_path)
    
    def _load_import_preview(self, file_path: str):
        """Load and validate import file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            # Validate preset data
            validation_errors = self._validate_preset_data(preset_data)
            
            # Display preview
            json_str = json.dumps(preset_data, indent=2, ensure_ascii=False)
            self.import_preview.setPlainText(json_str)
            
            # Display validation results
            if validation_errors:
                error_text = "\n".join(validation_errors)
                self.validation_text.setPlainText(f"Validation Errors:\n{error_text}")
                self.validation_text.setStyleSheet("QTextEdit { color: red; }")
                self.import_button.setEnabled(False)
            else:
                self.validation_text.setPlainText("Validation passed. Ready to import.")
                self.validation_text.setStyleSheet("QTextEdit { color: green; }")
                self.import_button.setEnabled(True)
                
                # Store preset data for import
                self._import_preset_data = preset_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {e}")
            QMessageBox.critical(self, "Invalid File", f"Invalid JSON file:\n{str(e)}")
            self.import_button.setEnabled(False)
        except Exception as e:
            logger.error(f"Error loading import file: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load file:\n{str(e)}")
            self.import_button.setEnabled(False)
    
    def _validate_preset_data(self, preset_data: Dict[str, Any]) -> List[str]:
        """Validate preset data"""
        errors = []
        
        # Check version
        if 'version' not in preset_data:
            errors.append("Missing 'version' field")
        
        # Check data section
        if 'data' not in preset_data:
            errors.append("Missing 'data' section")
            return errors
        
        data = preset_data['data']
        
        # Validate field configurations
        if 'field_configurations' in data:
            if not isinstance(data['field_configurations'], list):
                errors.append("'field_configurations' must be a list")
            else:
                for idx, config in enumerate(data['field_configurations']):
                    if 'field_name' not in config:
                        errors.append(f"Field config {idx}: missing 'field_name'")
                    if 'field_type' not in config:
                        errors.append(f"Field config {idx}: missing 'field_type'")
        
        # Validate formulas
        if 'formulas' in data:
            if not isinstance(data['formulas'], list):
                errors.append("'formulas' must be a list")
            else:
                for idx, formula in enumerate(data['formulas']):
                    if 'target_field' not in formula:
                        errors.append(f"Formula {idx}: missing 'target_field'")
                    if 'formula_expression' not in formula:
                        errors.append(f"Formula {idx}: missing 'formula_expression'")
        
        # Validate push conditions
        if 'push_conditions' in data:
            if not isinstance(data['push_conditions'], list):
                errors.append("'push_conditions' must be a list")
            else:
                for idx, condition in enumerate(data['push_conditions']):
                    if 'field_name' not in condition:
                        errors.append(f"Condition {idx}: missing 'field_name'")
                    if 'operator' not in condition:
                        errors.append(f"Condition {idx}: missing 'operator'")
        
        return errors
    
    def _on_import(self):
        """Handle import button click"""
        if not hasattr(self, '_import_preset_data'):
            QMessageBox.warning(self, "No Data", "No preset data loaded.")
            return
        
        # Confirm import
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            "Import this preset? This will add new configurations to the database.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            preset_data = self._import_preset_data
            data = preset_data['data']
            
            imported_counts = {
                'field_configurations': 0,
                'formulas': 0,
                'push_conditions': 0
            }
            
            # Import field configurations
            if 'field_configurations' in data:
                count = self._import_field_configurations(data['field_configurations'])
                imported_counts['field_configurations'] = count
            
            # Import formulas
            if 'formulas' in data:
                count = self._import_formulas(data['formulas'])
                imported_counts['formulas'] = count
            
            # Import push conditions
            if 'push_conditions' in data:
                count = self._import_push_conditions(data['push_conditions'])
                imported_counts['push_conditions'] = count
            
            # Show success message
            message = (
                f"Import completed!\n\n"
                f"Field Configurations: {imported_counts['field_configurations']}\n"
                f"Formulas: {imported_counts['formulas']}\n"
                f"Push Conditions: {imported_counts['push_conditions']}"
            )
            QMessageBox.information(self, "Import Successful", message)
            
            # Emit signal
            self.presetImported.emit(imported_counts)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            logger.error(f"Error importing preset: {e}")
            QMessageBox.critical(self, "Import Error", f"Failed to import:\n{str(e)}")
    
    def _import_field_configurations(self, configs: List[Dict[str, Any]]) -> int:
        """Import field configurations"""
        count = 0
        
        for config in configs:
            try:
                # Check if field already exists
                check_query = """
                    SELECT id FROM field_configurations
                    WHERE department_id = ? AND field_name = ?
                """
                existing = self.db_manager.fetch_one(
                    check_query,
                    (self.department_id, config['field_name'])
                )
                
                if existing:
                    # Update existing
                    update_query = """
                        UPDATE field_configurations
                        SET field_type = ?, widget_type = ?, is_required = ?,
                            validation_rules = ?, default_value = ?, options = ?,
                            display_order = ?, category = ?, is_active = ?
                        WHERE id = ?
                    """
                    self.db_manager.execute_update(
                        update_query,
                        (
                            config['field_type'],
                            config['widget_type'],
                            config['is_required'],
                            config.get('validation_rules'),
                            config.get('default_value'),
                            config.get('options'),
                            config['display_order'],
                            config.get('category'),
                            config['is_active'],
                            existing[0]
                        )
                    )
                else:
                    # Insert new
                    insert_query = """
                        INSERT INTO field_configurations
                        (department_id, field_name, field_type, widget_type, is_required,
                         validation_rules, default_value, options, display_order, category, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    self.db_manager.execute_update(
                        insert_query,
                        (
                            self.department_id,
                            config['field_name'],
                            config['field_type'],
                            config['widget_type'],
                            config['is_required'],
                            config.get('validation_rules'),
                            config.get('default_value'),
                            config.get('options'),
                            config['display_order'],
                            config.get('category'),
                            config['is_active']
                        )
                    )
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error importing field config {config.get('field_name')}: {e}")
        
        return count
    
    def _import_formulas(self, formulas: List[Dict[str, Any]]) -> int:
        """Import formulas"""
        count = 0
        
        for formula in formulas:
            try:
                # Check if formula already exists
                check_query = """
                    SELECT id FROM formulas
                    WHERE department_id = ? AND target_field = ?
                """
                existing = self.db_manager.fetch_one(
                    check_query,
                    (self.department_id, formula['target_field'])
                )
                
                if existing:
                    # Update existing
                    update_query = """
                        UPDATE formulas
                        SET formula_expression = ?, description = ?, is_active = ?
                        WHERE id = ?
                    """
                    self.db_manager.execute_update(
                        update_query,
                        (
                            formula['formula_expression'],
                            formula.get('description'),
                            formula['is_active'],
                            existing[0]
                        )
                    )
                else:
                    # Insert new
                    insert_query = """
                        INSERT INTO formulas
                        (department_id, target_field, formula_expression, description, is_active)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    self.db_manager.execute_update(
                        insert_query,
                        (
                            self.department_id,
                            formula['target_field'],
                            formula['formula_expression'],
                            formula.get('description'),
                            formula['is_active']
                        )
                    )
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error importing formula {formula.get('target_field')}: {e}")
        
        return count
    
    def _import_push_conditions(self, conditions: List[Dict[str, Any]]) -> int:
        """Import push conditions"""
        count = 0
        
        for condition in conditions:
            try:
                # Insert new condition (don't check for duplicates as conditions can be similar)
                insert_query = """
                    INSERT INTO push_conditions
                    (source_department_id, target_department_id, field_name, operator,
                     value, logic_operator, condition_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db_manager.execute_update(
                    insert_query,
                    (
                        condition['source_department_id'],
                        condition['target_department_id'],
                        condition['field_name'],
                        condition['operator'],
                        condition.get('value'),
                        condition.get('logic_operator', 'AND'),
                        condition['condition_order'],
                        condition['is_active']
                    )
                )
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error importing push condition: {e}")
        
        return count
