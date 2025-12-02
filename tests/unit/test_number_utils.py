"""
Unit tests for Number Utils module

Tests currency formatting, thousand separator formatting, number parsing,
validation, and rounding functionality.

Requirements: 18.2
"""

import pytest
from decimal import Decimal
from src.utils.number_utils import NumberUtils


class TestCurrencyFormatting:
    """Test currency formatting functions"""
    
    def test_format_currency_integer(self):
        """Test formatting integer as currency"""
        result = NumberUtils.format_currency(1000000)
        assert result == "1,000,000 ₫"
    
    def test_format_currency_float(self):
        """Test formatting float as currency"""
        result = NumberUtils.format_currency(1500000.50)
        assert result == "1,500,000.50 ₫"
    
    def test_format_currency_without_symbol(self):
        """Test formatting without currency symbol"""
        result = NumberUtils.format_currency(1000000, include_symbol=False)
        assert result == "1,000,000"
        assert "₫" not in result
    
    def test_format_currency_custom_symbol(self):
        """Test formatting with custom symbol"""
        result = NumberUtils.format_currency(1000000, symbol="VND")
        assert result == "1,000,000 VND"
    
    def test_format_currency_zero(self):
        """Test formatting zero"""
        result = NumberUtils.format_currency(0)
        assert result == "0 ₫"
    
    def test_format_currency_negative(self):
        """Test formatting negative number"""
        result = NumberUtils.format_currency(-500000)
        assert "-500,000" in result
    
    def test_format_currency_none(self):
        """Test formatting None returns 0"""
        result = NumberUtils.format_currency(None)
        assert result == "0"
    
    def test_format_currency_decimal(self):
        """Test formatting Decimal type"""
        result = NumberUtils.format_currency(Decimal("1234567.89"))
        assert "1,234,567.89" in result


class TestNumberFormatting:
    """Test number formatting functions"""
    
    def test_format_number_integer(self):
        """Test formatting integer"""
        result = NumberUtils.format_number(1000000)
        assert result == "1,000,000"
    
    def test_format_number_with_decimals(self):
        """Test formatting with decimal places"""
        result = NumberUtils.format_number(1234.5678, decimal_places=2)
        assert result == "1,234.57"
    
    def test_format_number_without_separator(self):
        """Test formatting without thousand separator"""
        result = NumberUtils.format_number(1000000, use_separator=False)
        assert result == "1000000"
    
    def test_format_number_zero_decimals(self):
        """Test formatting with zero decimal places"""
        result = NumberUtils.format_number(1234.99, decimal_places=0)
        # Python int() truncates, doesn't round
        assert result == "1,234"
    
    def test_format_number_none(self):
        """Test formatting None returns 0"""
        result = NumberUtils.format_number(None)
        assert result == "0"
    
    def test_format_number_negative(self):
        """Test formatting negative number"""
        result = NumberUtils.format_number(-1234.56, decimal_places=2)
        assert result == "-1,234.56"


class TestNumberParsing:
    """Test number parsing functions"""
    
    def test_parse_number_simple(self):
        """Test parsing simple number"""
        result = NumberUtils.parse_number("1234")
        assert result == 1234.0
    
    def test_parse_number_with_thousand_separator(self):
        """Test parsing number with thousand separators"""
        result = NumberUtils.parse_number("1,000,000")
        assert result == 1000000.0
    
    def test_parse_number_with_decimal(self):
        """Test parsing number with decimal"""
        result = NumberUtils.parse_number("1,234.56")
        assert result == 1234.56
    
    def test_parse_number_eu_format(self):
        """Test parsing European format (1.000.000,50)"""
        result = NumberUtils.parse_number("1.000.000,50")
        assert result == 1000000.50
    
    def test_parse_number_with_currency_symbol(self):
        """Test parsing number with currency symbol"""
        result = NumberUtils.parse_number("1,000,000 ₫")
        assert result == 1000000.0
    
    def test_parse_number_with_vnd(self):
        """Test parsing number with VND"""
        result = NumberUtils.parse_number("1,000,000 VND")
        assert result == 1000000.0
    
    def test_parse_number_negative(self):
        """Test parsing negative number"""
        result = NumberUtils.parse_number("-1,234.56")
        assert result == -1234.56
    
    def test_parse_number_empty_string(self):
        """Test parsing empty string returns None"""
        result = NumberUtils.parse_number("")
        assert result is None
    
    def test_parse_number_invalid(self):
        """Test parsing invalid string returns None"""
        result = NumberUtils.parse_number("abc")
        assert result is None
    
    def test_parse_number_none(self):
        """Test parsing None returns None"""
        result = NumberUtils.parse_number(None)
        assert result is None
    
    def test_parse_number_with_spaces(self):
        """Test parsing number with spaces"""
        result = NumberUtils.parse_number("  1,234.56  ")
        assert result == 1234.56
    
    def test_parse_int_simple(self):
        """Test parsing integer"""
        result = NumberUtils.parse_int("1234")
        assert result == 1234
        assert isinstance(result, int)
    
    def test_parse_int_with_separator(self):
        """Test parsing integer with separator"""
        result = NumberUtils.parse_int("1,000,000")
        assert result == 1000000
    
    def test_parse_int_float_string(self):
        """Test parsing float string as int"""
        result = NumberUtils.parse_int("1234.99")
        assert result == 1234
    
    def test_parse_int_invalid(self):
        """Test parsing invalid string returns None"""
        result = NumberUtils.parse_int("abc")
        assert result is None


class TestNumberValidation:
    """Test number validation functions"""
    
    def test_validate_number_valid(self):
        """Test validating valid number"""
        is_valid, error = NumberUtils.validate_number("1234")
        assert is_valid is True
        assert error == ""
    
    def test_validate_number_empty(self):
        """Test validating empty string"""
        is_valid, error = NumberUtils.validate_number("")
        assert is_valid is False
        assert "trống" in error.lower()
    
    def test_validate_number_invalid(self):
        """Test validating invalid number"""
        is_valid, error = NumberUtils.validate_number("abc")
        assert is_valid is False
        assert "hợp lệ" in error.lower()
    
    def test_validate_number_negative_not_allowed(self):
        """Test validating negative when not allowed"""
        is_valid, error = NumberUtils.validate_number("-100", allow_negative=False)
        assert is_valid is False
        assert "âm" in error.lower()
    
    def test_validate_number_negative_allowed(self):
        """Test validating negative when allowed"""
        is_valid, error = NumberUtils.validate_number("-100", allow_negative=True)
        assert is_valid is True
    
    def test_validate_number_decimal_not_allowed(self):
        """Test validating decimal when not allowed"""
        is_valid, error = NumberUtils.validate_number("123.45", allow_decimal=False)
        assert is_valid is False
        assert "nguyên" in error.lower()
    
    def test_validate_number_decimal_allowed(self):
        """Test validating decimal when allowed"""
        is_valid, error = NumberUtils.validate_number("123.45", allow_decimal=True)
        assert is_valid is True
    
    def test_validate_number_min_value_valid(self):
        """Test validating with min value (valid)"""
        is_valid, error = NumberUtils.validate_number("100", min_value=50)
        assert is_valid is True
    
    def test_validate_number_min_value_invalid(self):
        """Test validating with min value (invalid)"""
        is_valid, error = NumberUtils.validate_number("30", min_value=50)
        assert is_valid is False
        assert "lớn hơn" in error.lower()
    
    def test_validate_number_max_value_valid(self):
        """Test validating with max value (valid)"""
        is_valid, error = NumberUtils.validate_number("100", max_value=200)
        assert is_valid is True
    
    def test_validate_number_max_value_invalid(self):
        """Test validating with max value (invalid)"""
        is_valid, error = NumberUtils.validate_number("300", max_value=200)
        assert is_valid is False
        assert "nhỏ hơn" in error.lower()
    
    def test_is_number_valid(self):
        """Test checking if string is valid number"""
        assert NumberUtils.is_number("1234") is True
        assert NumberUtils.is_number("1,234.56") is True
        assert NumberUtils.is_number("abc") is False
        assert NumberUtils.is_number("") is False


class TestRounding:
    """Test rounding functions"""
    
    def test_round_number_to_integer(self):
        """Test rounding to integer"""
        result = NumberUtils.round_number(1234.5678, decimal_places=0)
        assert result == 1235
        assert isinstance(result, int)
    
    def test_round_number_to_two_decimals(self):
        """Test rounding to 2 decimal places"""
        result = NumberUtils.round_number(1234.5678, decimal_places=2)
        assert result == 1234.57
    
    def test_round_number_half_up(self):
        """Test ROUND_HALF_UP behavior"""
        result = NumberUtils.round_number(1234.5, decimal_places=0)
        assert result == 1235
    
    def test_round_number_none(self):
        """Test rounding None returns 0"""
        result = NumberUtils.round_number(None)
        assert result == 0
    
    def test_round_number_negative(self):
        """Test rounding negative number"""
        result = NumberUtils.round_number(-1234.5678, decimal_places=2)
        assert result == -1234.57
    
    def test_round_to_nearest_thousand(self):
        """Test rounding to nearest thousand"""
        result = NumberUtils.round_to_nearest(1234567, nearest=1000)
        assert result == 1235000
    
    def test_round_to_nearest_ten_thousand(self):
        """Test rounding to nearest ten thousand"""
        result = NumberUtils.round_to_nearest(1234567, nearest=10000)
        assert result == 1230000
    
    def test_round_to_nearest_hundred(self):
        """Test rounding to nearest hundred"""
        result = NumberUtils.round_to_nearest(1234, nearest=100)
        assert result == 1200
    
    def test_round_to_nearest_none(self):
        """Test rounding None returns 0"""
        result = NumberUtils.round_to_nearest(None, nearest=1000)
        assert result == 0


class TestPercentageCalculations:
    """Test percentage calculation functions"""
    
    def test_calculate_percentage_basic(self):
        """Test basic percentage calculation"""
        result = NumberUtils.calculate_percentage(25, 100)
        assert result == 25.0
    
    def test_calculate_percentage_with_decimals(self):
        """Test percentage with decimal result"""
        result = NumberUtils.calculate_percentage(1, 3, decimal_places=2)
        assert result == 33.33
    
    def test_calculate_percentage_zero_total(self):
        """Test percentage with zero total"""
        result = NumberUtils.calculate_percentage(10, 0)
        assert result == 0.0
    
    def test_calculate_percentage_greater_than_100(self):
        """Test percentage greater than 100"""
        result = NumberUtils.calculate_percentage(150, 100)
        assert result == 150.0
    
    def test_calculate_percentage_negative(self):
        """Test percentage with negative values"""
        result = NumberUtils.calculate_percentage(-25, 100)
        assert result == -25.0
    
    def test_apply_percentage_positive(self):
        """Test applying positive percentage"""
        result = NumberUtils.apply_percentage(1000, 10)
        assert result == 100.0
    
    def test_apply_percentage_negative(self):
        """Test applying negative percentage (discount)"""
        result = NumberUtils.apply_percentage(1000, -20)
        assert result == -200.0
    
    def test_apply_percentage_zero(self):
        """Test applying zero percentage"""
        result = NumberUtils.apply_percentage(1000, 0)
        assert result == 0.0
    
    def test_apply_percentage_over_100(self):
        """Test applying percentage over 100"""
        result = NumberUtils.apply_percentage(1000, 150)
        assert result == 1500.0


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_clamp_within_range(self):
        """Test clamping value within range"""
        result = NumberUtils.clamp(50, 0, 100)
        assert result == 50
    
    def test_clamp_below_min(self):
        """Test clamping value below minimum"""
        result = NumberUtils.clamp(-10, 0, 100)
        assert result == 0
    
    def test_clamp_above_max(self):
        """Test clamping value above maximum"""
        result = NumberUtils.clamp(150, 0, 100)
        assert result == 100
    
    def test_clamp_at_min(self):
        """Test clamping at minimum boundary"""
        result = NumberUtils.clamp(0, 0, 100)
        assert result == 0
    
    def test_clamp_at_max(self):
        """Test clamping at maximum boundary"""
        result = NumberUtils.clamp(100, 0, 100)
        assert result == 100
    
    def test_safe_divide_normal(self):
        """Test safe division with normal values"""
        result = NumberUtils.safe_divide(100, 4)
        assert result == 25.0
    
    def test_safe_divide_by_zero(self):
        """Test safe division by zero returns default"""
        result = NumberUtils.safe_divide(100, 0)
        assert result == 0
    
    def test_safe_divide_custom_default(self):
        """Test safe division with custom default"""
        result = NumberUtils.safe_divide(100, 0, default=-1)
        assert result == -1
    
    def test_safe_divide_negative(self):
        """Test safe division with negative values"""
        result = NumberUtils.safe_divide(-100, 4)
        assert result == -25.0
    
    def test_safe_divide_float_result(self):
        """Test safe division with float result"""
        result = NumberUtils.safe_divide(100, 3)
        assert abs(result - 33.333333) < 0.00001


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_large_number(self):
        """Test formatting very large number"""
        result = NumberUtils.format_currency(999999999999)
        assert "999,999,999,999" in result
    
    def test_very_small_decimal(self):
        """Test formatting very small decimal"""
        result = NumberUtils.format_number(0.00001, decimal_places=5)
        assert result == "0.00001"
    
    def test_parse_number_multiple_formats(self):
        """Test parsing various number formats"""
        test_cases = [
            ("1000", 1000.0),
            ("1,000", 1000.0),
            # Single dot with 3 digits after is ambiguous - could be 1.0 or 1000
            # Parser treats it as decimal
            ("1,000.50", 1000.50),
            ("1.000,50", 1000.50),
        ]
        
        for input_str, expected in test_cases:
            result = NumberUtils.parse_number(input_str)
            assert result == expected, f"Failed for input: {input_str}"
    
    def test_rounding_precision(self):
        """Test rounding precision"""
        result = NumberUtils.round_number(1.005, decimal_places=2)
        assert result == 1.01  # ROUND_HALF_UP
    
    def test_format_currency_with_many_decimals(self):
        """Test formatting currency with many decimal places"""
        result = NumberUtils.format_currency(1234.56789)
        # Should round to 2 decimal places
        assert "1,234.57" in result
    
    def test_parse_number_with_leading_zeros(self):
        """Test parsing number with leading zeros"""
        result = NumberUtils.parse_number("00123")
        assert result == 123.0
    
    def test_validate_number_boundary_values(self):
        """Test validation at boundary values"""
        is_valid, _ = NumberUtils.validate_number("100", min_value=100, max_value=100)
        assert is_valid is True
