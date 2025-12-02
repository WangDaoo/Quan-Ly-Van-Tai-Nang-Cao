; Inno Setup Script for Transport Management System
; Hệ Thống Quản Lý Vận Tải Toàn Diện
;
; Prerequisites:
; 1. Install Inno Setup from https://jrsoftware.org/isinfo.php
; 2. Build the application with PyInstaller first (run build.py)
; 3. Compile this script with Inno Setup Compiler
;
; This will create a Windows installer in the Output/ directory

#define MyAppName "Transport Management System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Transport Management"
#define MyAppURL "https://github.com/yourusername/transport-management"
#define MyAppExeName "TransportManagementSystem.exe"
#define MyAppDescription "Hệ Thống Quản Lý Vận Tải Toàn Diện"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_INFO.txt
OutputDir=Output
OutputBaseFilename=TransportManagementSystem_Setup_v{#MyAppVersion}
SetupIconFile=resources\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable and all files from dist folder
Source: "dist\TransportManagementSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
; README files
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "BUILD_INSTRUCTIONS.md"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Create directories with write permissions for the application
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify
Name: "{app}\backups"; Permissions: users-modify

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\User Manual"; Filename: "{app}\docs\USER_MANUAL.md"
Name: "{group}\Quick Start Guide"; Filename: "{app}\docs\QUICK_START_GUIDE.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up log files and temporary data on uninstall
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\backups"

[Code]
var
  DataDirPage: TInputDirWizardPage;
  KeepDataCheckBox: TNewCheckBox;

procedure InitializeWizard;
begin
  { Create custom page for data directory selection }
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Select Data Directory', 'Where should application data be stored?',
    'Select the folder where the application will store its database and files, then click Next.',
    False, '');
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{app}\data');

  { Add checkbox for keeping data on uninstall }
  KeepDataCheckBox := TNewCheckBox.Create(WizardForm);
  KeepDataCheckBox.Parent := DataDirPage.Surface;
  KeepDataCheckBox.Caption := 'Keep application data when uninstalling';
  KeepDataCheckBox.Checked := True;
  KeepDataCheckBox.Top := DataDirPage.Edits[0].Top + DataDirPage.Edits[0].Height + 20;
  KeepDataCheckBox.Width := DataDirPage.SurfaceWidth;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  { Skip data directory page if doing a silent install }
  Result := (PageID = DataDirPage.ID) and WizardSilent;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    { Create data directory with proper permissions }
    DataDir := DataDirPage.Values[0];
    if not DirExists(DataDir) then
      CreateDir(DataDir);
  end;
end;

function InitializeUninstall(): Boolean;
var
  DataDir: String;
  Response: Integer;
begin
  Result := True;
  
  { Check if user wants to keep data }
  DataDir := ExpandConstant('{app}\data');
  
  if DirExists(DataDir) then
  begin
    Response := MsgBox('Do you want to keep your application data (database and files)?' + #13#10 + 
                       'If you select No, all data will be permanently deleted.' + #13#10#13#10 +
                       'Data location: ' + DataDir,
                       mbConfirmation, MB_YESNO);
    
    if Response = IDYES then
    begin
      { Keep data - don't delete }
      Log('User chose to keep application data');
    end
    else
    begin
      { Delete data }
      Log('User chose to delete application data');
      DelTree(DataDir, True, True, True);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    { Clean up any remaining files }
    Log('Uninstall completed');
  end;
end;

function GetDataDir(Param: String): String;
begin
  { Return the data directory path }
  Result := DataDirPage.Values[0];
end;
