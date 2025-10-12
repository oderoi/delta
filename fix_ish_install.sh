#!/bin/bash
# Quick fix for iSH-shell Delta installation issues

echo "🔧 Quick Fix for iSH-shell Delta Installation"
echo "============================================="

# Install essential development packages
echo "Installing development packages..."
apk add gcc python3-dev musl-dev linux-headers build-base libffi-dev openssl-dev

# Upgrade Python packaging tools
echo "Upgrading Python tools..."
python3 -m pip install --upgrade pip setuptools wheel packaging

# Install core dependencies
echo "Installing core dependencies..."
python3 -m pip install click requests tabulate colorama huggingface_hub tqdm

# Try to install psutil (may fail)
echo "Attempting to install psutil..."
python3 -m pip install psutil || echo "⚠️  psutil failed - continuing without it"

# Install Delta
echo "Installing Delta..."
python3 -m pip uninstall delta -y || true
python3 -m pip install .

# Test installation
echo "Testing installation..."
if python3 -m delta.cli --help > /dev/null 2>&1; then
    echo "✅ Delta is working!"
    echo "Use: python3 -m delta.cli --help"
else
    echo "❌ Still having issues? Try the full installer:"
    echo "python3 install_delta_ish.py"
fi
