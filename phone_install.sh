#!/bin/bash
# Delta Phone Installation Script for Android/Linux
# This script handles installation on mobile devices with proper dependency management

set -e

echo "🚀 Delta Phone Installation Script"
echo "=================================="

# Check if we're on a mobile device
if [[ -f /system/build.prop ]] || [[ -n "$ANDROID_ROOT" ]]; then
    echo "📱 Detected Android device"
    MOBILE_DEVICE=true
else
    echo "💻 Detected Linux device"
    MOBILE_DEVICE=false
fi

# Check Python installation
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION found"

# Check pip installation
echo "📦 Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Upgrade pip to latest version
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# Install essential dependencies first
echo "🔧 Installing essential dependencies..."
python3 -m pip install --upgrade setuptools wheel

# Install core dependencies one by one to handle failures gracefully
CORE_DEPS=(
    "click>=8.1.0"
    "requests>=2.31.0"
    "tabulate>=0.9.0"
    "colorama>=0.4.6"
    "huggingface_hub>=0.20.0"
    "tqdm>=4.66.0"
    "psutil>=5.9.0"
)

for dep in "${CORE_DEPS[@]}"; do
    echo "Installing $dep..."
    if ! python3 -m pip install "$dep"; then
        echo "⚠️  Failed to install $dep with version constraint, trying without..."
        dep_name=$(echo "$dep" | cut -d'>' -f1)
        python3 -m pip install "$dep_name" || echo "⚠️  Could not install $dep_name"
    fi
done

# Install optional dependencies
echo "🔧 Installing optional dependencies..."
OPTIONAL_DEPS=(
    "duckduckgo-search>=3.0.0"
    "wikipedia>=1.4.0"
    "PyPDF2>=3.0.0"
)

for dep in "${OPTIONAL_DEPS[@]}"; do
    echo "Installing $dep..."
    python3 -m pip install "$dep" || echo "⚠️  Could not install $dep"
done

# Remove any existing delta installation
echo "🧹 Cleaning up existing Delta installation..."
python3 -m pip uninstall delta -y || true

# Install Delta from current directory
echo "📦 Installing Delta..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try development install first
if python3 -m pip install -e .; then
    echo "✅ Delta installed in development mode"
else
    echo "⚠️  Development install failed, trying regular install..."
    if python3 -m pip install .; then
        echo "✅ Delta installed successfully"
    else
        echo "❌ Failed to install Delta"
        exit 1
    fi
fi

# Verify installation
echo "🔍 Verifying installation..."

# Test click import
if python3 -c "import click; print('✅ Click imported successfully')"; then
    echo "✅ Click dependency verified"
else
    echo "❌ Click import failed"
    exit 1
fi

# Test delta CLI import
if python3 -c "from delta.cli import cli; print('✅ Delta CLI imported successfully')"; then
    echo "✅ Delta CLI import verified"
else
    echo "❌ Delta CLI import failed"
    exit 1
fi

# Test delta command
if python3 -m delta.cli --help > /dev/null 2>&1; then
    echo "✅ Delta CLI command works"
else
    echo "❌ Delta CLI command failed"
    exit 1
fi

# Run delta setup
echo "⚙️  Running Delta setup..."
if python3 -m delta.cli setup; then
    echo "✅ Delta setup completed"
else
    echo "⚠️  Delta setup failed, but installation may still work"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "You can now use Delta with:"
echo "  python3 -m delta.cli --help"
echo "  python3 -m delta.cli setup"
echo "  python3 -m delta.cli run"
echo ""
echo "For troubleshooting, run:"
echo "  python3 -m delta.cli doctor"
