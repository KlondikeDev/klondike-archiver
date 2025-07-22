@echo off
title Klondike Archiver - Complete Builder
color 0A

echo.
echo  ==========================================
echo    KLONDIKE ARCHIVER - COMPLETE BUILDER
echo  ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Download from: https://python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Check required files
if not exist "KCrinkle.py" (
    echo [ERROR] KCrinkle.py not found!
    echo Make sure you're in the right directory.
    pause
    exit /b 1
)

if not exist "klondike_icon.ico" (
    echo [ERROR] klondike_icon.ico not found!
    echo Make sure the icon file is in this directory.
    pause
    exit /b 1
)

if not exist "kc_file_icon.ico" (
    echo [ERROR] kc_file_icon.ico not found!
    echo Make sure the icon file is in this directory.
    pause
    exit /b 1
)

echo [OK] All required files found
echo.

REM Run the build script
echo Starting build process...
echo.
python build_fixed.py

echo.
echo Build process completed!
echo.

REM Check what was created
if exist "dist\KCrinkle.exe" (
    echo [SUCCESS] Application built: dist\KCrinkle.exe
) else (
    echo [ERROR] Application build failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   INSTALLER OPTIONS
echo ==========================================
echo.
echo Choose your installer option:
echo.
echo 1. Inno Setup (Recommended - Free)
echo 2. Skip installer creation
echo.
set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" goto inno_setup
if "%choice%"=="2" goto skip_installer

:inno_setup
echo.
echo Checking for Inno Setup...
set INNO_PATH=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set INNO_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if exist "C:\Program Files\Inno Setup 5\ISCC.exe" set INNO_PATH="C:\Program Files\Inno Setup 5\ISCC.exe"

if %INNO_PATH%=="" (
    echo [INFO] Inno Setup not found - opening download page...
    start https://jrsoftware.org/isinfo.php
    echo.
    echo After installing Inno Setup, run: build_inno_installer.bat
    goto end
)

echo [OK] Found Inno Setup
echo Building installer...
%INNO_PATH% KlondikeSetup.iss

if errorlevel 1 (
    echo [ERROR] Failed to build installer
) else (
    echo [SUCCESS] Installer created: installer_output\KlondikeArchiverSetup.exe
)
goto end

:skip_installer
echo.
echo Skipping installer creation.
echo You can manually run the batch file later:
echo - build_inno_installer.bat (for Inno Setup)

:end
echo.
echo ==========================================
echo   BUILD SUMMARY
echo ==========================================
echo.
if exist "dist\KCrinkle.exe" echo [OK] Application: dist\KCrinkle.exe
if exist "installer_output\KlondikeArchiverSetup.exe" echo [OK] Inno Installer: installer_output\KlondikeArchiverSetup.exe
echo.
echo Your Klondike Archiver is ready to distribute!
echo.
pause