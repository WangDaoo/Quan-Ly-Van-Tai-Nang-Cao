"""
Final Testing Checklist for Transport Management System
Comprehensive testing script for pre-release validation

Usage:
    python final_testing_checklist.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime


class TestResult:
    """Store test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.skipped = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
    
    def add_fail(self, test_name, reason=""):
        self.failed.append((test_name, reason))
    
    def add_warning(self, test_name, reason=""):
        self.warnings.append((test_name, reason))
    
    def add_skip(self, test_name, reason=""):
        self.skipped.append((test_name, reason))
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.passed) + len(self.failed) + len(self.warnings) + len(self.skipped)
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"✓ Passed: {len(self.passed)}")
        print(f"✗ Failed: {len(self.failed)}")
        print(f"⚠ Warnings: {len(self.warnings)}")
        print(f"○ Skipped: {len(self.skipped)}")
        
        if self.failed:
            print("\nFailed Tests:")
            for test, reason in self.failed:
                print(f"  ✗ {test}")
                if reason:
                    print(f"    Reason: {reason}")
        
        if self.warnings:
            print("\nWarnings:")
            for test, reason in self.warnings:
                print(f"  ⚠ {test}")
                if reason:
                    print(f"    Reason: {reason}")
        
        print("=" * 70)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def ask_user(question):
    """Ask user a yes/no question"""
    while True:
        response = input(f"{question} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please answer 'y' or 'n'")


def test_build_artifacts(results):
    """Test 1: Build Artifacts"""
    print_section("Test 1: Build Artifacts")
    
    # Check executable
    exe_path = Path('dist/TransportManagementSystem/TransportManagementSystem.exe')
    if exe_path.exists():
        print(f"✓ Executable exists: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        results.add_pass("Executable exists")
    else:
        print(f"✗ Executable not found: {exe_path}")
        results.add_fail("Executable exists", "File not found")
    
    # Check installer
    installer_files = list(Path('Output').glob('TransportManagementSystem_Setup_*.exe'))
    if installer_files:
        installer = installer_files[0]
        print(f"✓ Installer exists: {installer}")
        print(f"  Size: {installer.stat().st_size / (1024*1024):.2f} MB")
        results.add_pass("Installer exists")
    else:
        print("⚠ Installer not found in Output/")
        results.add_warning("Installer exists", "File not found")
    
    # Check documentation
    docs = ['README.md', 'BUILD_INSTRUCTIONS.md', 'INSTALLER_INSTRUCTIONS.md']
    for doc in docs:
        if Path(doc).exists():
            print(f"✓ {doc} exists")
            results.add_pass(f"Documentation: {doc}")
        else:
            print(f"✗ {doc} missing")
            results.add_fail(f"Documentation: {doc}", "File not found")


def test_application_launch(results):
    """Test 2: Application Launch"""
    print_section("Test 2: Application Launch")
    
    print("This test requires manual verification.")
    print("Please launch the application and verify it starts correctly.")
    print("\nSteps:")
    print("1. Navigate to dist/TransportManagementSystem/")
    print("2. Double-click TransportManagementSystem.exe")
    print("3. Wait for the application to load")
    print("4. Verify the main window appears")
    
    if ask_user("\nDid the application launch successfully?"):
        results.add_pass("Application launch")
        
        if ask_user("Did it launch within 10 seconds?"):
            results.add_pass("Startup time")
        else:
            results.add_warning("Startup time", "Slow startup (>10 seconds)")
    else:
        results.add_fail("Application launch", "Application failed to start")
        return
    
    if ask_user("Is the main window displayed correctly?"):
        results.add_pass("Main window display")
    else:
        results.add_fail("Main window display", "Window not displayed correctly")


def test_core_functionality(results):
    """Test 3: Core Functionality"""
    print_section("Test 3: Core Functionality")
    
    print("Test the following core features:")
    
    features = [
        ("Create new trip record", "Trip creation"),
        ("Edit existing trip record", "Trip editing"),
        ("Delete trip record", "Trip deletion"),
        ("Use autocomplete for customer", "Autocomplete"),
        ("Filter table data", "Filtering"),
        ("Sort table columns", "Sorting"),
        ("Copy/paste cells", "Copy/paste"),
        ("Export to Excel", "Excel export"),
        ("Import from Excel", "Excel import"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_dynamic_forms(results):
    """Test 4: Dynamic Forms"""
    print_section("Test 4: Dynamic Forms")
    
    print("Test dynamic form features:")
    
    features = [
        ("Open Field Manager dialog", "Field Manager"),
        ("Add new field configuration", "Add field"),
        ("Edit field configuration", "Edit field"),
        ("Delete field configuration", "Delete field"),
        ("Reorder fields with drag & drop", "Field reordering"),
        ("Form updates with new configuration", "Form refresh"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_formula_engine(results):
    """Test 5: Formula Engine"""
    print_section("Test 5: Formula Engine")
    
    print("Test formula engine features:")
    
    features = [
        ("Open Formula Builder dialog", "Formula Builder"),
        ("Create simple formula (e.g., [A] + [B])", "Simple formula"),
        ("Create complex formula with parentheses", "Complex formula"),
        ("Formula auto-calculates on field change", "Auto-calculation"),
        ("Formula validation shows errors", "Formula validation"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_workflow_automation(results):
    """Test 6: Workflow Automation"""
    print_section("Test 6: Workflow Automation")
    
    print("Test workflow automation features:")
    
    features = [
        ("Open Push Conditions dialog", "Push Conditions dialog"),
        ("Create push condition", "Create condition"),
        ("Test condition evaluation", "Condition evaluation"),
        ("Auto-push when condition met", "Auto-push"),
        ("View workflow history", "Workflow history"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_multi_department(results):
    """Test 7: Multi-Department Support"""
    print_section("Test 7: Multi-Department Support")
    
    print("Test multi-department features:")
    
    features = [
        ("Switch between department tabs", "Department switching"),
        ("Each department has independent data", "Data isolation"),
        ("Department-specific field configurations", "Department configs"),
        ("Push data between departments", "Inter-department push"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_performance(results):
    """Test 8: Performance"""
    print_section("Test 8: Performance")
    
    print("Test performance with large datasets:")
    
    if ask_user("Can you load 1000+ records without lag?"):
        results.add_pass("Large dataset loading")
    else:
        results.add_warning("Large dataset loading", "Performance issues with large datasets")
    
    if ask_user("Is filtering responsive (< 1 second)?"):
        results.add_pass("Filtering performance")
    else:
        results.add_warning("Filtering performance", "Slow filtering")
    
    if ask_user("Is autocomplete responsive (< 500ms)?"):
        results.add_pass("Autocomplete performance")
    else:
        results.add_warning("Autocomplete performance", "Slow autocomplete")
    
    if ask_user("Does Excel export complete in reasonable time?"):
        results.add_pass("Export performance")
    else:
        results.add_warning("Export performance", "Slow export")


def test_error_handling(results):
    """Test 9: Error Handling"""
    print_section("Test 9: Error Handling")
    
    print("Test error handling:")
    
    features = [
        ("Try to save invalid data (shows error)", "Validation errors"),
        ("Try to import invalid Excel file", "Import errors"),
        ("Try to create invalid formula", "Formula errors"),
        ("Check logs/transportapp.log for errors", "Error logging"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_ui_responsiveness(results):
    """Test 10: UI Responsiveness"""
    print_section("Test 10: UI Responsiveness")
    
    print("Test UI responsiveness:")
    
    features = [
        ("Resize window (UI adapts correctly)", "Window resizing"),
        ("All buttons are clickable", "Button functionality"),
        ("All menus work correctly", "Menu functionality"),
        ("Keyboard shortcuts work", "Keyboard shortcuts"),
        ("Tooltips appear on hover", "Tooltips"),
    ]
    
    for feature, test_name in features:
        if ask_user(f"Does '{feature}' work correctly?"):
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"{feature} not working")


def test_data_persistence(results):
    """Test 11: Data Persistence"""
    print_section("Test 11: Data Persistence")
    
    print("Test data persistence:")
    print("\nSteps:")
    print("1. Create some test data")
    print("2. Close the application")
    print("3. Reopen the application")
    print("4. Verify data is still there")
    
    if ask_user("\nIs data persisted correctly after restart?"):
        results.add_pass("Data persistence")
    else:
        results.add_fail("Data persistence", "Data not saved correctly")
    
    if ask_user("Are window settings (size, position) saved?"):
        results.add_pass("Window state persistence")
    else:
        results.add_warning("Window state persistence", "Window settings not saved")


def test_installer(results):
    """Test 12: Installer"""
    print_section("Test 12: Installer")
    
    print("Test the installer (requires clean system or VM):")
    print("\nNote: This test should be done on a system without Python installed")
    
    if ask_user("Have you tested the installer?"):
        if ask_user("Does the installer run without errors?"):
            results.add_pass("Installer execution")
        else:
            results.add_fail("Installer execution", "Installer has errors")
        
        if ask_user("Are all files installed correctly?"):
            results.add_pass("File installation")
        else:
            results.add_fail("File installation", "Files not installed correctly")
        
        if ask_user("Are shortcuts created correctly?"):
            results.add_pass("Shortcut creation")
        else:
            results.add_fail("Shortcut creation", "Shortcuts not created")
        
        if ask_user("Does the application run after installation?"):
            results.add_pass("Post-install execution")
        else:
            results.add_fail("Post-install execution", "App doesn't run after install")
        
        if ask_user("Does the uninstaller work correctly?"):
            results.add_pass("Uninstaller")
        else:
            results.add_fail("Uninstaller", "Uninstaller has issues")
    else:
        results.add_skip("Installer tests", "Not tested yet")


def test_documentation(results):
    """Test 13: Documentation"""
    print_section("Test 13: Documentation")
    
    print("Review documentation:")
    
    docs = [
        ("User Manual is complete and accurate", "User Manual"),
        ("Quick Start Guide is helpful", "Quick Start Guide"),
        ("Technical Documentation is detailed", "Technical Documentation"),
        ("Build Instructions are clear", "Build Instructions"),
        ("Installer Instructions are clear", "Installer Instructions"),
    ]
    
    for doc, test_name in docs:
        if ask_user(f"Is '{doc}'?"):
            results.add_pass(test_name)
        else:
            results.add_warning(test_name, "Documentation needs improvement")


def generate_report(results):
    """Generate detailed test report"""
    print_section("Generating Test Report")
    
    report_path = Path('FINAL_TEST_REPORT.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("FINAL TEST REPORT - Transport Management System\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tester: [Your Name]\n\n")
        
        f.write("SUMMARY\n")
        f.write("-" * 70 + "\n")
        total = len(results.passed) + len(results.failed) + len(results.warnings) + len(results.skipped)
        f.write(f"Total Tests: {total}\n")
        f.write(f"Passed: {len(results.passed)}\n")
        f.write(f"Failed: {len(results.failed)}\n")
        f.write(f"Warnings: {len(results.warnings)}\n")
        f.write(f"Skipped: {len(results.skipped)}\n\n")
        
        if results.passed:
            f.write("PASSED TESTS\n")
            f.write("-" * 70 + "\n")
            for test in results.passed:
                f.write(f"✓ {test}\n")
            f.write("\n")
        
        if results.failed:
            f.write("FAILED TESTS\n")
            f.write("-" * 70 + "\n")
            for test, reason in results.failed:
                f.write(f"✗ {test}\n")
                if reason:
                    f.write(f"  Reason: {reason}\n")
            f.write("\n")
        
        if results.warnings:
            f.write("WARNINGS\n")
            f.write("-" * 70 + "\n")
            for test, reason in results.warnings:
                f.write(f"⚠ {test}\n")
                if reason:
                    f.write(f"  Reason: {reason}\n")
            f.write("\n")
        
        if results.skipped:
            f.write("SKIPPED TESTS\n")
            f.write("-" * 70 + "\n")
            for test, reason in results.skipped:
                f.write(f"○ {test}\n")
                if reason:
                    f.write(f"  Reason: {reason}\n")
            f.write("\n")
        
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 70 + "\n")
        if results.failed:
            f.write("Critical Issues:\n")
            for test, reason in results.failed:
                f.write(f"- Fix: {test}\n")
            f.write("\n")
        
        if results.warnings:
            f.write("Improvements Needed:\n")
            for test, reason in results.warnings:
                f.write(f"- Improve: {test}\n")
            f.write("\n")
        
        if not results.failed and not results.warnings:
            f.write("✓ All tests passed! Application is ready for release.\n\n")
        
        f.write("=" * 70 + "\n")
    
    print(f"✓ Test report saved to: {report_path}")


def main():
    """Main testing process"""
    print("=" * 70)
    print("  FINAL TESTING CHECKLIST")
    print("  Transport Management System v1.0.0")
    print("=" * 70)
    print("\nThis script will guide you through comprehensive testing.")
    print("Please have the application ready to test.")
    print("\nPress Enter to begin...")
    input()
    
    results = TestResult()
    
    # Run all tests
    test_build_artifacts(results)
    test_application_launch(results)
    test_core_functionality(results)
    test_dynamic_forms(results)
    test_formula_engine(results)
    test_workflow_automation(results)
    test_multi_department(results)
    test_performance(results)
    test_error_handling(results)
    test_ui_responsiveness(results)
    test_data_persistence(results)
    test_installer(results)
    test_documentation(results)
    
    # Print summary
    results.print_summary()
    
    # Generate report
    generate_report(results)
    
    # Final recommendations
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    
    if results.failed:
        print("\n⚠ Critical issues found! Please fix before release:")
        for test, reason in results.failed:
            print(f"  - {test}")
        print("\nRun this test again after fixes.")
    elif results.warnings:
        print("\n⚠ Some warnings found. Consider addressing before release:")
        for test, reason in results.warnings:
            print(f"  - {test}")
        print("\nApplication can be released, but improvements recommended.")
    else:
        print("\n✓ All tests passed! Application is ready for release.")
        print("\nProceed to Task 18.4: Release Preparation")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
