#!/usr/bin/env python3
"""
Fixed build script for Klondike Archiver - No Unicode issues
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if needed"""
    print("Checking PyInstaller...")
    
    try:
        import PyInstaller
        print("[OK] PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            print("[OK] PyInstaller installed")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install PyInstaller")
            return False

def build_exe():
    """Build the executable"""
    print("\nBuilding KCrinkle.exe...")
    
    # Check if required files exist
    if not Path('KCrinkle.py').exists():
        print("[ERROR] KCrinkle.py not found!")
        return False
    
    if not Path('klondike_icon.ico').exists():
        print("[ERROR] klondike_icon.ico not found!")
        return False
    
    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single executable
        '--windowed',                   # No console window
        '--name=KCrinkle',             # Output name
        '--icon=klondike_icon.ico',    # App icon
        '--distpath=dist',             # Output folder
        'KCrinkle.py'                  # Main file
    ]
    
    try:
        print("Running PyInstaller...")
        result = subprocess.run(cmd, check=True)
        print("[OK] Executable created: dist/KCrinkle.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False

def create_inno_script():
    """Create Inno Setup script for professional installer"""
    print("\nCreating Inno Setup installer script...")
    
    # Get current directory for paths
    current_dir = Path.cwd().resolve()
    
    inno_script = '''[Setup]
AppId={{1B2F5C8D-9E3A-4B7C-8F1D-6A5E9B2C4D7F}
AppName=Klondike Archiver
AppVersion=1.0.0
AppVerName=Klondike Archiver 1.0.0
AppPublisher=Klondike Corporation
DefaultDirName={autopf}\Klondike Archiver
DefaultGroupName=Klondike Archiver
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
OutputDir=dist
OutputBaseFilename=KlondikeArchiverSetup
SetupIconFile=klondike_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\KCrinkle.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "fileassoc"; Description: "Associate .kc files with Klondike Archiver"; GroupDescription: "File Associations"; Flags: checkedonce

[Files]
Source: "dist\KCrinkle.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "klondike_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "kc_file_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"
Name: "{group}\{cm:UninstallProgram,Klondike Archiver}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"; Tasks: quicklaunchicon

[Registry]
; File association for .kc files
Root: HKCR; Subkey: ".kc"; ValueType: string; ValueName: ""; ValueData: "KlondikeArchive"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive"; ValueType: string; ValueName: ""; ValueData: "Klondike Crinkle Archive"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\kc_file_icon.ico"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell"; ValueType: string; ValueName: ""; ValueData: "open"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\open"; ValueType: string; ValueName: ""; ValueData: "&Open with Klondike Archiver"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc

; Context menu for .kc files
Root: HKCR; Subkey: "KlondikeArchive\shell\uncrinkle"; ValueType: string; ValueName: ""; ValueData: "Uncrinkle with KC"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\uncrinkle\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc

; Add to "Open with" menu
Root: HKCR; Subkey: "Applications\KCrinkle.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc
Root: HKCR; Subkey: "Applications\KCrinkle.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Klondike Archiver"; Tasks: fileassoc

[Run]
Filename: "{app}\KCrinkle.exe"; Description: "{cm:LaunchProgram,Klondike Archiver}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*.log"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Refresh shell to update file associations
    if IsTaskSelected('fileassoc') then
    begin
      RegWriteStringValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.kc', 'Progid', 'KlondikeArchive');
    end;
  end;
end;

// Custom messages
[CustomMessages]
LaunchProgram=Launch %1
'''
    
    with open('KlondikeSetup.iss', 'w') as f:
        f.write(inno_script)
    
    print("[OK] Created KlondikeSetup.iss")
    return True

def create_batch_installer():
    """Create batch file to build installer"""
    print("Creating installer build script...")

    # Inno Setup batch
    inno_batch = '''@echo off
title Building Klondike Archiver Installer
echo.
echo Building Klondike Archiver with Inno Setup...
echo.

REM Check if Inno Setup is installed
set INNO_PATH=""
if exist "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" set INNO_PATH="C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
if exist "C:\\Program Files\\Inno Setup 6\\ISCC.exe" set INNO_PATH="C:\\Program Files\\Inno Setup 6\\ISCC.exe"
if exist "C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe" set INNO_PATH="C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe"
if exist "C:\\Program Files\\Inno Setup 5\\ISCC.exe" set INNO_PATH="C:\\Program Files\\Inno Setup 5\\ISCC.exe"

if %INNO_PATH%=="" (
    echo [ERROR] Inno Setup not found!
    echo Download from: https://jrsoftware.org/isinfo.php
    echo Install and try again.
    pause
    exit /b 1
)

echo [OK] Found Inno Setup: %INNO_PATH%
echo Building installer...

%INNO_PATH% KlondikeSetup.iss

if errorlevel 1 (
    echo [ERROR] Failed to build installer
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Installer created!
echo Location: installer_output\\KlondikeArchiverSetup.exe
echo.
pause
'''

    with open('build_inno_installer.bat', 'w') as f:
        f.write(inno_batch)

    print("[OK] Created build_inno_installer.bat")

def main():
    """Main build process"""
    print("KLONDIKE ARCHIVER BUILDER")
    print("=" * 40)
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Build executable
    if not build_exe():
        return False
    
    # Create installer scripts
    create_inno_script()
    create_batch_installer()
    
    print("\n" + "=" * 40)
    print("[SUCCESS] BUILD COMPLETE!")
    print("\nFILES CREATED:")
    print("   dist/KCrinkle.exe - Your application")
    print("   KlondikeSetup.iss - Inno Setup script")
    print("   build_inno_installer.bat - Build Inno installer")
    
    print("\nNEXT STEPS:")
    print("1. Test: Run dist/KCrinkle.exe")
    print("2. For Inno Setup installer:")
    print("   - Download Inno Setup from https://jrsoftware.org/isinfo.php")
    print("   - Run build_inno_installer.bat")
    
    return True

if __name__ == "__main__":
    try:
        main()
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to continue...")