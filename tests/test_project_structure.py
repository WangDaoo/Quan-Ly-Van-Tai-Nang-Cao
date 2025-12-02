"""
Test project structure and basic imports
"""

import pytest
from pathlib import Path


def test_project_directories_exist():
    """Test that all required directories exist"""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "src",
        "src/gui",
        "src/gui/widgets",
        "src/gui/dialogs",
        "src/services",
        "src/models",
        "src/database",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/performance",
        "tests/fixtures",
        "data",
        "logs",
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} is not a directory"


def test_required_files_exist():
    """Test that all required files exist"""
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "src/__init__.py",
        "src/utils/logger.py",
    ]
    
    for file_path in required_files:
        full_path = base_dir / file_path
        assert full_path.exists(), f"File {file_path} does not exist"
        assert full_path.is_file(), f"{file_path} is not a file"


def test_config_import():
    """Test that config module can be imported"""
    import config
    
    assert hasattr(config, "APP_NAME")
    assert hasattr(config, "APP_VERSION")
    assert hasattr(config, "DATABASE_PATH")
    assert hasattr(config, "LOG_FILE")


def test_logger_import():
    """Test that logger module can be imported"""
    from src.utils.logger import setup_logging, get_logger
    
    logger = get_logger("test")
    assert logger is not None


def test_requirements_file_format():
    """Test that requirements.txt is properly formatted"""
    base_dir = Path(__file__).parent.parent
    req_file = base_dir / "requirements.txt"
    
    with open(req_file, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Check that we have the required packages
    required_packages = ["PyQt6", "pandas", "openpyxl", "pydantic", "pytest"]
    
    for package in required_packages:
        assert any(package in line for line in lines), f"Package {package} not found in requirements.txt"


def test_main_module_syntax():
    """Test that main.py has valid Python syntax"""
    import ast
    base_dir = Path(__file__).parent.parent
    main_file = base_dir / "main.py"
    
    with open(main_file, "r", encoding="utf-8") as f:
        code = f.read()
    
    # This will raise SyntaxError if invalid
    ast.parse(code)
