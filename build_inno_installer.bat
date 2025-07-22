@echo off
title Building Klondike Archiver Installer
echo.
echo Building Klondike Archiver with Inno Setup...
echo.

REM Check if Inno Setup is installed
set INNO_PATH=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set INNO_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if exist "C:\Program Files\Inno Setup 5\ISCC.exe" set INNO_PATH="C:\Program Files\Inno Setup 5\ISCC.exe"

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
echo Location: installer_output\KlondikeArchiverSetup.exe
echo.
pause
