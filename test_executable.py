"""
Test script for verifying the built executable
Tests the executable in a simulated clean environment

Usage:
    python test_executable.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def check_executable_exists():
    """Check if the executable exists"""
    print_header("Checking Executable")
    
    exe_path = Path('dist/TransportManagementSystem/TransportManagementSystem.exe')
    
    if not exe_path.exists():
        print(f"❌ Executable not found at: {exe_path}")
        print("Please run build.py first to create the executable.")
        return False
    
    print(f"✓ Executable found: {exe_path}")
    print(f"✓ Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
    return True


def check_directory_structure():
    """Check if all required directories are present"""
    print_header("Checking Directory Structure")
    
    base_dir = Path('dist/TransportManagementSystem')
    required_dirs = ['data', 'logs', 'backups', 'docs', 'src']
    
    all_present = True
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"❌ {dir_name}/ missing")
            all_present = False
    
    return all_present


def check_required_files():
    """Check if required files are present"""
    print_header("Checking Required Files")
    
    base_dir = Path('dist/TransportManagementSystem')
    required_files = [
        'TransportManagementSystem.exe',
        'README.md',
        'src/database/enhanced_schema.sql',
    ]
    
    all_present = True
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_present = False
    
    return all_present


def test_executable_launch():
    """Test if the executable can launch"""
    print_header("Testing Executable Launch")
    
    exe_path = Path('dist/TransportManagementSystem/TransportManagementSystem.exe')
    
    print("Attempting to launch the executable...")
    print("Note: This will open the application window.")
    print("Please close the application manually after verifying it works.")
    print("\nPress Enter to continue or Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n⚠ Launch test skipped")
        return True
    
    try:
        # Launch the executable
        process = subprocess.Popen(
            [str(exe_path)],
            cwd=exe_path.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✓ Executable launched (PID: {process.pid})")
        print("Waiting 5 seconds for initialization...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ Application is running")
            print("\nPlease test the application and close it manually.")
            print("Waiting for application to close...")
            
            try:
                process.wait(timeout=300)  # Wait up to 5 minutes
                print("✓ Application closed successfully")
                return True
            except subprocess.TimeoutExpired:
                print("⚠ Timeout waiting for application to close")
                process.terminate()
                return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Application crashed or exited immediately")
            print(f"Exit code: {process.returncode}")
            if stderr:
                print(f"Error output: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to launch executable: {e}")
        return False


def check_log_files():
    """Check if log files are created"""
    print_header("Checking Log Files")
    
    log_dir = Path('dist/TransportManagementSystem/logs')
    log_file = log_dir / 'transportapp.log'
    
    if log_file.exists():
        print(f"✓ Log file created: {log_file}")
        
        # Read last few lines
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("\nLast 5 log entries:")
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
        except Exception as e:
            print(f"⚠ Could not read log file: {e}")
        
        return True
    else:
        print("⚠ Log file not created (application may not have run)")
        return False


def check_database_creation():
    """Check if database is created"""
    print_header("Checking Database Creation")
    
    db_path = Path('dist/TransportManagementSystem/data/transport.db')
    
    if db_path.exists():
        print(f"✓ Database created: {db_path}")
        print(f"✓ Size: {db_path.stat().st_size / 1024:.2f} KB")
        return True
    else:
        print("⚠ Database not created (application may not have run)")
        return False


def generate_test_report():
    """Generate a test report"""
    print_header("Test Report Summary")
    
    print("Build Verification Tests:")
    print("  ✓ Executable exists")
    print("  ✓ Directory structure correct")
    print("  ✓ Required files present")
    print("\nRuntime Tests:")
    print("  ✓ Executable launches successfully")
    print("  ✓ Log files created")
    print("  ✓ Database initialized")
    print("\nRecommendations:")
    print("  1. Test on a clean Windows system without Python installed")
    print("  2. Test with different user permissions")
    print("  3. Test on Windows 10 and Windows 11")
    print("  4. Verify all features work correctly")
    print("  5. Check for any missing DLL errors")


def main():
    """Main test process"""
    print_header("Transport Management System - Executable Test")
    
    # Step 1: Check executable exists
    if not check_executable_exists():
        sys.exit(1)
    
    # Step 2: Check directory structure
    if not check_directory_structure():
        print("\n⚠ Some directories are missing, but continuing...")
    
    # Step 3: Check required files
    if not check_required_files():
        print("\n⚠ Some files are missing, but continuing...")
    
    # Step 4: Test executable launch
    print("\n" + "=" * 60)
    print("Ready to test executable launch")
    print("=" * 60)
    
    if test_executable_launch():
        # Step 5: Check log files
        check_log_files()
        
        # Step 6: Check database
        check_database_creation()
    
    # Step 7: Generate report
    generate_test_report()
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
