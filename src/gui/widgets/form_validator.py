"""
Form Validator Module
Implements 6 types of validators with real-time validation and visual feedback
"""

import re
from typing import Any, Optional, List, Dict, Callable
from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Base class for all validators"""
    
    def __init__(self, error_message: str = ""):
        self.error_message = error_message
    
    @abstractmethod
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validate the value
        Returns: (is_valid, error_message)
        """
        pass


class RequiredValidator(BaseValidator):
    """Validates that a field is not empty"""
    
    def __init__(self, error_message: str = "This field is required"):
        super().__init__(error_message)
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None:
            return False, self.error_message
        
        if isinstance(value, str):
            if not value.strip():
                return False, self.error_message
        elif isinstance(value, (list, dict)):
            if not value:
                return False, self.error_message
        
        return True, ""


class NumberOnlyValidator(BaseValidator):
    """Validates that a field contains only numbers"""
    
    def __init__(self, allow_decimals: bool = False, 
                 error_message: str = "Only numbers are allowed"):
        super().__init__(error_message)
        self.allow_decimals = allow_decimals
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None or value == "":
            return True, ""  # Empty is valid, use RequiredValidator for required fields
        
        str_value = str(value).strip()
        if not str_value:
            return True, ""
        
        if self.allow_decimals:
            # Allow decimals with . or ,
            pattern = r'^-?\d+([.,]\d+)?$'
        else:
            # Only integers
            pattern = r'^-?\d+$'
        
        if re.match(pattern, str_value):
            return True, ""
        else:
            return False, self.error_message


class TextOnlyValidator(BaseValidator):
    """Validates that a field contains only text (letters and spaces)"""
    
    def __init__(self, allow_spaces: bool = True, allow_unicode: bool = True,
                 error_message: str = "Only text characters are allowed"):
        super().__init__(error_message)
        self.allow_spaces = allow_spaces
        self.allow_unicode = allow_unicode
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None or value == "":
            return True, ""
        
        str_value = str(value)
        
        if self.allow_unicode:
            # Allow Unicode letters
            if self.allow_spaces:
                pattern = r'^[\p{L}\s]+$'
                # Python re doesn't support \p{L}, use alternative
                if all(c.isalpha() or c.isspace() for c in str_value):
                    return True, ""
            else:
                if all(c.isalpha() for c in str_value):
                    return True, ""
        else:
            # Only ASCII letters
            if self.allow_spaces:
                pattern = r'^[a-zA-Z\s]+$'
            else:
                pattern = r'^[a-zA-Z]+$'
            
            if re.match(pattern, str_value):
                return True, ""
        
        return False, self.error_message


class NoSpecialCharsValidator(BaseValidator):
    """Validates that a field contains no special characters"""
    
    def __init__(self, allowed_chars: str = "", 
                 error_message: str = "Special characters are not allowed"):
        super().__init__(error_message)
        self.allowed_chars = allowed_chars
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None or value == "":
            return True, ""
        
        str_value = str(value)
        
        # Define special characters (everything except alphanumeric, space, and allowed chars)
        for char in str_value:
            if not (char.isalnum() or char.isspace() or char in self.allowed_chars):
                return False, self.error_message
        
        return True, ""


class EmailFormatValidator(BaseValidator):
    """Validates email format according to RFC 5322"""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, error_message: str = "Invalid email format"):
        super().__init__(error_message)
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None or value == "":
            return True, ""
        
        str_value = str(value).strip()
        if not str_value:
            return True, ""
        
        if self.EMAIL_PATTERN.match(str_value):
            return True, ""
        else:
            return False, self.error_message


class PatternMatchingValidator(BaseValidator):
    """Validates that a field matches a specific regex pattern"""
    
    def __init__(self, pattern: str, error_message: str = "Invalid format"):
        super().__init__(error_message)
        try:
            self.pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    def validate(self, value: Any) -> tuple[bool, str]:
        if value is None or value == "":
            return True, ""
        
        str_value = str(value)
        
        if self.pattern.match(str_value):
            return True, ""
        else:
            return False, self.error_message


class FormValidator:
    """
    Main form validator class that manages multiple validators for form fields
    Supports real-time validation and cross-field validation
    """
    
    def __init__(self):
        self._field_validators: Dict[str, List[BaseValidator]] = {}
        self._cross_field_validators: List[Callable] = []
        self._validation_results: Dict[str, tuple[bool, str]] = {}
    
    def add_validator(self, field_name: str, validator: BaseValidator):
        """Add a validator to a specific field"""
        if field_name not in self._field_validators:
            self._field_validators[field_name] = []
        self._field_validators[field_name].append(validator)
    
    def add_cross_field_validator(self, validator_func: Callable):
        """
        Add a cross-field validator function
        Function should accept form_data dict and return (is_valid, error_message, field_name)
        """
        self._cross_field_validators.append(validator_func)
    
    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """
        Validate a single field value
        Returns: (is_valid, error_message)
        """
        if field_name not in self._field_validators:
            return True, ""
        
        for validator in self._field_validators[field_name]:
            is_valid, error_message = validator.validate(value)
            if not is_valid:
                self._validation_results[field_name] = (False, error_message)
                return False, error_message
        
        self._validation_results[field_name] = (True, "")
        return True, ""
    
    def validate_form(self, form_data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate all fields in the form
        Returns: (is_valid, error_dict)
        """
        errors = {}
        all_valid = True
        
        # Validate each field
        for field_name, value in form_data.items():
            is_valid, error_message = self.validate_field(field_name, value)
            if not is_valid:
                errors[field_name] = error_message
                all_valid = False
        
        # Run cross-field validators
        for cross_validator in self._cross_field_validators:
            is_valid, error_message, field_name = cross_validator(form_data)
            if not is_valid:
                errors[field_name] = error_message
                all_valid = False
        
        return all_valid, errors
    
    def get_field_validation_result(self, field_name: str) -> tuple[bool, str]:
        """Get the last validation result for a field"""
        return self._validation_results.get(field_name, (True, ""))
    
    def clear_validation_results(self):
        """Clear all validation results"""
        self._validation_results.clear()
    
    def is_form_valid(self) -> bool:
        """Check if all validated fields are currently valid"""
        return all(is_valid for is_valid, _ in self._validation_results.values())


class ValidationRuleBuilder:
    """Helper class to build validation rules from configuration"""
    
    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> List[BaseValidator]:
        """
        Build validators from configuration dictionary
        
        Config format:
        {
            "required": True,
            "type": "number" | "text" | "email" | "pattern",
            "no_special_chars": True,
            "pattern": "regex_pattern",
            "allow_decimals": True,
            "allow_spaces": True,
            "allowed_chars": "-_",
            "error_messages": {
                "required": "Custom message",
                ...
            }
        }
        """
        validators = []
        error_messages = config.get("error_messages", {})
        
        # Required validator
        if config.get("required", False):
            msg = error_messages.get("required", "This field is required")
            validators.append(RequiredValidator(msg))
        
        # Type-based validators
        field_type = config.get("type", "").lower()
        
        if field_type == "number":
            allow_decimals = config.get("allow_decimals", False)
            msg = error_messages.get("number", "Only numbers are allowed")
            validators.append(NumberOnlyValidator(allow_decimals, msg))
        
        elif field_type == "text":
            allow_spaces = config.get("allow_spaces", True)
            allow_unicode = config.get("allow_unicode", True)
            msg = error_messages.get("text", "Only text characters are allowed")
            validators.append(TextOnlyValidator(allow_spaces, allow_unicode, msg))
        
        elif field_type == "email":
            msg = error_messages.get("email", "Invalid email format")
            validators.append(EmailFormatValidator(msg))
        
        # No special characters validator
        if config.get("no_special_chars", False):
            allowed_chars = config.get("allowed_chars", "")
            msg = error_messages.get("no_special_chars", "Special characters are not allowed")
            validators.append(NoSpecialCharsValidator(allowed_chars, msg))
        
        # Pattern matching validator
        if "pattern" in config:
            pattern = config["pattern"]
            msg = error_messages.get("pattern", "Invalid format")
            validators.append(PatternMatchingValidator(pattern, msg))
        
        return validators
