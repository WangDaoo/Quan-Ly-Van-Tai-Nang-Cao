"""
Build installer script for Transport Management System
Automates the Inno Setup compilation process

Prerequisites:
1. Inno Setup must be installed (https://jrsoftware.org/isinfo.php)
2. Application must be built with PyInstaller first (run build.py)

Usage:
    python build_installer.py
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def check_inno_setup():
    """Check if Inno Setup is installed"""
    print_header("Checking Inno Setup Installation")
    
    # Common Inno Setup installation paths
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            print(f"✓ Inno Setup found at: {path}")
            return path
    
    print("❌ Inno Setup not found!")
    print("\nPlease install Inno Setup from:")
    print("https://jrsoftware.org/isinfo.php")
    print("\nAfter installation, run this script again.")
    return None


def check_build_exists():
    """Check if PyInstaller build exists"""
    print_header("Checking PyInstaller Build")
    
    dist_dir = Path('dist/TransportManagementSystem')
    exe_file = dist_dir / 'TransportManagementSystem.exe'
    
    if not dist_dir.exists():
        print("❌ Build directory not found!")
        print("Please run build.py first to create the executable.")
        return False
    
    if not exe_file.exists():
        print("❌ Executable not found!")
        print("Please run build.py first to create the executable.")
        return False
    
    print(f"✓ Build found at: {dist_dir}")
    print(f"✓ Executable: {exe_file}")
    return True


def check_required_files():
    """Check if all required files for installer exist"""
    print_header("Checking Required Files")
    
    required_files = [
        'installer_setup.iss',
        'LICENSE.txt',
        'INSTALL_INFO.txt',
        'README.md',
        'BUILD_INSTRUCTIONS.md',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)
    
    # Check for icon (optional)
    icon_path = Path('resources/icon.ico')
    if icon_path.exists():
        print(f"✓ resources/icon.ico (optional)")
    else:
        print(f"⚠ resources/icon.ico missing (optional - will use default icon)")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("\n✓ All required files present")
    return True


def create_output_directory():
    """Create output directory for installer"""
    print_header("Creating Output Directory")
    
    output_dir = Path('Output')
    output_dir.mkdir(exist_ok=True)
    
    print(f"✓ Output directory ready: {output_dir}")


def compile_installer(iscc_path):
    """Compile the installer using Inno Setup"""
    print_header("Compiling Installer")
    
    script_file = 'installer_setup.iss'
    
    print(f"Compiling {script_file}...")
    print("This may take a few minutes...\n")
    
    try:
        result = subprocess.run(
            [iscc_path, script_file],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        print("\n✓ Installer compiled successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def verify_installer():
    """Verify the installer was created"""
    print_header("Verifying Installer")
    
    output_dir = Path('Output')
    
    # Find the installer file
    installer_files = list(output_dir.glob('TransportManagementSystem_Setup_*.exe'))
    
    if not installer_files:
        print("❌ Installer file not found!")
        return False
    
    installer_file = installer_files[0]
    
    print(f"✓ Installer created: {installer_file}")
    print(f"✓ Size: {installer_file.stat().st_size / (1024*1024):.2f} MB")
    
    return True


def create_installer_readme():
    """Create README for the installer"""
    print_header("Creating Installer README")
    
    readme_path = Path('Output/README.txt')
    
    readme_content = """
Transport Management System Installer
======================================

This installer will install the Transport Management System on your computer.

INSTALLATION:
1. Double-click the installer executable
2. Follow the installation wizard
3. Choose installation directory
4. Select additional options (desktop shortcut, etc.)
5. Click Install

SYSTEM REQUIREMENTS:
- Windows 10 (64-bit) or later
- 4GB RAM minimum
- 500MB free disk space

AFTER INSTALLATION:
- Launch from Start Menu or Desktop shortcut
- Read the Quick Start Guide in the docs folder
- Sample data will be loaded on first run

UNINSTALLATION:
- Use Windows Settings > Apps > Installed Apps
- Or use the uninstaller from Start Menu

For more information, see INSTALL_INFO.txt included in the installer.

© 2024 Transport Management. All rights reserved.
"""
    
    readme_path.write_text(readme_content.strip(), encoding='utf-8')
    print(f"✓ Created {readme_path}")


def main():
    """Main build process"""
    print_header("Transport Management System - Installer Build Script")
    
    # Step 1: Check Inno Setup
    iscc_path = check_inno_setup()
    if not iscc_path:
        sys.exit(1)
    
    # Step 2: Check PyInstaller build
    if not check_build_exists():
        sys.exit(1)
    
    # Step 3: Check required files
    if not check_required_files():
        sys.exit(1)
    
    # Step 4: Create output directory
    create_output_directory()
    
    # Step 5: Compile installer
    if not compile_installer(iscc_path):
        sys.exit(1)
    
    # Step 6: Verify installer
    if not verify_installer():
        sys.exit(1)
    
    # Step 7: Create installer README
    create_installer_readme()
    
    # Success
    print_header("Installer Build Completed Successfully!")
    print("The installer is located in: Output/")
    print("\nNext steps:")
    print("1. Test the installer on a clean system")
    print("2. Verify all features work after installation")
    print("3. Test the uninstaller")
    print("4. Proceed to final testing (task 18.3)")


if __name__ == "__main__":
    main()
