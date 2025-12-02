"""
Field Widgets Module - 10 types of form field widgets
Implements various input widgets with validation and formatting
"""

from PyQt6.QtWidgets import (
    QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox,
    QCheckBox, QTextEdit, QWidget, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QValidator, QIntValidator, QDoubleValidator
import re
from typing import Optional, List, Any
from datetime import datetime


class BaseFieldWidget(QWidget):
    """Base class for all field widgets"""
    valueChanged = pyqtSignal(object)
    validationChanged = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_valid = True
        self._error_message = ""
    
    def get_value(self) -> Any:
        """Get the current value of the widget"""
        raise NotImplementedError
    
    def set_value(self, value: Any):
        """Set the value of the widget"""
        raise NotImplementedError
    
    def clear(self):
        """Clear the widget value"""
        raise NotImplementedError
    
    def is_valid(self) -> bool:
        """Check if the current value is valid"""
        return self._is_valid
    
    def get_error_message(self) -> str:
        """Get the validation error message"""
        return self._error_message
    
    def set_error_state(self, is_valid: bool, message: str = ""):
        """Set the validation state"""
        self._is_valid = is_valid
        self._error_message = message
        self.validationChanged.emit(is_valid)
        
        # Visual feedback
        if hasattr(self, '_input_widget'):
            if is_valid:
                self._input_widget.setStyleSheet("")
            else:
                self._input_widget.setStyleSheet("border: 2px solid red;")


class TextboxWidget(BaseFieldWidget):
    """Text input widget with validation"""
    
    def __init__(self, placeholder: str = "", max_length: int = 255, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QLineEdit()
        self._input_widget.setPlaceholderText(placeholder)
        if max_length > 0:
            self._input_widget.setMaxLength(max_length)
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        self.valueChanged.emit(text)
    
    def get_value(self) -> str:
        return self._input_widget.text()
    
    def set_value(self, value: Any):
        self._input_widget.setText(str(value) if value is not None else "")
    
    def clear(self):
        self._input_widget.clear()


class NumberWidget(BaseFieldWidget):
    """Number input widget with min/max and step"""
    
    def __init__(self, min_value: float = 0, max_value: float = 999999999, 
                 step: float = 1, decimals: int = 0, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if decimals > 0:
            self._input_widget = QDoubleSpinBox()
            self._input_widget.setDecimals(decimals)
        else:
            self._input_widget = QSpinBox()
        
        self._input_widget.setMinimum(min_value)
        self._input_widget.setMaximum(max_value)
        self._input_widget.setSingleStep(step)
        
        self._input_widget.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self._input_widget)
    
    def _on_value_changed(self, value):
        self.valueChanged.emit(value)
    
    def get_value(self) -> float:
        return self._input_widget.value()
    
    def set_value(self, value: Any):
        if value is not None:
            if isinstance(self._input_widget, QSpinBox):
                self._input_widget.setValue(int(value))
            else:
                self._input_widget.setValue(float(value))
    
    def clear(self):
        self._input_widget.setValue(self._input_widget.minimum())


class CurrencyWidget(BaseFieldWidget):
    """Currency input widget with auto-formatting"""
    
    def __init__(self, currency_symbol: str = "VND", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QLineEdit()
        self._input_widget.setPlaceholderText("0")
        self._currency_symbol = currency_symbol
        self._raw_value = 0
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        self._input_widget.editingFinished.connect(self._format_display)
        
        if currency_symbol:
            label = QLabel(currency_symbol)
            layout.addWidget(self._input_widget)
            layout.addWidget(label)
        else:
            layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        # Remove formatting to get raw number
        clean_text = text.replace(",", "").replace(".", "").strip()
        try:
            self._raw_value = int(clean_text) if clean_text else 0
            self.valueChanged.emit(self._raw_value)
        except ValueError:
            pass
    
    def _format_display(self):
        # Format with thousand separators
        formatted = f"{self._raw_value:,}"
        self._input_widget.blockSignals(True)
        self._input_widget.setText(formatted)
        self._input_widget.blockSignals(False)
    
    def get_value(self) -> int:
        return self._raw_value
    
    def set_value(self, value: Any):
        if value is not None:
            self._raw_value = int(value)
            self._format_display()
    
    def clear(self):
        self._raw_value = 0
        self._input_widget.clear()


class DateEditWidget(BaseFieldWidget):
    """Date input widget with calendar picker"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QDateEdit()
        self._input_widget.setCalendarPopup(True)
        self._input_widget.setDate(QDate.currentDate())
        self._input_widget.setDisplayFormat("dd/MM/yyyy")
        
        self._input_widget.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self._input_widget)
    
    def _on_date_changed(self, date: QDate):
        self.valueChanged.emit(date.toString("yyyy-MM-dd"))
    
    def get_value(self) -> str:
        return self._input_widget.date().toString("yyyy-MM-dd")
    
    def set_value(self, value: Any):
        if value:
            if isinstance(value, str):
                date = QDate.fromString(value, "yyyy-MM-dd")
                if date.isValid():
                    self._input_widget.setDate(date)
            elif isinstance(value, datetime):
                date = QDate(value.year, value.month, value.day)
                self._input_widget.setDate(date)
    
    def clear(self):
        self._input_widget.setDate(QDate.currentDate())


class ComboboxWidget(BaseFieldWidget):
    """Dropdown widget with autocomplete"""
    
    def __init__(self, options: List[str] = None, editable: bool = True, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QComboBox()
        self._input_widget.setEditable(editable)
        
        if options:
            self._input_widget.addItems(options)
        
        if editable:
            self._input_widget.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            # Enable autocomplete
            self._input_widget.setCompleter(None)  # Will be set by autocomplete system
        
        self._input_widget.currentTextChanged.connect(self._on_text_changed)
        layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        self.valueChanged.emit(text)
    
    def get_value(self) -> str:
        return self._input_widget.currentText()
    
    def set_value(self, value: Any):
        if value is not None:
            self._input_widget.setCurrentText(str(value))
    
    def set_options(self, options: List[str]):
        """Update the dropdown options"""
        current = self.get_value()
        self._input_widget.clear()
        self._input_widget.addItems(options)
        if current:
            self._input_widget.setCurrentText(current)
    
    def clear(self):
        self._input_widget.setCurrentIndex(-1)
        if self._input_widget.isEditable():
            self._input_widget.clearEditText()


class CheckboxWidget(BaseFieldWidget):
    """Checkbox widget"""
    
    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QCheckBox(label)
        self._input_widget.stateChanged.connect(self._on_state_changed)
        
        layout.addWidget(self._input_widget)
    
    def _on_state_changed(self, state: int):
        self.valueChanged.emit(state == Qt.CheckState.Checked.value)
    
    def get_value(self) -> bool:
        return self._input_widget.isChecked()
    
    def set_value(self, value: Any):
        if value is not None:
            self._input_widget.setChecked(bool(value))
    
    def clear(self):
        self._input_widget.setChecked(False)


class EmailWidget(BaseFieldWidget):
    """Email input widget with validation"""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, placeholder: str = "email@example.com", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QLineEdit()
        self._input_widget.setPlaceholderText(placeholder)
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        # Validate email format
        if text:
            is_valid = bool(self.EMAIL_PATTERN.match(text))
            self.set_error_state(is_valid, "Invalid email format" if not is_valid else "")
        else:
            self.set_error_state(True, "")
        
        self.valueChanged.emit(text)
    
    def get_value(self) -> str:
        return self._input_widget.text()
    
    def set_value(self, value: Any):
        self._input_widget.setText(str(value) if value is not None else "")
    
    def clear(self):
        self._input_widget.clear()


class PhoneWidget(BaseFieldWidget):
    """Phone input widget with formatting"""
    
    def __init__(self, placeholder: str = "0123456789", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QLineEdit()
        self._input_widget.setPlaceholderText(placeholder)
        self._input_widget.setMaxLength(15)
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        # Remove non-digit characters
        digits_only = re.sub(r'\D', '', text)
        
        # Validate phone number (basic validation)
        if text:
            is_valid = len(digits_only) >= 10
            self.set_error_state(is_valid, "Phone number must be at least 10 digits" if not is_valid else "")
        else:
            self.set_error_state(True, "")
        
        self.valueChanged.emit(text)
    
    def get_value(self) -> str:
        return self._input_widget.text()
    
    def set_value(self, value: Any):
        self._input_widget.setText(str(value) if value is not None else "")
    
    def clear(self):
        self._input_widget.clear()


class TextAreaWidget(BaseFieldWidget):
    """Multi-line text input widget with word count"""
    
    def __init__(self, placeholder: str = "", max_length: int = 1000, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QTextEdit()
        self._input_widget.setPlaceholderText(placeholder)
        self._max_length = max_length
        
        self._word_count_label = QLabel("0 words")
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        
        layout.addWidget(self._input_widget)
        layout.addWidget(self._word_count_label)
    
    def _on_text_changed(self):
        text = self._input_widget.toPlainText()
        
        # Check max length
        if self._max_length > 0 and len(text) > self._max_length:
            # Truncate text
            self._input_widget.blockSignals(True)
            cursor = self._input_widget.textCursor()
            cursor.deletePreviousChar()
            self._input_widget.blockSignals(False)
            return
        
        # Update word count
        words = len(text.split()) if text.strip() else 0
        self._word_count_label.setText(f"{words} words")
        
        self.valueChanged.emit(text)
    
    def get_value(self) -> str:
        return self._input_widget.toPlainText()
    
    def set_value(self, value: Any):
        self._input_widget.setPlainText(str(value) if value is not None else "")
    
    def clear(self):
        self._input_widget.clear()


class URLWidget(BaseFieldWidget):
    """URL input widget with validation"""
    
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def __init__(self, placeholder: str = "https://example.com", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._input_widget = QLineEdit()
        self._input_widget.setPlaceholderText(placeholder)
        
        self._input_widget.textChanged.connect(self._on_text_changed)
        self._input_widget.editingFinished.connect(self._auto_add_protocol)
        
        layout.addWidget(self._input_widget)
    
    def _on_text_changed(self, text: str):
        # Validate URL format
        if text:
            is_valid = bool(self.URL_PATTERN.match(text))
            self.set_error_state(is_valid, "Invalid URL format" if not is_valid else "")
        else:
            self.set_error_state(True, "")
        
        self.valueChanged.emit(text)
    
    def _auto_add_protocol(self):
        """Auto-add http:// if no protocol specified"""
        text = self._input_widget.text().strip()
        if text and not text.startswith(('http://', 'https://')):
            self._input_widget.setText(f"http://{text}")
    
    def get_value(self) -> str:
        return self._input_widget.text()
    
    def set_value(self, value: Any):
        self._input_widget.setText(str(value) if value is not None else "")
    
    def clear(self):
        self._input_widget.clear()
