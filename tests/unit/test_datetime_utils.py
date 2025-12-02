"""
Unit tests for DateTime Utils module

Tests date/time formatting, parsing, calculations, timezone handling,
and date range validation functionality.

Requirements: 18.1
"""

import pytest
from datetime import datetime, timedelta, date
import pytz
from src.utils.datetime_utils import DateTimeUtils


class TestDateTimeFormatting:
    """Test date/time formatting functions"""
    
    def test_format_date_default(self):
        """Test default date formatting (DD/MM/YYYY)"""
        dt = datetime(2024, 12, 2, 14, 30, 0)
        result = DateTimeUtils.format_date(dt)
        assert result == "02/12/2024"
    
    def test_format_date_custom_format(self):
        """Test custom date formatting"""
        dt = datetime(2024, 12, 2, 14, 30, 0)
        result = DateTimeUtils.format_date(dt, DateTimeUtils.FORMAT_DATE)
        assert result == "2024-12-02"
    
    def test_format_date_with_time(self):
        """Test datetime formatting"""
        dt = datetime(2024, 12, 2, 14, 30, 45)
        result = DateTimeUtils.format_date(dt, DateTimeUtils.FORMAT_DISPLAY_DATETIME)
        assert result == "02/12/2024 14:30:45"
    
    def test_format_date_none(self):
        """Test formatting None returns empty string"""
        result = DateTimeUtils.format_date(None)
        assert result == ""
    
    def test_format_date_iso(self):
        """Test ISO format"""
        dt = datetime(2024, 12, 2, 14, 30, 0)
        result = DateTimeUtils.format_date(dt, DateTimeUtils.FORMAT_ISO)
        assert result == "2024-12-02T14:30:00"


class TestDateTimeParsing:
    """Test date/time parsing functions"""
    
    def test_parse_date_default_format(self):
        """Test parsing DD/MM/YYYY format"""
        result = DateTimeUtils.parse_date("02/12/2024")
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 2
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format"""
        result = DateTimeUtils.parse_date("2024-12-02", DateTimeUtils.FORMAT_DATE)
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 2
    
    def test_parse_date_alternative_formats(self):
        """Test parsing various date formats"""
        formats_and_dates = [
            ("2024-12-02", datetime(2024, 12, 2)),
            ("02-12-2024", datetime(2024, 12, 2)),
            ("2024/12/02", datetime(2024, 12, 2)),
        ]
        
        for date_str, expected in formats_and_dates:
            result = DateTimeUtils.parse_date(date_str)
            assert result is not None
            assert result.year == expected.year
            assert result.month == expected.month
            assert result.day == expected.day
    
    def test_parse_date_empty_string(self):
        """Test parsing empty string returns None"""
        result = DateTimeUtils.parse_date("")
        assert result is None
    
    def test_parse_date_invalid_format(self):
        """Test parsing invalid date returns None"""
        result = DateTimeUtils.parse_date("invalid-date")
        assert result is None
    
    def test_parse_date_with_time(self):
        """Test parsing datetime string"""
        result = DateTimeUtils.parse_date("2024-12-02 14:30:00", DateTimeUtils.FORMAT_DATETIME)
        assert result.year == 2024
        assert result.hour == 14
        assert result.minute == 30


class TestDateTimeCalculations:
    """Test date/time calculation functions"""
    
    def test_add_days_positive(self):
        """Test adding positive days"""
        dt = datetime(2024, 12, 1)
        result = DateTimeUtils.add_days(dt, 5)
        assert result.day == 6
        assert result.month == 12
    
    def test_add_days_negative(self):
        """Test subtracting days"""
        dt = datetime(2024, 12, 10)
        result = DateTimeUtils.add_days(dt, -5)
        assert result.day == 5
        assert result.month == 12
    
    def test_add_days_cross_month(self):
        """Test adding days across month boundary"""
        dt = datetime(2024, 11, 28)
        result = DateTimeUtils.add_days(dt, 5)
        assert result.day == 3
        assert result.month == 12
    
    def test_add_months_positive(self):
        """Test adding positive months"""
        dt = datetime(2024, 1, 15)
        result = DateTimeUtils.add_months(dt, 3)
        assert result.month == 4
        assert result.year == 2024
    
    def test_add_months_negative(self):
        """Test subtracting months"""
        dt = datetime(2024, 6, 15)
        result = DateTimeUtils.add_months(dt, -3)
        assert result.month == 3
        assert result.year == 2024
    
    def test_add_months_cross_year(self):
        """Test adding months across year boundary"""
        dt = datetime(2024, 11, 15)
        result = DateTimeUtils.add_months(dt, 3)
        assert result.month == 2
        assert result.year == 2025
    
    def test_add_months_day_adjustment(self):
        """Test month addition with day adjustment"""
        dt = datetime(2024, 1, 31)
        result = DateTimeUtils.add_months(dt, 1)
        # February doesn't have 31 days, should adjust to 29 (2024 is leap year)
        assert result.month == 2
        assert result.day == 29
    
    def test_add_years_positive(self):
        """Test adding positive years"""
        dt = datetime(2024, 6, 15)
        result = DateTimeUtils.add_years(dt, 2)
        assert result.year == 2026
        assert result.month == 6
        assert result.day == 15
    
    def test_add_years_negative(self):
        """Test subtracting years"""
        dt = datetime(2024, 6, 15)
        result = DateTimeUtils.add_years(dt, -2)
        assert result.year == 2022
    
    def test_diff_days_positive(self):
        """Test calculating positive day difference"""
        dt1 = datetime(2024, 12, 10)
        dt2 = datetime(2024, 12, 5)
        result = DateTimeUtils.diff_days(dt1, dt2)
        assert result == 5
    
    def test_diff_days_negative(self):
        """Test calculating negative day difference"""
        dt1 = datetime(2024, 12, 5)
        dt2 = datetime(2024, 12, 10)
        result = DateTimeUtils.diff_days(dt1, dt2)
        assert result == -5
    
    def test_diff_days_same_date(self):
        """Test difference of same dates"""
        dt = datetime(2024, 12, 5)
        result = DateTimeUtils.diff_days(dt, dt)
        assert result == 0
    
    def test_diff_hours_positive(self):
        """Test calculating positive hour difference"""
        dt1 = datetime(2024, 12, 5, 14, 0, 0)
        dt2 = datetime(2024, 12, 5, 10, 0, 0)
        result = DateTimeUtils.diff_hours(dt1, dt2)
        assert result == 4.0
    
    def test_diff_hours_with_minutes(self):
        """Test hour difference with minutes"""
        dt1 = datetime(2024, 12, 5, 14, 30, 0)
        dt2 = datetime(2024, 12, 5, 10, 0, 0)
        result = DateTimeUtils.diff_hours(dt1, dt2)
        assert result == 4.5


class TestDateTimeValidation:
    """Test date/time validation functions"""
    
    def test_is_valid_date_range_valid(self):
        """Test valid date range"""
        start = datetime(2024, 12, 1)
        end = datetime(2024, 12, 10)
        assert DateTimeUtils.is_valid_date_range(start, end) is True
    
    def test_is_valid_date_range_same_date(self):
        """Test same start and end date"""
        dt = datetime(2024, 12, 5)
        assert DateTimeUtils.is_valid_date_range(dt, dt) is True
    
    def test_is_valid_date_range_invalid(self):
        """Test invalid date range (start after end)"""
        start = datetime(2024, 12, 10)
        end = datetime(2024, 12, 1)
        assert DateTimeUtils.is_valid_date_range(start, end) is False
    
    def test_is_valid_date_range_none_start(self):
        """Test validation with None start date"""
        end = datetime(2024, 12, 10)
        assert DateTimeUtils.is_valid_date_range(None, end) is False
    
    def test_is_valid_date_range_none_end(self):
        """Test validation with None end date"""
        start = datetime(2024, 12, 1)
        assert DateTimeUtils.is_valid_date_range(start, None) is False
    
    def test_validate_date_range_valid(self):
        """Test comprehensive date range validation"""
        start = datetime(2024, 12, 1)
        end = datetime(2024, 12, 10)
        is_valid, error = DateTimeUtils.validate_date_range(start, end)
        assert is_valid is True
        assert error == ""
    
    def test_validate_date_range_none_start(self):
        """Test validation error for None start"""
        end = datetime(2024, 12, 10)
        is_valid, error = DateTimeUtils.validate_date_range(None, end)
        assert is_valid is False
        assert "bắt đầu" in error.lower()
    
    def test_validate_date_range_none_end(self):
        """Test validation error for None end"""
        start = datetime(2024, 12, 1)
        is_valid, error = DateTimeUtils.validate_date_range(start, None)
        assert is_valid is False
        assert "kết thúc" in error.lower()
    
    def test_validate_date_range_invalid_order(self):
        """Test validation error for invalid order"""
        start = datetime(2024, 12, 10)
        end = datetime(2024, 12, 1)
        is_valid, error = DateTimeUtils.validate_date_range(start, end)
        assert is_valid is False
        assert "trước" in error.lower()
    
    def test_validate_date_range_max_days_valid(self):
        """Test validation with max days constraint (valid)"""
        start = datetime(2024, 12, 1)
        end = datetime(2024, 12, 10)
        is_valid, error = DateTimeUtils.validate_date_range(start, end, max_days=30)
        assert is_valid is True
    
    def test_validate_date_range_max_days_exceeded(self):
        """Test validation with max days constraint (exceeded)"""
        start = datetime(2024, 12, 1)
        end = datetime(2024, 12, 31)
        is_valid, error = DateTimeUtils.validate_date_range(start, end, max_days=20)
        assert is_valid is False
        assert "20 ngày" in error


class TestTimezoneHandling:
    """Test timezone handling functions"""
    
    def test_now_default_timezone(self):
        """Test getting current time with default timezone"""
        result = DateTimeUtils.now()
        assert result.tzinfo is not None
        assert result.tzinfo.zone == "Asia/Ho_Chi_Minh"
    
    def test_now_custom_timezone(self):
        """Test getting current time with custom timezone"""
        result = DateTimeUtils.now(timezone="UTC")
        assert result.tzinfo is not None
    
    def test_today(self):
        """Test getting today's date"""
        result = DateTimeUtils.today()
        assert isinstance(result, date)
        assert result == date.today()
    
    def test_convert_timezone(self):
        """Test timezone conversion"""
        dt = datetime(2024, 12, 2, 12, 0, 0)
        result = DateTimeUtils.convert_timezone(dt, "UTC", "Asia/Ho_Chi_Minh")
        assert result.tzinfo is not None
        # Ho Chi Minh is UTC+7
        assert result.hour == 19


class TestDateTimeUtilities:
    """Test utility functions"""
    
    def test_get_start_of_day(self):
        """Test getting start of day"""
        dt = datetime(2024, 12, 2, 14, 30, 45)
        result = DateTimeUtils.get_start_of_day(dt)
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
    
    def test_get_end_of_day(self):
        """Test getting end of day"""
        dt = datetime(2024, 12, 2, 14, 30, 45)
        result = DateTimeUtils.get_end_of_day(dt)
        assert result.hour == 23
        assert result.minute == 59
        assert result.second == 59
    
    def test_get_start_of_month(self):
        """Test getting start of month"""
        dt = datetime(2024, 12, 15, 14, 30, 45)
        result = DateTimeUtils.get_start_of_month(dt)
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
    
    def test_get_end_of_month(self):
        """Test getting end of month"""
        dt = datetime(2024, 12, 15, 14, 30, 45)
        result = DateTimeUtils.get_end_of_month(dt)
        assert result.day == 31
        assert result.hour == 23
        assert result.minute == 59
    
    def test_get_end_of_month_february(self):
        """Test end of February in leap year"""
        dt = datetime(2024, 2, 15)
        result = DateTimeUtils.get_end_of_month(dt)
        assert result.day == 29  # 2024 is leap year
    
    def test_is_weekend_saturday(self):
        """Test weekend detection for Saturday"""
        dt = datetime(2024, 11, 30)  # Saturday
        assert DateTimeUtils.is_weekend(dt) is True
    
    def test_is_weekend_sunday(self):
        """Test weekend detection for Sunday"""
        dt = datetime(2024, 12, 1)  # Sunday
        assert DateTimeUtils.is_weekend(dt) is True
    
    def test_is_weekend_weekday(self):
        """Test weekend detection for weekday"""
        dt = datetime(2024, 12, 2)  # Monday
        assert DateTimeUtils.is_weekend(dt) is False
    
    def test_get_weekday_name_vietnamese(self):
        """Test getting Vietnamese weekday name"""
        dt = datetime(2024, 12, 2)  # Monday
        result = DateTimeUtils.get_weekday_name(dt, locale="vi")
        assert result == "Thứ Hai"
    
    def test_get_weekday_name_english(self):
        """Test getting English weekday name"""
        dt = datetime(2024, 12, 2)  # Monday
        result = DateTimeUtils.get_weekday_name(dt, locale="en")
        assert result == "Monday"
    
    def test_get_weekday_name_sunday_vietnamese(self):
        """Test Sunday in Vietnamese"""
        dt = datetime(2024, 12, 1)  # Sunday
        result = DateTimeUtils.get_weekday_name(dt, locale="vi")
        assert result == "Chủ Nhật"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_leap_year_february_29(self):
        """Test leap year handling"""
        dt = datetime(2024, 2, 29)
        result = DateTimeUtils.add_years(dt, 1)
        # 2025 is not a leap year, should adjust to Feb 28
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 28
    
    def test_add_months_to_january_31(self):
        """Test adding months from Jan 31"""
        dt = datetime(2024, 1, 31)
        result = DateTimeUtils.add_months(dt, 1)
        # February has 29 days in 2024
        assert result.month == 2
        assert result.day == 29
    
    def test_year_boundary_calculations(self):
        """Test calculations across year boundaries"""
        dt = datetime(2024, 12, 31, 23, 59, 59)
        result = DateTimeUtils.add_days(dt, 1)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
