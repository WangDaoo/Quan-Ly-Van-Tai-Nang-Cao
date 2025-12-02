"""
Configuration file for Transport Management System
Hệ Thống Quản Lý Vận Tải Toàn Diện
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "transport.db"
BACKUP_DIR = BASE_DIR / "backups"

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "transportapp.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
LOG_STRUCTURED = False  # Enable JSON structured logging
LOG_PERFORMANCE = True  # Enable performance logging

# Application configuration
APP_NAME = "Hệ Thống Quản Lý Vận Tải"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "Transport Management"

# UI Configuration
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768

# Performance configuration
CONNECTION_POOL_SIZE = 5
AUTOCOMPLETE_DEBOUNCE_MS = 300
FILTER_DEBOUNCE_MS = 300
PAGINATION_DEFAULT_SIZE = 100
CACHE_MAX_SIZE = 1000

# Validation configuration
MAX_TEXT_LENGTH = 255
MAX_TEXTAREA_LENGTH = 5000
PHONE_PATTERN = r"^[\d\s\-\+\(\)]+$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
URL_PATTERN = r"^https?://[^\s]+$"

# Formula configuration
SUPPORTED_OPERATORS = ["+", "-", "*", "/"]
FORMULA_FIELD_PATTERN = r"\[([^\]]+)\]"

# Workflow configuration
CONDITION_OPERATORS = [
    "equals",
    "not_equals",
    "contains",
    "not_contains",
    "starts_with",
    "ends_with",
    "greater_than",
    "less_than",
    "greater_or_equal",
    "less_or_equal",
    "is_empty",
    "is_not_empty",
]

LOGIC_OPERATORS = ["AND", "OR"]

# Field types
FIELD_TYPES = [
    "text",
    "number",
    "currency",
    "date",
    "dropdown",
    "checkbox",
    "email",
    "phone",
    "textarea",
    "url",
]

# Validation types
VALIDATION_TYPES = [
    "required",
    "number_only",
    "text_only",
    "no_special_chars",
    "email_format",
    "pattern_matching",
]

# Default departments
DEFAULT_DEPARTMENTS = [
    {"name": "sales", "display_name": "Sales", "description": "Phòng Kinh Doanh"},
    {"name": "processing", "display_name": "Processing", "description": "Phòng Xử Lý"},
    {"name": "accounting", "display_name": "Accounting", "description": "Phòng Kế Toán"},
]

# Company names for price tables
COMPANY_NAMES = ["Company A", "Company B", "Company C"]

# Ensure directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
