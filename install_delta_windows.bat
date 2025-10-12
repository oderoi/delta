@echo off
REM Delta CLI Windows Installation Script
REM This script installs Delta CLI on Windows

echo ============================================================
echo 🚀 Delta CLI - Windows Installation Script
echo ============================================================
echo.

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Check if pip is available
echo.
echo 🔍 Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not available!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

echo ✅ pip is available

REM Install Delta
echo.
echo 📦 Installing Delta CLI...
python -m pip install delta
if %errorlevel% neq 0 (
    echo ❌ Failed to install Delta!
    echo.
    echo Try running as Administrator or use:
    echo python -m pip install --user delta
    pause
    exit /b 1
)

echo ✅ Delta installed successfully!

REM Test Delta command
echo.
echo 🧪 Testing Delta installation...
python -m delta.cli --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Delta command not found, but Python module should work
    echo You can use: python -m delta.cli [command]
) else (
    echo ✅ Delta command works!
)

REM Setup Delta
echo.
echo 🔧 Setting up Delta environment...
python -m delta.cli setup
if %errorlevel% neq 0 (
    echo ⚠️  Delta setup failed, but you can try manually:
    echo python -m delta.cli setup
)

REM Test basic functionality
echo.
echo 🧪 Testing basic functionality...
python -m delta.cli list
if %errorlevel% neq 0 (
    echo ⚠️  Delta list command failed, but installation may still work
)

REM Print usage guide
echo.
echo ============================================================
echo 🎉 Installation Complete!
echo ============================================================
echo.
echo 📋 Usage Guide:
echo.
echo 1. Download a model:
echo    python -m delta.cli pull qwen2:0.5b
echo.
echo 2. Start chatting:
echo    python -m delta.cli run qwen2:0.5b
echo.
echo 3. List available models:
echo    python -m delta.cli list
echo.
echo 4. Get help:
echo    python -m delta.cli --help
echo.
echo 📚 For more information, see:
echo    - README.md
echo    - WINDOWS_INSTALLATION_GUIDE.md
echo.
echo 🆘 If you have issues:
echo    - Check WINDOWS_INSTALLATION_GUIDE.md for troubleshooting
echo    - Run: python -m delta.cli doctor
echo    - Report issues on GitHub
echo.
pause
