# Installer Instructions - Transport Management System

This document provides detailed instructions for creating a Windows installer using Inno Setup.

## Prerequisites

### Required Software

1. **Inno Setup 6.x**
   - Download from: https://jrsoftware.org/isinfo.php
   - Install with default options
   - Version 6.0 or later recommended

2. **PyInstaller Build**
   - Must complete Task 18.1 first
   - Run `python build.py` to create the executable
   - Verify `dist/TransportManagementSystem/` exists

### Required Files

The following files must exist before building the installer:

- `installer_setup.iss` - Inno Setup script
- `LICENSE.txt` - License agreement
- `INSTALL_INFO.txt` - Installation information
- `README.md` - Project README
- `BUILD_INSTRUCTIONS.md` - Build documentation
- `dist/TransportManagementSystem/` - Built application

### Optional Files

- `resources/icon.ico` - Application icon (recommended)

## Building the Installer

### Method 1: Using Build Script (Recommended)

The easiest way to build the installer:

```bash
python build_installer.py
```

This script will:
1. Check if Inno Setup is installed
2. Verify PyInstaller build exists
3. Check all required files are present
4. Create output directory
5. Compile the installer
6. Verify the installer was created
7. Create installer README

### Method 2: Manual Build

If you prefer to build manually:

1. Open Inno Setup Compiler
2. File > Open > Select `installer_setup.iss`
3. Build > Compile
4. Wait for compilation to complete
5. Check `Output/` folder for the installer

### Method 3: Command Line

Using Inno Setup command line compiler:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_setup.iss
```

## Installer Output

After successful build, you'll find:

```
Output/
├── TransportManagementSystem_Setup_v1.0.0.exe  (Installer)
└── README.txt                                   (Installer guide)
```

Typical installer size: 150-250 MB (includes all dependencies)

## Installer Features

### Installation Options

1. **Installation Directory**
   - Default: `C:\Program Files\Transport Management System`
   - User can choose custom directory
   - Requires admin privileges

2. **Data Directory**
   - Default: `[Installation Directory]\data`
   - User can choose custom location
   - Requires write permissions

3. **Shortcuts**
   - Start Menu shortcuts (always created)
   - Desktop shortcut (optional)
   - Quick Launch shortcut (optional, Windows 7 only)

4. **Components**
   - Main application (required)
   - Documentation (required)
   - Sample data (optional)

### Installation Process

The installer will:

1. Display license agreement
2. Show installation information
3. Select installation directory
4. Select data directory
5. Choose additional options
6. Install files
7. Create shortcuts
8. Set up permissions
9. Offer to launch application

### Uninstallation

The uninstaller will:

1. Ask if user wants to keep data
2. Remove application files
3. Remove shortcuts
4. Optionally remove data directory
5. Clean up registry entries

## Customization

### Changing Application Information

Edit `installer_setup.iss`:

```iss
#define MyAppName "Your App Name"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppURL "https://yourwebsite.com"
```

### Adding Application Icon

1. Create or obtain a 256x256 icon file
2. Save as `resources/icon.ico`
3. The installer script will automatically use it

### Changing Installation Directory

Edit the `DefaultDirName` in `installer_setup.iss`:

```iss
DefaultDirName={autopf}\YourAppName
```

### Adding Custom Pages

You can add custom wizard pages by editing the `[Code]` section in `installer_setup.iss`.

### Modifying File Associations

Add to the `[Registry]` section:

```iss
[Registry]
Root: HKCR; Subkey: ".ext"; ValueType: string; ValueName: ""; ValueData: "YourAppFile"
Root: HKCR; Subkey: "YourAppFile"; ValueType: string; ValueName: ""; ValueData: "Your App File"
Root: HKCR; Subkey: "YourAppFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\YourApp.exe,0"
Root: HKCR; Subkey: "YourAppFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\YourApp.exe"" ""%1"""
```

## Testing the Installer

### Basic Testing

1. **Clean System Test**
   - Test on a system without Python installed
   - Verify all features work correctly
   - Check for missing dependencies

2. **Installation Test**
   - Run the installer
   - Verify all files are copied
   - Check shortcuts are created
   - Verify permissions are correct

3. **Application Test**
   - Launch the application
   - Test core functionality
   - Check database creation
   - Verify log files are created

4. **Uninstallation Test**
   - Run the uninstaller
   - Test both "keep data" and "delete data" options
   - Verify all files are removed
   - Check no orphaned files remain

### Advanced Testing

1. **Different Windows Versions**
   - Windows 10 (various builds)
   - Windows 11
   - Windows Server (if applicable)

2. **Different User Permissions**
   - Administrator account
   - Standard user account
   - Limited user account

3. **Different Installation Scenarios**
   - Fresh installation
   - Upgrade from previous version
   - Reinstallation
   - Custom directory installation

4. **Edge Cases**
   - Installation to non-default drive
   - Installation with special characters in path
   - Installation with limited disk space
   - Installation with antivirus active

## Troubleshooting

### Common Issues

#### 1. Inno Setup Not Found

**Error**: `ISCC.exe not found`

**Solution**: 
- Install Inno Setup from https://jrsoftware.org/isinfo.php
- Verify installation path in `build_installer.py`
- Add Inno Setup to PATH environment variable

#### 2. Build Directory Not Found

**Error**: `dist/TransportManagementSystem not found`

**Solution**:
- Run `python build.py` first
- Verify PyInstaller build completed successfully
- Check for build errors in console output

#### 3. Missing Files

**Error**: `Required file not found`

**Solution**:
- Verify all files listed in "Required Files" section exist
- Check file paths in `installer_setup.iss`
- Ensure files are not in .gitignore

#### 4. Compilation Errors

**Error**: Various Inno Setup compilation errors

**Solution**:
- Check syntax in `installer_setup.iss`
- Verify all file paths are correct
- Review Inno Setup error messages
- Check Inno Setup documentation

#### 5. Installer Doesn't Run

**Error**: Installer fails to launch or crashes

**Solution**:
- Check Windows compatibility
- Run as administrator
- Disable antivirus temporarily
- Check Windows Event Viewer for errors

#### 6. Application Doesn't Launch After Install

**Error**: Application fails to start after installation

**Solution**:
- Check if all DLLs are included
- Verify data directory permissions
- Check logs/transportapp.log for errors
- Test on clean system without Python

## Advanced Configuration

### Code Signing

To sign the installer (recommended for distribution):

1. Obtain a code signing certificate
2. Add to `installer_setup.iss`:

```iss
[Setup]
SignTool=signtool
SignedUninstaller=yes
```

3. Configure signtool in Inno Setup:
   - Tools > Configure Sign Tools
   - Add: `signtool=path\to\signtool.exe sign /f "cert.pfx" /p "password" /t http://timestamp.server.com $f`

### Multi-Language Support

The installer already includes English and Vietnamese:

```iss
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"
```

To add more languages:

```iss
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
```

### Silent Installation

Users can install silently:

```bash
TransportManagementSystem_Setup_v1.0.0.exe /SILENT
```

Or very silent (no progress):

```bash
TransportManagementSystem_Setup_v1.0.0.exe /VERYSILENT
```

With custom directory:

```bash
TransportManagementSystem_Setup_v1.0.0.exe /SILENT /DIR="C:\CustomPath"
```

## Distribution

### Preparing for Distribution

1. **Test Thoroughly**
   - Test on multiple systems
   - Verify all features work
   - Check for any errors

2. **Create Checksums**
   ```bash
   certutil -hashfile TransportManagementSystem_Setup_v1.0.0.exe SHA256
   ```

3. **Create Release Notes**
   - Document new features
   - List bug fixes
   - Include known issues

4. **Prepare Documentation**
   - User manual
   - Quick start guide
   - FAQ

### Distribution Channels

- **Direct Download**: Host on your website
- **GitHub Releases**: Upload to GitHub releases
- **Software Repositories**: Submit to software directories
- **Enterprise Distribution**: Use internal distribution system

## Maintenance

### Updating the Installer

When releasing a new version:

1. Update version number in `installer_setup.iss`
2. Update `MyAppVersion` constant
3. Rebuild the application with `build.py`
4. Rebuild the installer with `build_installer.py`
5. Test the upgrade process

### Upgrade Installations

The installer handles upgrades automatically:
- Detects existing installation
- Preserves user data
- Updates application files
- Maintains user settings

## Checklist

Before releasing the installer:

- [ ] Application built successfully
- [ ] All required files present
- [ ] Icon file included
- [ ] License agreement reviewed
- [ ] Installation information updated
- [ ] Version number correct
- [ ] Installer compiles without errors
- [ ] Tested on clean system
- [ ] All features work after installation
- [ ] Uninstaller works correctly
- [ ] Documentation included
- [ ] Release notes prepared

## Next Steps

After creating the installer:

1. **Final Testing** (Task 18.3)
   - Comprehensive manual testing
   - Test on different Windows versions
   - Performance optimization

2. **Release Preparation** (Task 18.4)
   - Create release notes
   - Prepare documentation package
   - Setup backup/restore utilities

## References

- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [Inno Setup Examples](https://jrsoftware.org/ishelp/index.php?topic=examples)
- [Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)

## Support

For installer issues:
1. Check Inno Setup compiler output
2. Review error messages carefully
3. Test on clean system
4. Check Inno Setup documentation
5. Review Windows Event Viewer

---

© 2024 Transport Management. All rights reserved.
