@echo off
REM Delta CLI - Simple Windows Installation
REM This is the ONLY working installation method

echo ============================================================
echo 🚀 Delta CLI - Windows Installation
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

REM Clean conflicting packages
echo.
echo 🧹 Cleaning conflicting packages...
python -m pip uninstall delta delta-0.4.2 delta-cli delta-ai -y >nul 2>&1
echo ✅ Cleaned conflicting packages

REM Install dependencies
echo.
echo 📦 Installing dependencies...
python -m pip install requests>=2.31.0 click>=8.1.0 tabulate>=0.9.0 colorama>=0.4.6 huggingface_hub>=0.20.0 tqdm>=4.66.0 psutil>=5.9.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies!
    echo Try running as Administrator
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Install Delta manually
echo.
echo 🚀 Installing Delta CLI...
python final_windows_install.py
if %errorlevel% neq 0 (
    echo ❌ Delta installation failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo ✅ Delta CLI installed

REM Test installation
echo.
echo 🧪 Testing installation...
python -m delta.cli --help >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Delta test failed!
    echo Try running: python -m delta.cli --help
    pause
    exit /b 1
)

echo ✅ Delta installation test passed

REM Print success message
echo.
echo ============================================================
echo 🎉 Installation Complete!
echo ============================================================
echo.
echo 📋 Usage Instructions:
echo.
echo 1. List available models:
echo    python -m delta.cli list
echo.
echo 2. Download a model (requires build tools):
echo    python -m delta.cli pull qwen2:0.5b
echo.
echo 3. Start chatting:
echo    python -m delta.cli run qwen2:0.5b
echo.
echo 4. Get help:
echo    python -m delta.cli --help
echo.
echo 📚 For more information, see WINDOWS_INSTALLATION_GUIDE.md
echo.
echo 🎉 Delta CLI is ready to use on Windows!
echo.
pause