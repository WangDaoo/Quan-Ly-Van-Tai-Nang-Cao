"""
Unit tests for manual testing tools
"""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.manual.manual_test_helper import ManualTestHelper


class TestManualTestHelper:
    """Test ManualTestHelper class"""
    
    def test_setup_database(self):
        """Test database setup"""
        helper = ManualTestHelper()
        assert helper.setup_database() is True
        assert helper.db_manager is not None
    
    def test_verify_database_structure(self):
        """Test database structure verification"""
        helper = ManualTestHelper()
        helper.setup_database()
        
        results = helper.verify_database_structure()
        assert len(results) > 0
        
        # Check that all expected tables are verified
        table_names = [r[0] for r in results]
        assert any("trips" in name for name in table_names)
        assert any("company_prices" in name for name in table_names)
        assert any("departments" in name for name in table_names)
    
    def test_verify_sample_data(self):
        """Test sample data verification"""
        helper = ManualTestHelper()
        helper.setup_database()
        
        results = helper.verify_sample_data()
        assert len(results) > 0
        
        # Check that data checks are performed
        check_names = [r[0] for r in results]
        assert any("Trips" in name for name in check_names)
        assert any("Company prices" in name for name in check_names)
        assert any("Departments" in name for name in check_names)
    
    def test_print_results(self):
        """Test results printing"""
        helper = ManualTestHelper()
        helper.setup_database()
        
        results = {
            "Test Category": [
                ("Test 1", True, "Description 1"),
                ("Test 2", False, "Description 2"),
                ("Test 3", True, "Description 3"),
            ]
        }
        
        passed, total = helper.print_results(results)
        assert total == 3
        assert passed == 2


class TestManualTestingFiles:
    """Test that all manual testing files exist"""
    
    def test_manual_testing_guide_exists(self):
        """Test that manual testing guide exists"""
        guide_path = Path(__file__).parent.parent.parent / "docs" / "MANUAL_TESTING_GUIDE.md"
        assert guide_path.exists()
        
        # Check file has content
        content = guide_path.read_text(encoding='utf-8')
        assert len(content) > 1000
        assert "GUI Interactions" in content
        assert "Keyboard Shortcuts" in content
        assert "Responsive Design" in content
        assert "Error Scenarios" in content
    
    def test_manual_test_helper_exists(self):
        """Test that manual test helper exists"""
        helper_path = Path(__file__).parent / "manual_test_helper.py"
        assert helper_path.exists()
    
    def test_interactive_checklist_exists(self):
        """Test that interactive checklist exists"""
        checklist_path = Path(__file__).parent / "interactive_test_checklist.py"
        assert checklist_path.exists()
    
    def test_readme_exists(self):
        """Test that README exists"""
        readme_path = Path(__file__).parent / "README.md"
        assert readme_path.exists()
        
        # Check README has content
        content = readme_path.read_text(encoding='utf-8')
        assert "Manual Testing Tools" in content
        assert "Usage" in content


class TestManualTestingImports:
    """Test that manual testing modules can be imported"""
    
    def test_import_manual_test_helper(self):
        """Test importing ManualTestHelper"""
        from tests.manual.manual_test_helper import ManualTestHelper
        assert ManualTestHelper is not None
    
    def test_import_interactive_checklist(self):
        """Test importing InteractiveTestChecklist"""
        from tests.manual.interactive_test_checklist import InteractiveTestChecklist
        assert InteractiveTestChecklist is not None
    
    def test_import_from_init(self):
        """Test importing from __init__.py"""
        from tests.manual import ManualTestHelper, InteractiveTestChecklist
        assert ManualTestHelper is not None
        assert InteractiveTestChecklist is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
