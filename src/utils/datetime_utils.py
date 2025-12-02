"""
Datetime Utilities Module

Provides comprehensive date and time handling utilities including:
- Formatting and parsing
- Date calculations
- Timezone handling
- Date range validation

Requirements: 18.1
"""

from datetime import datetime, timedelta, date
from typing import Optional, Tuple
import pytz


class DateTimeUtils:
    """Utility class for date and time operations"""
    
    # Common date formats
    FORMAT_DATE = "%Y-%m-%d"
    FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
    FORMAT_DISPLAY = "%d/%m/%Y"
    FORMAT_DISPLAY_DATETIME = "%d/%m/%Y %H:%M:%S"
    FORMAT_ISO = "%Y-%m-%dT%H:%M:%S"
    
    # Default timezone
    DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh"
    
    @staticmethod
    def format_date(dt: datetime, format_str: str = FORMAT_DISPLAY) -> str:
        """
        Format datetime object to string
        
        Args:
            dt: Datetime object to format
            format_str: Format string (default: DD/MM/YYYY)
            
        Returns:
            Formatted date string
        """
        if dt is None:
            return ""
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = FORMAT_DISPLAY) -> Optional[datetime]:
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date string to parse
            format_str: Format string (default: DD/MM/YYYY)
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            # Try alternative formats
            formats = [
                DateTimeUtils.FORMAT_DATE,
                DateTimeUtils.FORMAT_DATETIME,
                DateTimeUtils.FORMAT_ISO,
                "%d-%m-%Y",
                "%Y/%m/%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
    
    @staticmethod
    def now(timezone: str = DEFAULT_TIMEZONE) -> datetime:
        """
        Get current datetime with timezone
        
        Args:
            timezone: Timezone name (default: Asia/Ho_Chi_Minh)
            
        Returns:
            Current datetime with timezone
        """
        tz = pytz.timezone(timezone)
        return datetime.now(tz)
    
    @staticmethod
    def today() -> date:
        """
        Get today's date
        
        Returns:
            Today's date
        """
        return date.today()
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Add days to datetime
        
        Args:
            dt: Base datetime
            days: Number of days to add (can be negative)
            
        Returns:
            New datetime with days added
        """
        return dt + timedelta(days=days)
    
    @staticmethod
    def add_months(dt: datetime, months: int) -> datetime:
        """
        Add months to datetime
        
        Args:
            dt: Base datetime
            months: Number of months to add (can be negative)
            
        Returns:
            New datetime with months added
        """
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return dt.replace(year=year, month=month, day=day)
    
    @staticmethod
    def add_years(dt: datetime, years: int) -> datetime:
        """
        Add years to datetime
        
        Args:
            dt: Base datetime
            years: Number of years to add (can be negative)
            
        Returns:
            New datetime with years added
        """
        return DateTimeUtils.add_months(dt, years * 12)
    
    @staticmethod
    def diff_days(dt1: datetime, dt2: datetime) -> int:
        """
        Calculate difference in days between two dates
        
        Args:
            dt1: First datetime
            dt2: Second datetime
            
        Returns:
            Number of days between dates (dt1 - dt2)
        """
        return (dt1.date() - dt2.date()).days
    
    @staticmethod
    def diff_hours(dt1: datetime, dt2: datetime) -> float:
        """
        Calculate difference in hours between two datetimes
        
        Args:
            dt1: First datetime
            dt2: Second datetime
            
        Returns:
            Number of hours between datetimes (dt1 - dt2)
        """
        return (dt1 - dt2).total_seconds() / 3600
    
    @staticmethod
    def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
        """
        Validate that start_date is before or equal to end_date
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            True if valid range, False otherwise
        """
        if start_date is None or end_date is None:
            return False
        return start_date <= end_date
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime, 
                          max_days: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate date range with optional maximum days constraint
        
        Args:
            start_date: Start date
            end_date: End date
            max_days: Maximum allowed days in range (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date is None:
            return False, "Ngày bắt đầu không được để trống"
        
        if end_date is None:
            return False, "Ngày kết thúc không được để trống"
        
        if start_date > end_date:
            return False, "Ngày bắt đầu phải trước hoặc bằng ngày kết thúc"
        
        if max_days is not None:
            days_diff = DateTimeUtils.diff_days(end_date, start_date)
            if days_diff > max_days:
                return False, f"Khoảng thời gian không được vượt quá {max_days} ngày"
        
        return True, ""
    
    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """
        Convert datetime from one timezone to another
        
        Args:
            dt: Datetime to convert
            from_tz: Source timezone name
            to_tz: Target timezone name
            
        Returns:
            Datetime in target timezone
        """
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Localize if naive
        if dt.tzinfo is None:
            dt = from_timezone.localize(dt)
        
        return dt.astimezone(to_timezone)
    
    @staticmethod
    def get_start_of_day(dt: datetime) -> datetime:
        """
        Get start of day (00:00:00)
        
        Args:
            dt: Input datetime
            
        Returns:
            Datetime at start of day
        """
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_day(dt: datetime) -> datetime:
        """
        Get end of day (23:59:59)
        
        Args:
            dt: Input datetime
            
        Returns:
            Datetime at end of day
        """
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def get_start_of_month(dt: datetime) -> datetime:
        """
        Get start of month (first day at 00:00:00)
        
        Args:
            dt: Input datetime
            
        Returns:
            Datetime at start of month
        """
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_month(dt: datetime) -> datetime:
        """
        Get end of month (last day at 23:59:59)
        
        Args:
            dt: Input datetime
            
        Returns:
            Datetime at end of month
        """
        next_month = DateTimeUtils.add_months(dt, 1)
        first_of_next = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_of_next - timedelta(microseconds=1)
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        Check if date is weekend (Saturday or Sunday)
        
        Args:
            dt: Datetime to check
            
        Returns:
            True if weekend, False otherwise
        """
        return dt.weekday() >= 5
    
    @staticmethod
    def get_weekday_name(dt: datetime, locale: str = "vi") -> str:
        """
        Get weekday name
        
        Args:
            dt: Datetime
            locale: Locale for weekday name (vi or en)
            
        Returns:
            Weekday name
        """
        weekdays_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        weekdays_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        weekday = dt.weekday()
        
        if locale == "vi":
            return weekdays_vi[weekday]
        else:
            return weekdays_en[weekday]
