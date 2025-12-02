"""
Number Utilities Module

Provides comprehensive number handling utilities including:
- Currency formatting
- Thousand separator formatting
- Number parsing and validation
- Rounding utilities

Requirements: 18.2
"""

from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import re


class NumberUtils:
    """Utility class for number operations"""
    
    # Currency settings
    CURRENCY_SYMBOL = "₫"
    CURRENCY_SYMBOL_VND = "VND"
    THOUSAND_SEPARATOR = ","
    DECIMAL_SEPARATOR = "."
    
    @staticmethod
    def format_currency(value: Union[int, float, Decimal], 
                       include_symbol: bool = True,
                       symbol: str = CURRENCY_SYMBOL) -> str:
        """
        Format number as currency with thousand separators
        
        Args:
            value: Number to format
            include_symbol: Whether to include currency symbol
            symbol: Currency symbol to use
            
        Returns:
            Formatted currency string
            
        Examples:
            >>> NumberUtils.format_currency(1000000)
            '1,000,000 ₫'
            >>> NumberUtils.format_currency(1500000.50, symbol="VND")
            '1,500,000.50 VND'
        """
        if value is None:
            return "0"
        
        # Convert to float for formatting
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return "0"
        
        # Format with thousand separators
        if num_value == int(num_value):
            # Integer value
            formatted = f"{int(num_value):,}".replace(",", NumberUtils.THOUSAND_SEPARATOR)
        else:
            # Decimal value
            formatted = f"{num_value:,.2f}".replace(",", NumberUtils.THOUSAND_SEPARATOR)
        
        if include_symbol:
            return f"{formatted} {symbol}"
        return formatted
    
    @staticmethod
    def format_number(value: Union[int, float, Decimal], 
                     decimal_places: int = 0,
                     use_separator: bool = True) -> str:
        """
        Format number with thousand separators
        
        Args:
            value: Number to format
            decimal_places: Number of decimal places
            use_separator: Whether to use thousand separator
            
        Returns:
            Formatted number string
            
        Examples:
            >>> NumberUtils.format_number(1000000)
            '1,000,000'
            >>> NumberUtils.format_number(1234.5678, decimal_places=2)
            '1,234.57'
        """
        if value is None:
            return "0"
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return "0"
        
        if decimal_places == 0:
            formatted = f"{int(num_value)}"
        else:
            formatted = f"{num_value:.{decimal_places}f}"
        
        if use_separator:
            # Split into integer and decimal parts
            parts = formatted.split(".")
            integer_part = parts[0]
            
            # Add thousand separators to integer part
            integer_part = f"{int(integer_part):,}".replace(",", NumberUtils.THOUSAND_SEPARATOR)
            
            if len(parts) > 1:
                formatted = f"{integer_part}{NumberUtils.DECIMAL_SEPARATOR}{parts[1]}"
            else:
                formatted = integer_part
        
        return formatted
    
    @staticmethod
    def parse_number(value: str) -> Optional[float]:
        """
        Parse number string to float, handling thousand separators
        
        Args:
            value: String to parse
            
        Returns:
            Parsed number or None if invalid
            
        Examples:
            >>> NumberUtils.parse_number("1,000,000")
            1000000.0
            >>> NumberUtils.parse_number("1.234,56")
            1234.56
        """
        if not value or not isinstance(value, str):
            return None
        
        # Remove whitespace and currency symbols
        cleaned = value.strip()
        cleaned = cleaned.replace(NumberUtils.CURRENCY_SYMBOL, "")
        cleaned = cleaned.replace(NumberUtils.CURRENCY_SYMBOL_VND, "")
        cleaned = cleaned.strip()
        
        # Handle different formats
        # Format 1: 1,000,000.50 (US format)
        # Format 2: 1.000.000,50 (EU format)
        
        # Count separators to determine format
        comma_count = cleaned.count(",")
        dot_count = cleaned.count(".")
        
        if comma_count > 0 and dot_count > 0:
            # Mixed separators - determine which is decimal
            last_comma_pos = cleaned.rfind(",")
            last_dot_pos = cleaned.rfind(".")
            
            if last_comma_pos > last_dot_pos:
                # EU format: 1.000.000,50
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                # US format: 1,000,000.50
                cleaned = cleaned.replace(",", "")
        elif comma_count > 1:
            # Multiple commas - thousand separator
            cleaned = cleaned.replace(",", "")
        elif dot_count > 1:
            # Multiple dots - thousand separator (EU)
            cleaned = cleaned.replace(".", "")
        elif comma_count == 1:
            # Single comma - could be decimal or thousand
            parts = cleaned.split(",")
            if len(parts[1]) <= 2:
                # Likely decimal: 1000,50
                cleaned = cleaned.replace(",", ".")
            else:
                # Likely thousand: 1,000
                cleaned = cleaned.replace(",", "")
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def parse_int(value: str) -> Optional[int]:
        """
        Parse integer string, handling thousand separators
        
        Args:
            value: String to parse
            
        Returns:
            Parsed integer or None if invalid
        """
        parsed = NumberUtils.parse_number(value)
        if parsed is not None:
            return int(parsed)
        return None
    
    @staticmethod
    def validate_number(value: str, 
                       min_value: Optional[float] = None,
                       max_value: Optional[float] = None,
                       allow_negative: bool = True,
                       allow_decimal: bool = True) -> tuple[bool, str]:
        """
        Validate number string
        
        Args:
            value: String to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative numbers are allowed
            allow_decimal: Whether decimal numbers are allowed
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Giá trị không được để trống"
        
        parsed = NumberUtils.parse_number(value)
        
        if parsed is None:
            return False, "Giá trị không phải là số hợp lệ"
        
        if not allow_negative and parsed < 0:
            return False, "Giá trị không được âm"
        
        if not allow_decimal and parsed != int(parsed):
            return False, "Giá trị phải là số nguyên"
        
        if min_value is not None and parsed < min_value:
            return False, f"Giá trị phải lớn hơn hoặc bằng {NumberUtils.format_number(min_value)}"
        
        if max_value is not None and parsed > max_value:
            return False, f"Giá trị phải nhỏ hơn hoặc bằng {NumberUtils.format_number(max_value)}"
        
        return True, ""
    
    @staticmethod
    def is_number(value: str) -> bool:
        """
        Check if string is a valid number
        
        Args:
            value: String to check
            
        Returns:
            True if valid number, False otherwise
        """
        return NumberUtils.parse_number(value) is not None
    
    @staticmethod
    def round_number(value: Union[int, float, Decimal], 
                    decimal_places: int = 0,
                    rounding_mode: str = ROUND_HALF_UP) -> Union[int, float]:
        """
        Round number to specified decimal places
        
        Args:
            value: Number to round
            decimal_places: Number of decimal places
            rounding_mode: Rounding mode (ROUND_HALF_UP, ROUND_DOWN, etc.)
            
        Returns:
            Rounded number
            
        Examples:
            >>> NumberUtils.round_number(1234.5678, 2)
            1234.57
            >>> NumberUtils.round_number(1234.5, 0)
            1235
        """
        if value is None:
            return 0
        
        try:
            decimal_value = Decimal(str(value))
            if decimal_places == 0:
                return int(decimal_value.quantize(Decimal('1'), rounding=rounding_mode))
            else:
                quantizer = Decimal(10) ** -decimal_places
                return float(decimal_value.quantize(quantizer, rounding=rounding_mode))
        except (ValueError, InvalidOperation):
            return 0
    
    @staticmethod
    def round_to_nearest(value: Union[int, float], nearest: int = 1000) -> int:
        """
        Round number to nearest multiple
        
        Args:
            value: Number to round
            nearest: Multiple to round to
            
        Returns:
            Rounded number
            
        Examples:
            >>> NumberUtils.round_to_nearest(1234567, 1000)
            1235000
            >>> NumberUtils.round_to_nearest(1234567, 10000)
            1230000
        """
        if value is None:
            return 0
        
        try:
            return int(round(float(value) / nearest) * nearest)
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def calculate_percentage(value: Union[int, float], 
                           total: Union[int, float],
                           decimal_places: int = 2) -> float:
        """
        Calculate percentage
        
        Args:
            value: Part value
            total: Total value
            decimal_places: Number of decimal places
            
        Returns:
            Percentage value
            
        Examples:
            >>> NumberUtils.calculate_percentage(25, 100)
            25.0
            >>> NumberUtils.calculate_percentage(1, 3, 2)
            33.33
        """
        if total == 0:
            return 0.0
        
        try:
            percentage = (float(value) / float(total)) * 100
            return NumberUtils.round_number(percentage, decimal_places)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0
    
    @staticmethod
    def apply_percentage(value: Union[int, float], 
                        percentage: Union[int, float]) -> float:
        """
        Apply percentage to value
        
        Args:
            value: Base value
            percentage: Percentage to apply
            
        Returns:
            Result of applying percentage
            
        Examples:
            >>> NumberUtils.apply_percentage(1000, 10)
            100.0
            >>> NumberUtils.apply_percentage(1000, -20)
            -200.0
        """
        try:
            return float(value) * (float(percentage) / 100)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def clamp(value: Union[int, float], 
             min_value: Union[int, float], 
             max_value: Union[int, float]) -> Union[int, float]:
        """
        Clamp value between min and max
        
        Args:
            value: Value to clamp
            min_value: Minimum value
            max_value: Maximum value
            
        Returns:
            Clamped value
        """
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def safe_divide(numerator: Union[int, float], 
                   denominator: Union[int, float],
                   default: Union[int, float] = 0) -> float:
        """
        Safe division with default value for division by zero
        
        Args:
            numerator: Numerator
            denominator: Denominator
            default: Default value if division by zero
            
        Returns:
            Division result or default
        """
        try:
            if denominator == 0:
                return default
            return float(numerator) / float(denominator)
        except (ValueError, TypeError):
            return default
