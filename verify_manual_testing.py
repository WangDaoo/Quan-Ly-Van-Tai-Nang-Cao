"""
Quick verification script for manual testing tools
"""

import sys
from pathlib import Path

def verify_files_exist():
    """Verify all manual testing files exist"""
    print("Verifying manual testing files...")
    print("="*80)
    
    files_to_check = [
        "docs/MANUAL_TESTING_GUIDE.md",
        "tests/manual/__init__.py",
        "tests/manual/manual_test_helper.py",
        "tests/manual/interactive_test_checklist.py",
        "tests/manual/README.md",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        path = Path(file_path)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    print("="*80)
    return all_exist

def verify_imports():
    """Verify imports work"""
    print("\nVerifying imports...")
    print("="*80)
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6.QtWidgets imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyQt6.QtWidgets: {e}")
        return False
    
    try:
        from PyQt6.QtCore import Qt
        print("✅ PyQt6.QtCore imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyQt6.QtCore: {e}")
        return False
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from tests.manual import ManualTestHelper, InteractiveTestChecklist
        print("✅ Manual testing modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import manual testing modules: {e}")
        return False
    
    print("="*80)
    return True

def verify_database():
    """Verify database exists"""
    print("\nVerifying database...")
    print("="*80)
    
    try:
        from config import DATABASE_PATH
        db_path = Path(DATABASE_PATH)
        
        if db_path.exists():
            print(f"✅ Database exists at: {DATABASE_PATH}")
            
            # Check database size
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"   Database size: {size_mb:.2f} MB")
            
            return True
        else:
            print(f"⚠️  Database not found at: {DATABASE_PATH}")
            print("   Run the application first to create the database")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    
    print("="*80)

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*80)
    print("MANUAL TESTING TOOLS - USAGE INSTRUCTIONS")
    print("="*80)
    print()
    print("1. Manual Testing Guide:")
    print("   Location: docs/MANUAL_TESTING_GUIDE.md")
    print("   Open this file to see comprehensive test cases")
    print()
    print("2. Automated Verification:")
    print("   Command: python tests/manual/manual_test_helper.py")
    print("   This will verify database structure and optionally launch GUI tests")
    print()
    print("3. Interactive Test Checklist:")
    print("   Command: python tests/manual/interactive_test_checklist.py")
    print("   This launches a GUI application for guided manual testing")
    print()
    print("="*80)
    print()

def main():
    """Main verification function"""
    print("\n🧪 Manual Testing Tools Verification")
    print("="*80)
    print()
    
    # Verify files
    files_ok = verify_files_exist()
    
    # Verify imports
    imports_ok = verify_imports()
    
    # Verify database
    db_ok = verify_database()
    
    # Print summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Files: {'✅ All files present' if files_ok else '❌ Some files missing'}")
    print(f"Imports: {'✅ All imports successful' if imports_ok else '❌ Import errors'}")
    print(f"Database: {'✅ Database ready' if db_ok else '⚠️  Database needs setup'}")
    print("="*80)
    
    if files_ok and imports_ok:
        print("\n✅ Manual testing tools are ready to use!")
        print_usage_instructions()
        
        # Ask if user wants to run tests
        print("Would you like to:")
        print("1. Run automated verification (manual_test_helper.py)")
        print("2. Launch interactive checklist (interactive_test_checklist.py)")
        print("3. Exit")
        print()
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == "1":
            print("\nLaunching automated verification...")
            import subprocess
            subprocess.run([sys.executable, "tests/manual/manual_test_helper.py"])
        elif choice == "2":
            print("\nLaunching interactive checklist...")
            import subprocess
            subprocess.run([sys.executable, "tests/manual/interactive_test_checklist.py"])
        else:
            print("\nExiting. Run the tools manually when ready.")
    else:
        print("\n❌ Please fix the issues above before using manual testing tools")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
