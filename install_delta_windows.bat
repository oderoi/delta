
@echo off
REM Delta CLI - Complete Windows Installation & Usage
REM This is the ONLY Windows installation file you need!

echo ============================================================
echo Delta CLI - Complete Windows Installation
echo ============================================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo OK: Python is installed
python --version

REM Run the complete installation
echo.
echo Running complete installation...
python WINDOWS_COMPLETE_INSTALL.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo SUCCESS: Windows installation completed!
echo.
echo Delta CLI is ready to use on Windows!
echo.
echo Quick start:
echo   python -m delta.cli list
echo   python -m delta.cli pull qwen2:0.5b
echo   python -m delta.cli run qwen2:0.5b
echo.
pause