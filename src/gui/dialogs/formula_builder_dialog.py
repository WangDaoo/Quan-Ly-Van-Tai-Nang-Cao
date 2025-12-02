"""
Formula Builder Dialog - Dialog for creating and editing formulas
Provides formula editor with syntax highlighting, field selector, testing, and validation
"""
import logging
import re
from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QMessageBox, QComboBox, QGroupBox,
    QFormLayout, QDialogButtonBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.formula import Formula
from src.models.field_configuration import FieldConfiguration

logger = logging.getLogger(__name__)


class FormulaSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for formula expressions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_formats()
    
    def setup_formats(self):
        """Setup text formats for different syntax elements"""
        # Operators
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#FF6B6B"))
        self.operator_format.setFontWeight(QFont.Weight.Bold)
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#4ECDC4"))
        
        # Field references
        self.field_format = QTextCharFormat()
        self.field_format.setForeground(QColor("#95E1D3"))
        self.field_format.setFontWeight(QFont.Weight.Bold)
        
        # Parentheses
        self.paren_format = QTextCharFormat()
        self.paren_format.setForeground(QColor("#F38181"))
        self.paren_format.setFontWeight(QFont.Weight.Bold)
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Highlight operators
        for match in re.finditer(r'[\+\-\*/]', text):
            self.setFormat(match.start(), match.end() - match.start(), self.operator_format)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Highlight field references [Field_Name]
        for match in re.finditer(r'\[[^\]]+\]', text):
            self.setFormat(match.start(), match.end() - match.start(), self.field_format)
        
        # Highlight parentheses
        for match in re.finditer(r'[()]', text):
            self.setFormat(match.start(), match.end() - match.start(), self.paren_format)


class FormulaBuilderDialog(QDialog):
    """
    Dialog for building and editing formulas with syntax highlighting and testing.
    
    Features:
    - Formula editor with syntax highlighting
    - Field selector dropdown
    - Formula testing with sample data
    - Formula validation and error display
    """
    
    formula_saved = pyqtSignal()
    
    def __init__(self, db_manager: EnhancedDatabaseManager, department_id: int, 
                 formula: Optional[Formula] = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.department_id = department_id
        self.formula = formula
        self.is_edit_mode = formula is not None
        self.available_fields: List[FieldConfiguration] = []
        
        self.setWindowTitle("Sửa Công Thức" if self.is_edit_mode else "Tạo Công Thức")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_available_fields()
        
        if self.is_edit_mode:
            self.load_formula_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for editor and test section
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section - Formula editor
        editor_widget = self._create_editor_section()
        splitter.addWidget(editor_widget)
        
        # Bottom section - Testing
        test_widget = self._create_test_section()
        splitter.addWidget(test_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_formula)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_editor_section(self):
        """Create the formula editor section"""
        widget = QGroupBox("Công Thức")
        layout = QVBoxLayout(widget)
        
        # Form fields
        form_layout = QFormLayout()
        
        # Target field
        self.target_field_edit = QLineEdit()
        form_layout.addRow("Trường Đích:", self.target_field_edit)
        
        # Description
        self.description_edit = QLineEdit()
        form_layout.addRow("Mô Tả:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Field selector toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Chèn Trường:"))
        
        self.field_selector = QComboBox()
        self.field_selector.currentIndexChanged.connect(self.insert_field)
        toolbar.addWidget(self.field_selector, 1)
        
        # Operator buttons
        operators = ['+', '-', '*', '/', '(', ')']
        for op in operators:
            btn = QPushButton(op)
            btn.setMaximumWidth(40)
            btn.clicked.connect(lambda checked, o=op: self.insert_operator(o))
            toolbar.addWidget(btn)
        
        layout.addLayout(toolbar)
        
        # Formula editor
        layout.addWidget(QLabel("Biểu Thức Công Thức:"))
        self.formula_editor = QTextEdit()
        self.formula_editor.setMaximumHeight(150)
        self.formula_editor.setPlaceholderText("Ví dụ: [Số lượng] * [Đơn giá] - [Giảm giá]")
        
        # Apply syntax highlighting
        self.highlighter = FormulaSyntaxHighlighter(self.formula_editor.document())
        
        layout.addWidget(self.formula_editor)
        
        # Validation button
        validate_btn = QPushButton("Kiểm Tra Cú Pháp")
        validate_btn.clicked.connect(self.validate_formula)
        layout.addWidget(validate_btn)
        
        # Error display
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        
        return widget
    
    def _create_test_section(self):
        """Create the formula testing section"""
        widget = QGroupBox("Kiểm Tra Công Thức")
        layout = QVBoxLayout(widget)
        
        # Instructions
        layout.addWidget(QLabel("Nhập giá trị mẫu để kiểm tra công thức:"))
        
        # Test data table
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(2)
        self.test_table.setHorizontalHeaderLabels(["Trường", "Giá Trị"])
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.test_table)
        
        # Test button and result
        test_layout = QHBoxLayout()
        test_btn = QPushButton("Tính Toán")
        test_btn.clicked.connect(self.test_formula)
        test_layout.addWidget(test_btn)
        
        test_layout.addWidget(QLabel("Kết Quả:"))
        self.result_label = QLabel("---")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        test_layout.addWidget(self.result_label)
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        return widget
    
    def load_available_fields(self):
        """Load available fields for the department"""
        try:
            query = """
                SELECT * FROM field_configurations 
                WHERE department_id = ? AND is_active = 1
                ORDER BY field_name
            """
            results = self.db_manager.execute_query(query, (self.department_id,))
            
            self.field_selector.clear()
            self.field_selector.addItem("-- Chọn trường --", None)
            
            for row in results:
                field_name = row['field_name']
                self.field_selector.addItem(field_name, field_name)
            
            # Update test table
            self.update_test_table()
        except Exception as e:
            logger.error(f"Error loading fields: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách trường: {str(e)}")
    
    def update_test_table(self):
        """Update test table with fields from formula"""
        formula_text = self.formula_editor.toPlainText()
        field_refs = re.findall(r'\[([^\]]+)\]', formula_text)
        
        self.test_table.setRowCount(len(field_refs))
        for i, field_name in enumerate(field_refs):
            self.test_table.setItem(i, 0, QTableWidgetItem(field_name))
            self.test_table.setItem(i, 1, QTableWidgetItem("0"))
    
    def insert_field(self):
        """Insert selected field into formula"""
        field_name = self.field_selector.currentData()
        if field_name:
            cursor = self.formula_editor.textCursor()
            cursor.insertText(f"[{field_name}]")
            self.field_selector.setCurrentIndex(0)
            self.update_test_table()
    
    def insert_operator(self, operator: str):
        """Insert operator into formula"""
        cursor = self.formula_editor.textCursor()
        cursor.insertText(f" {operator} ")
    
    def validate_formula(self):
        """Validate the formula syntax"""
        try:
            formula_text = self.formula_editor.toPlainText().strip()
            if not formula_text:
                self.error_label.setText("Công thức không được để trống")
                return False
            
            # Create a temporary formula object for validation
            temp_formula = Formula(
                department_id=self.department_id,
                target_field=self.target_field_edit.text() or "temp",
                formula_expression=formula_text
            )
            
            self.error_label.setText("✓ Cú pháp hợp lệ")
            self.error_label.setStyleSheet("color: green;")
            return True
        except ValueError as e:
            self.error_label.setText(f"✗ Lỗi: {str(e)}")
            self.error_label.setStyleSheet("color: red;")
            return False
        except Exception as e:
            logger.error(f"Error validating formula: {e}")
            self.error_label.setText(f"✗ Lỗi không xác định: {str(e)}")
            self.error_label.setStyleSheet("color: red;")
            return False
    
    def test_formula(self):
        """Test the formula with sample data"""
        try:
            if not self.validate_formula():
                return
            
            formula_text = self.formula_editor.toPlainText().strip()
            
            # Get test values from table
            field_values = {}
            for row in range(self.test_table.rowCount()):
                field_name = self.test_table.item(row, 0).text()
                value_text = self.test_table.item(row, 1).text()
                try:
                    field_values[field_name] = float(value_text)
                except ValueError:
                    QMessageBox.warning(
                        self, 
                        "Lỗi", 
                        f"Giá trị không hợp lệ cho trường '{field_name}': {value_text}"
                    )
                    return
            
            # Evaluate formula
            result = self.evaluate_formula(formula_text, field_values)
            self.result_label.setText(f"{result:,.2f}")
            self.result_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        except Exception as e:
            logger.error(f"Error testing formula: {e}")
            self.result_label.setText("Lỗi")
            self.result_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            QMessageBox.critical(self, "Lỗi", f"Không thể tính toán: {str(e)}")
    
    def evaluate_formula(self, formula: str, field_values: Dict[str, float]) -> float:
        """
        Evaluate formula with given field values.
        Simple implementation using string replacement and eval.
        """
        # Replace field references with values
        expression = formula
        for field_name, value in field_values.items():
            expression = expression.replace(f"[{field_name}]", str(value))
        
        # Check if all fields were replaced
        if '[' in expression or ']' in expression:
            raise ValueError("Không tìm thấy giá trị cho một số trường trong công thức")
        
        # Evaluate using Python's eval (safe in this controlled context)
        try:
            result = eval(expression)
            return float(result)
        except ZeroDivisionError:
            raise ValueError("Lỗi: Chia cho 0")
        except Exception as e:
            raise ValueError(f"Lỗi tính toán: {str(e)}")
    
    def load_formula_data(self):
        """Load existing formula data into form"""
        if not self.formula:
            return
        
        self.target_field_edit.setText(self.formula.target_field)
        self.description_edit.setText(self.formula.description or "")
        self.formula_editor.setPlainText(self.formula.formula_expression)
        self.update_test_table()
    
    def save_formula(self):
        """Save the formula"""
        try:
            target_field = self.target_field_edit.text().strip()
            if not target_field:
                QMessageBox.warning(self, "Lỗi", "Trường đích không được để trống")
                return
            
            formula_text = self.formula_editor.toPlainText().strip()
            if not formula_text:
                QMessageBox.warning(self, "Lỗi", "Công thức không được để trống")
                return
            
            # Validate formula
            if not self.validate_formula():
                QMessageBox.warning(self, "Lỗi", "Vui lòng sửa lỗi cú pháp trước khi lưu")
                return
            
            # Create or update formula
            if self.is_edit_mode:
                query = """
                    UPDATE formulas 
                    SET target_field = ?, formula_expression = ?, description = ?
                    WHERE id = ?
                """
                params = (
                    target_field,
                    formula_text,
                    self.description_edit.text().strip() or None,
                    self.formula.id
                )
                self.db_manager.execute_update(query, params)
                QMessageBox.information(self, "Thành Công", "Đã cập nhật công thức")
            else:
                query = """
                    INSERT INTO formulas (department_id, target_field, formula_expression, description, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """
                params = (
                    self.department_id,
                    target_field,
                    formula_text,
                    self.description_edit.text().strip() or None
                )
                self.db_manager.execute_insert(query, params)
                QMessageBox.information(self, "Thành Công", "Đã tạo công thức mới")
            
            self.formula_saved.emit()
            self.accept()
        except Exception as e:
            logger.error(f"Error saving formula: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu công thức: {str(e)}")


class FormulaManagerDialog(QDialog):
    """Dialog for managing all formulas in a department"""
    
    formulas_changed = pyqtSignal()
    
    def __init__(self, db_manager: EnhancedDatabaseManager, department_id: int, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.department_id = department_id
        
        self.setWindowTitle("Quản Lý Công Thức")
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.load_formulas()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("Thêm Công Thức")
        add_btn.clicked.connect(self.add_formula)
        toolbar.addWidget(add_btn)
        
        self.edit_btn = QPushButton("Sửa")
        self.edit_btn.clicked.connect(self.edit_formula)
        self.edit_btn.setEnabled(False)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_formula)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.formula_table = QTableWidget()
        self.formula_table.setColumnCount(4)
        self.formula_table.setHorizontalHeaderLabels([
            "Trường Đích", "Công Thức", "Mô Tả", "Trạng Thái"
        ])
        self.formula_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.formula_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.formula_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.formula_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.formula_table.cellDoubleClicked.connect(lambda: self.edit_formula())
        layout.addWidget(self.formula_table)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_formulas(self):
        """Load formulas from database"""
        try:
            query = """
                SELECT * FROM formulas 
                WHERE department_id = ?
                ORDER BY target_field
            """
            results = self.db_manager.execute_query(query, (self.department_id,))
            
            self.formula_table.setRowCount(0)
            for row_data in results:
                row = self.formula_table.rowCount()
                self.formula_table.insertRow(row)
                
                self.formula_table.setItem(row, 0, QTableWidgetItem(row_data['target_field']))
                self.formula_table.setItem(row, 1, QTableWidgetItem(row_data['formula_expression']))
                self.formula_table.setItem(row, 2, QTableWidgetItem(row_data['description'] or ""))
                self.formula_table.setItem(row, 3, QTableWidgetItem(
                    "Hoạt động" if row_data['is_active'] else "Không hoạt động"
                ))
                
                # Store formula ID
                self.formula_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading formulas: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải công thức: {str(e)}")
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.formula_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_formula(self):
        """Add a new formula"""
        dialog = FormulaBuilderDialog(self.db_manager, self.department_id, parent=self)
        dialog.formula_saved.connect(self.load_formulas)
        dialog.formula_saved.connect(self.formulas_changed.emit)
        dialog.exec()
    
    def edit_formula(self):
        """Edit selected formula"""
        selected_row = self.formula_table.currentRow()
        if selected_row < 0:
            return
        
        formula_id = self.formula_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM formulas WHERE id = ?"
            results = self.db_manager.execute_query(query, (formula_id,))
            if results:
                formula_data = results[0]
                formula = Formula(**formula_data)
                
                dialog = FormulaBuilderDialog(
                    self.db_manager, 
                    self.department_id, 
                    formula=formula,
                    parent=self
                )
                dialog.formula_saved.connect(self.load_formulas)
                dialog.formula_saved.connect(self.formulas_changed.emit)
                dialog.exec()
        except Exception as e:
            logger.error(f"Error editing formula: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa công thức: {str(e)}")
    
    def delete_formula(self):
        """Delete selected formula"""
        selected_row = self.formula_table.currentRow()
        if selected_row < 0:
            return
        
        formula_id = self.formula_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        target_field = self.formula_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Xác Nhận Xóa",
            f"Bạn có chắc muốn xóa công thức cho trường '{target_field}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "UPDATE formulas SET is_active = 0 WHERE id = ?"
                self.db_manager.execute_update(query, (formula_id,))
                self.load_formulas()
                self.formulas_changed.emit()
                QMessageBox.information(self, "Thành Công", "Đã xóa công thức")
            except Exception as e:
                logger.error(f"Error deleting formula: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa công thức: {str(e)}")
