# Build Instructions - Transport Management System

This document provides detailed instructions for building the Transport Management System executable using PyInstaller.

## Prerequisites

### Required Software
- Python 3.10 or later
- pip (Python package manager)
- All dependencies from requirements.txt

### Required Packages
```bash
pip install -r requirements.txt
```

Key packages:
- PyQt6 >= 6.6.0
- pandas >= 2.1.0
- openpyxl >= 3.1.0
- pydantic >= 2.5.0
- pyinstaller >= 6.0.0

## Build Process

### Method 1: Using Build Script (Recommended)

The easiest way to build the application is using the automated build script:

```bash
python build.py
```

This script will:
1. Check all required packages are installed
2. Clean previous build artifacts
3. Ensure required directories exist
4. Run PyInstaller with the spec file
5. Verify the build output
6. Create distribution README

### Method 2: Manual Build

If you prefer to build manually:

```bash
# Clean previous builds
rmdir /s /q build dist

# Run PyInstaller
pyinstaller transport_app.spec --clean
```

## Build Output

After a successful build, you'll find:

```
dist/
└── TransportManagementSystem/
    ├── TransportManagementSystem.exe  (Main executable)
    ├── README.md                      (Project README)
    ├── README_DISTRIBUTION.txt        (Distribution guide)
    ├── data/                          (Database directory)
    ├── logs/                          (Log files directory)
    ├── backups/                       (Backup directory)
    ├── docs/                          (Documentation)
    ├── src/                           (Source resources)
    └── [Various DLL and support files]
```

## Testing the Build

### Automated Testing

Use the test script to verify the build:

```bash
python test_executable.py
```

This will:
- Check executable exists
- Verify directory structure
- Test executable launch
- Check log file creation
- Verify database initialization

### Manual Testing

1. Navigate to `dist/TransportManagementSystem/`
2. Double-click `TransportManagementSystem.exe`
3. Verify the application launches
4. Test core functionality:
   - Create a new trip record
   - Edit existing records
   - Use autocomplete features
   - Test Excel import/export
   - Verify filtering works
   - Test formula calculations

### Clean System Testing

**Important**: Test on a system without Python installed to ensure all dependencies are bundled correctly.

1. Copy the entire `dist/TransportManagementSystem/` folder to a clean Windows system
2. Run the executable
3. Verify all features work correctly
4. Check for any missing DLL errors

## Troubleshooting

### Common Issues

#### 1. Missing Module Errors

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**: Add the missing module to `hiddenimports` in `transport_app.spec`:

```python
hiddenimports=[
    # ... existing imports
    'missing_module_name',
]
```

#### 2. PyQt6 Plugin Errors

**Error**: `Could not find the Qt platform plugin "windows"`

**Solution**: This is usually handled automatically, but if it occurs, ensure PyQt6 is properly installed and try rebuilding with `--clean` flag.

#### 3. Large Executable Size

The executable may be 100-200 MB due to bundled dependencies. This is normal for PyQt6 applications.

**To reduce size**:
- Enable UPX compression (already enabled in spec file)
- Exclude unnecessary modules in the `excludes` list
- Consider using `--onefile` mode (not recommended for this app due to slower startup)

#### 4. Slow Startup

**Issue**: Application takes long to start

**Solutions**:
- Use `--onedir` mode (current default) instead of `--onefile`
- Optimize imports in main.py
- Use lazy loading for heavy modules

#### 5. Database Errors

**Error**: Database file not found or permission errors

**Solution**: Ensure the `data/` directory is included in the build and has write permissions.

## Build Configuration

### PyInstaller Spec File

The `transport_app.spec` file contains all build configuration:

- **Analysis**: Defines what to include/exclude
- **PYZ**: Python archive configuration
- **EXE**: Executable configuration
- **COLLECT**: Final collection of all files

### Key Configuration Options

```python
# Console mode (False = GUI app, no console window)
console=False

# UPX compression (reduces size)
upx=True

# Icon (add when available)
icon='resources/icon.ico'
```

## Advanced Options

### Creating a Single-File Executable

To create a single .exe file instead of a folder:

```python
# In transport_app.spec, replace EXE section with:
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
```

**Note**: Single-file mode has slower startup time and is not recommended for this application.

### Debug Mode

To enable debug output for troubleshooting:

```python
# In transport_app.spec:
exe = EXE(
    # ...
    debug=True,  # Enable debug mode
    console=True,  # Show console for debug output
    # ...
)
```

## Build Checklist

Before releasing:

- [ ] All tests pass
- [ ] Build completes without errors
- [ ] Executable launches successfully
- [ ] All features work correctly
- [ ] Tested on clean Windows system
- [ ] No missing DLL errors
- [ ] Log files are created properly
- [ ] Database initializes correctly
- [ ] Documentation is included
- [ ] File size is reasonable (< 300 MB)

## Next Steps

After successful build:

1. **Create Installer** (Task 18.2)
   - Use Inno Setup to create Windows installer
   - Add application icon and branding
   - Include uninstaller

2. **Final Testing** (Task 18.3)
   - Comprehensive manual testing
   - Test on different Windows versions
   - Performance optimization

3. **Release Preparation** (Task 18.4)
   - Create release notes
   - Prepare documentation package
   - Setup backup/restore utilities

## Support

For build issues:
1. Check the build log in the console output
2. Review PyInstaller warnings
3. Test with `--debug all` flag for detailed output
4. Check `logs/transportapp.log` for runtime errors

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Packaging Guide](https://packaging.python.org/)
