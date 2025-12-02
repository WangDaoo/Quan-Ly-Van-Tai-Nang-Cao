"""
Build script for Transport Management System
Automates the PyInstaller build process with pre-build checks

Usage:
    python build.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def check_requirements():
    """Check if all required packages are installed"""
    print_header("Checking Requirements")
    
    required_packages = [
        'PyQt6',
        'pandas',
        'openpyxl',
        'pydantic',
        'psutil',
        'pyinstaller'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All required packages are installed")
    return True


def clean_build_directories():
    """Clean previous build artifacts"""
    print_header("Cleaning Build Directories")
    
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_path)
    
    print("✓ Build directories cleaned")


def ensure_directories():
    """Ensure required directories exist"""
    print_header("Ensuring Required Directories")
    
    directories = [
        'data',
        'logs',
        'backups',
        'docs'
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep if directory is empty
        gitkeep = dir_path / '.gitkeep'
        if not any(dir_path.iterdir()) or not gitkeep.exists():
            gitkeep.touch()
        
        print(f"✓ {dir_name}/ exists")
    
    print("\n✓ All required directories exist")


def run_pyinstaller():
    """Run PyInstaller with the spec file"""
    print_header("Running PyInstaller")
    
    spec_file = 'transport_app.spec'
    
    if not Path(spec_file).exists():
        print(f"❌ Spec file '{spec_file}' not found!")
        return False
    
    print(f"Building with {spec_file}...")
    
    try:
        result = subprocess.run(
            ['pyinstaller', spec_file, '--clean'],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        print("\n✓ Build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found! Please install it with: pip install pyinstaller")
        return False


def verify_build():
    """Verify the build output"""
    print_header("Verifying Build")
    
    dist_dir = Path('dist/TransportManagementSystem')
    
    if not dist_dir.exists():
        print("❌ Build directory not found!")
        return False
    
    exe_file = dist_dir / 'TransportManagementSystem.exe'
    
    if not exe_file.exists():
        print("❌ Executable not found!")
        return False
    
    print(f"✓ Executable found: {exe_file}")
    print(f"✓ Size: {exe_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Check for required directories
    required_dirs = ['data', 'logs', 'backups', 'docs', 'src']
    
    for dir_name in required_dirs:
        dir_path = dist_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory included")
        else:
            print(f"⚠ {dir_name}/ directory missing")
    
    print("\n✓ Build verification completed")
    return True


def create_readme():
    """Create README for the distribution"""
    print_header("Creating Distribution README")
    
    dist_dir = Path('dist/TransportManagementSystem')
    readme_path = dist_dir / 'README_DISTRIBUTION.txt'
    
    readme_content = """
Hệ Thống Quản Lý Vận Tải Toàn Diện
Transport Management System v1.0.0

INSTALLATION:
1. Extract all files to a folder on your computer
2. Run TransportManagementSystem.exe to start the application

FIRST RUN:
- The application will automatically create the database
- Sample data will be loaded on first run
- All data is stored in the 'data' folder

FOLDERS:
- data/     : Database files
- logs/     : Application logs
- backups/  : Database backups
- docs/     : User documentation

REQUIREMENTS:
- Windows 10 or later (64-bit)
- 4GB RAM minimum
- 100MB free disk space

SUPPORT:
For help and documentation, see the files in the docs/ folder:
- USER_MANUAL.md          : Complete user guide
- QUICK_START_GUIDE.md    : Quick start tutorial
- TECHNICAL_DOCUMENTATION.md : Technical details

TROUBLESHOOTING:
- If the application doesn't start, check logs/transportapp.log
- Make sure you have write permissions in the installation folder
- Try running as administrator if you encounter permission issues

© 2024 Transport Management. All rights reserved.
"""
    
    readme_path.write_text(readme_content.strip(), encoding='utf-8')
    print(f"✓ Created {readme_path}")


def main():
    """Main build process"""
    print_header("Transport Management System - Build Script")
    
    # Step 1: Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Step 2: Clean previous builds
    clean_build_directories()
    
    # Step 3: Ensure directories exist
    ensure_directories()
    
    # Step 4: Run PyInstaller
    if not run_pyinstaller():
        sys.exit(1)
    
    # Step 5: Verify build
    if not verify_build():
        sys.exit(1)
    
    # Step 6: Create distribution README
    create_readme()
    
    # Success
    print_header("Build Completed Successfully!")
    print("The executable is located in: dist/TransportManagementSystem/")
    print("You can now test the application or create an installer.")
    print("\nNext steps:")
    print("1. Test the executable on a clean system")
    print("2. Create an installer with Inno Setup (see task 18.2)")
    print("3. Perform final testing (see task 18.3)")


if __name__ == "__main__":
    main()
