"""
Validation Utilities

Provides comprehensive validation for user inputs, database constraints,
formula syntax, and file formats.

Requirements: 17.4
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

import config
from .error_handler import ValidationError


logger = logging.getLogger(__name__)


# ============================================================================
# Input Validation Functions
# ============================================================================

def validate_required(value: Any, field_name: str = "Field") -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is not empty.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} là bắt buộc"
    return True, None


def validate_number(value: Any, field_name: str = "Field") -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a valid number.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        float(value)
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} phải là số hợp lệ"


def validate_integer(value: Any, field_name: str = "Field") -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a valid integer.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        int(value)
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} phải là số nguyên hợp lệ"


def validate_positive_number(
    value: Any,
    field_name: str = "Field",
    allow_zero: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        allow_zero: Whether to allow zero
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, error = validate_number(value, field_name)
    if not is_valid:
        return is_valid, error
    
    num = float(value)
    if allow_zero:
        if num < 0:
            return False, f"{field_name} phải là số không âm"
    else:
        if num <= 0:
            return False, f"{field_name} phải là số dương"
    
    return True, None


def validate_range(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    field_name: str = "Field"
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a number is within a range.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, error = validate_number(value, field_name)
    if not is_valid:
        return is_valid, error
    
    num = float(value)
    
    if min_value is not None and num < min_value:
        return False, f"{field_name} phải lớn hơn hoặc bằng {min_value}"
    
    if max_value is not None and num > max_value:
        return False, f"{field_name} phải nhỏ hơn hoặc bằng {max_value}"
    
    return True, None


def validate_text_length(
    value: str,
    max_length: int,
    field_name: str = "Field"
) -> Tuple[bool, Optional[str]]:
    """
    Validate text length.
    
    Args:
        value: Text to validate
        max_length: Maximum allowed length
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} phải là văn bản"
    
    if len(value) > max_length:
        return False, f"{field_name} không được vượt quá {max_length} ký tự"
    
    return True, None


def validate_email(email: str, field_name: str = "Email") -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, f"{field_name} không được để trống"
    
    pattern = config.EMAIL_PATTERN
    if not re.match(pattern, email):
        return False, f"{field_name} không đúng định dạng"
    
    return True, None


def validate_phone(phone: str, field_name: str = "Phone") -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, f"{field_name} không được để trống"
    
    pattern = config.PHONE_PATTERN
    if not re.match(pattern, phone):
        return False, f"{field_name} không đúng định dạng"
    
    return True, None


def validate_url(url: str, field_name: str = "URL") -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, f"{field_name} không được để trống"
    
    pattern = config.URL_PATTERN
    if not re.match(pattern, url):
        return False, f"{field_name} không đúng định dạng"
    
    return True, None


def validate_date(
    date_value: Any,
    field_name: str = "Date"
) -> Tuple[bool, Optional[str]]:
    """
    Validate date value.
    
    Args:
        date_value: Date to validate (string or datetime)
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if isinstance(date_value, datetime):
        return True, None
    
    if isinstance(date_value, str):
        try:
            datetime.fromisoformat(date_value)
            return True, None
        except ValueError:
            return False, f"{field_name} không đúng định dạng ngày tháng"
    
    return False, f"{field_name} phải là ngày tháng hợp lệ"


def validate_pattern(
    value: str,
    pattern: str,
    field_name: str = "Field"
) -> Tuple[bool, Optional[str]]:
    """
    Validate value against a regex pattern.
    
    Args:
        value: Value to validate
        pattern: Regex pattern
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} phải là văn bản"
    
    if not re.match(pattern, value):
        return False, f"{field_name} không đúng định dạng yêu cầu"
    
    return True, None


def validate_no_special_chars(
    value: str,
    field_name: str = "Field"
) -> Tuple[bool, Optional[str]]:
    """
    Validate that text contains no special characters.
    
    Args:
        value: Text to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} phải là văn bản"
    
    # Allow letters, numbers, spaces, and Vietnamese characters
    pattern = r'^[a-zA-Z0-9\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]*$'
    
    if not re.match(pattern, value):
        return False, f"{field_name} không được chứa ký tự đặc biệt"
    
    return True, None


# ============================================================================
# Database Constraint Validation
# ============================================================================

def validate_trip_data(trip_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate trip data against database constraints.
    
    Args:
        trip_data: Trip data dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    is_valid, error = validate_required(trip_data.get('khach_hang'), 'Khách hàng')
    if not is_valid:
        errors.append(error)
    
    is_valid, error = validate_required(trip_data.get('gia_ca'), 'Giá cả')
    if not is_valid:
        errors.append(error)
    
    # Validate numbers
    if 'gia_ca' in trip_data:
        is_valid, error = validate_positive_number(trip_data['gia_ca'], 'Giá cả', allow_zero=False)
        if not is_valid:
            errors.append(error)
    
    if 'khoan_luong' in trip_data:
        is_valid, error = validate_positive_number(trip_data['khoan_luong'], 'Khoán lương', allow_zero=True)
        if not is_valid:
            errors.append(error)
    
    if 'chi_phi_khac' in trip_data:
        is_valid, error = validate_positive_number(trip_data['chi_phi_khac'], 'Chi phí khác', allow_zero=True)
        if not is_valid:
            errors.append(error)
    
    # Validate text lengths
    if 'khach_hang' in trip_data:
        is_valid, error = validate_text_length(trip_data['khach_hang'], 255, 'Khách hàng')
        if not is_valid:
            errors.append(error)
    
    if 'diem_di' in trip_data:
        is_valid, error = validate_text_length(trip_data['diem_di'], 255, 'Điểm đi')
        if not is_valid:
            errors.append(error)
    
    if 'diem_den' in trip_data:
        is_valid, error = validate_text_length(trip_data['diem_den'], 255, 'Điểm đến')
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors


def validate_field_configuration(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate field configuration data.
    
    Args:
        config_data: Field configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    is_valid, error = validate_required(config_data.get('field_name'), 'Tên trường')
    if not is_valid:
        errors.append(error)
    
    is_valid, error = validate_required(config_data.get('field_type'), 'Loại trường')
    if not is_valid:
        errors.append(error)
    
    # Validate field type
    if 'field_type' in config_data:
        if config_data['field_type'] not in config.FIELD_TYPES:
            errors.append(f"Loại trường không hợp lệ: {config_data['field_type']}")
    
    # Validate display order
    if 'display_order' in config_data:
        is_valid, error = validate_integer(config_data['display_order'], 'Thứ tự hiển thị')
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors


# ============================================================================
# Formula Syntax Validation
# ============================================================================

def validate_formula_syntax(formula: str) -> Tuple[bool, Optional[str]]:
    """
    Validate formula syntax.
    
    Args:
        formula: Formula expression
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not formula or not formula.strip():
        return False, "Công thức không được để trống"
    
    # Check for balanced brackets
    if formula.count('[') != formula.count(']'):
        return False, "Dấu ngoặc vuông không cân bằng"
    
    if formula.count('(') != formula.count(')'):
        return False, "Dấu ngoặc đơn không cân bằng"
    
    # Check for valid operators
    valid_operators = set(config.SUPPORTED_OPERATORS)
    
    # Remove field references and numbers to check operators
    temp = re.sub(r'\[[^\]]+\]', '', formula)
    temp = re.sub(r'\d+\.?\d*', '', temp)
    temp = re.sub(r'[()]', '', temp)
    temp = temp.strip()
    
    for char in temp:
        if char not in valid_operators and not char.isspace():
            return False, f"Toán tử không hợp lệ: {char}"
    
    # Check for consecutive operators
    for i in range(len(formula) - 1):
        if formula[i] in valid_operators and formula[i+1] in valid_operators:
            return False, "Không được có hai toán tử liên tiếp"
    
    return True, None


def validate_formula_fields(
    formula: str,
    available_fields: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate that all fields in formula exist.
    
    Args:
        formula: Formula expression
        available_fields: List of available field names
        
    Returns:
        Tuple of (is_valid, list_of_invalid_fields)
    """
    # Extract field references
    field_pattern = r'\[([^\]]+)\]'
    field_refs = re.findall(field_pattern, formula)
    
    invalid_fields = []
    for field in field_refs:
        if field not in available_fields:
            invalid_fields.append(field)
    
    return len(invalid_fields) == 0, invalid_fields


# ============================================================================
# File Format Validation
# ============================================================================

def validate_excel_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Excel file format.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        return False, "File không tồn tại"
    
    # Check file extension
    if path.suffix.lower() not in ['.xlsx', '.xls']:
        return False, "File phải có định dạng .xlsx hoặc .xls"
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024
    if path.stat().st_size > max_size:
        return False, "File quá lớn (tối đa 50MB)"
    
    # Try to open file
    try:
        import openpyxl
        openpyxl.load_workbook(file_path, read_only=True)
        return True, None
    except Exception as e:
        return False, f"Không thể đọc file Excel: {str(e)}"


def validate_json_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON file format.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        return False, "File không tồn tại"
    
    # Check file extension
    if path.suffix.lower() != '.json':
        return False, "File phải có định dạng .json"
    
    # Try to parse JSON
    try:
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"File JSON không hợp lệ: {str(e)}"
    except Exception as e:
        return False, f"Không thể đọc file JSON: {str(e)}"


# ============================================================================
# Validator Class
# ============================================================================

class Validator:
    """
    Comprehensive validator for all data types.
    """
    
    @staticmethod
    def validate(
        value: Any,
        rules: List[Dict[str, Any]],
        field_name: str = "Field"
    ) -> Tuple[bool, List[str]]:
        """
        Validate value against multiple rules.
        
        Args:
            value: Value to validate
            rules: List of validation rules
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for rule in rules:
            rule_type = rule.get('type')
            
            if rule_type == 'required':
                is_valid, error = validate_required(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'number':
                is_valid, error = validate_number(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'positive':
                is_valid, error = validate_positive_number(
                    value, field_name, rule.get('allow_zero', True)
                )
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'range':
                is_valid, error = validate_range(
                    value,
                    rule.get('min'),
                    rule.get('max'),
                    field_name
                )
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'email':
                is_valid, error = validate_email(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'phone':
                is_valid, error = validate_phone(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'url':
                is_valid, error = validate_url(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'pattern':
                is_valid, error = validate_pattern(
                    value, rule.get('pattern', ''), field_name
                )
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'no_special_chars':
                is_valid, error = validate_no_special_chars(value, field_name)
                if not is_valid:
                    errors.append(error)
            
            elif rule_type == 'max_length':
                is_valid, error = validate_text_length(
                    value, rule.get('max_length', 255), field_name
                )
                if not is_valid:
                    errors.append(error)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_dict(
        data: Dict[str, Any],
        schema: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate dictionary against schema.
        
        Args:
            data: Data dictionary to validate
            schema: Validation schema (field_name -> rules)
            
        Returns:
            Tuple of (is_valid, dict_of_field_errors)
        """
        all_errors = {}
        
        for field_name, rules in schema.items():
            value = data.get(field_name)
            is_valid, errors = Validator.validate(value, rules, field_name)
            
            if not is_valid:
                all_errors[field_name] = errors
        
        return len(all_errors) == 0, all_errors
