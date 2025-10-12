#!/bin/bash
# Delta iSH-Shell Installation Script
# Specifically designed for iPhone iSH-shell environment

set -e

echo "🚀 Delta iSH-Shell Installation Script"
echo "======================================"

# Check if we're in iSH-shell
if [[ -f /etc/alpine-release ]]; then
    echo "📱 Detected iSH-shell (Alpine Linux)"
    ISH_SHELL=true
else
    echo "💻 Detected regular Linux"
    ISH_SHELL=false
fi

# Step 1: Install essential development packages
echo ""
echo "🔧 Step 1: Installing development packages..."
echo "This may take a few minutes..."

# Update package index
apk update

# Install essential packages for Python development
echo "Installing gcc, python3-dev, musl-dev, linux-headers..."
apk add gcc python3-dev musl-dev linux-headers build-base libffi-dev openssl-dev

# Install additional useful packages
echo "Installing additional packages..."
apk add git curl wget

# Step 2: Upgrade Python packaging tools
echo ""
echo "⬆️  Step 2: Upgrading Python packaging tools..."

# Upgrade pip first
python3 -m pip install --upgrade pip

# Upgrade setuptools and wheel
python3 -m pip install --upgrade setuptools wheel packaging

# Step 3: Install core dependencies
echo ""
echo "🔧 Step 3: Installing core dependencies..."

# Install core dependencies one by one
CORE_DEPS=(
    "click>=8.1.0"
    "requests>=2.31.0"
    "tabulate>=0.9.0"
    "colorama>=0.4.6"
    "huggingface_hub>=0.20.0"
    "tqdm>=4.66.0"
)

for dep in "${CORE_DEPS[@]}"; do
    echo "Installing $dep..."
    if ! python3 -m pip install "$dep"; then
        echo "⚠️  Failed to install $dep with version constraint, trying without..."
        dep_name=$(echo "$dep" | cut -d'>' -f1)
        python3 -m pip install "$dep_name" || echo "⚠️  Could not install $dep_name"
    fi
done

# Step 4: Handle psutil (problematic in iSH-shell)
echo ""
echo "🔧 Step 4: Handling psutil..."

echo "Attempting to install psutil..."
if python3 -m pip install psutil; then
    echo "✅ psutil installed successfully"
else
    echo "⚠️  psutil compilation failed, trying binary wheel..."
    if python3 -m pip install --only-binary=psutil psutil; then
        echo "✅ psutil installed from binary wheel"
    else
        echo "⚠️  psutil installation failed - some features will be disabled"
        echo "Creating psutil compatibility layer..."
        
        # Create a minimal psutil replacement
        cat > /tmp/psutil_compat.py << 'EOF'
# Minimal psutil compatibility layer for iSH-shell
import platform
import os

class VirtualMemory:
    def __init__(self):
        self.total = 8 * 1024**3  # Assume 8GB
        self.available = 4 * 1024**3  # Assume 4GB available
        self.used = self.total - self.available
        self.free = self.available

def virtual_memory():
    return VirtualMemory()

def cpu_count():
    return 4  # Assume 4 cores

# Export the same interface as psutil
__all__ = ['virtual_memory', 'cpu_count']
EOF
        
        # Install the compatibility layer
        python3 -m pip install /tmp/psutil_compat.py || echo "⚠️  Could not install psutil compatibility layer"
    fi
fi

# Step 5: Install optional dependencies (skip problematic ones)
echo ""
echo "🔧 Step 5: Installing optional dependencies..."

# Try to install optional dependencies, but don't fail if they don't work
echo "Installing PyPDF2..."
python3 -m pip install PyPDF2 || echo "⚠️  PyPDF2 installation failed"

echo "Skipping duckduckgo-search and wikipedia (problematic in iSH-shell)"

# Step 6: Clean up any existing Delta installation
echo ""
echo "🧹 Step 6: Cleaning up existing Delta installation..."
python3 -m pip uninstall delta -y || true

# Step 7: Install Delta
echo ""
echo "📦 Step 7: Installing Delta..."

# Get the current directory
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

# Step 8: Test the installation
echo ""
echo "🧪 Step 8: Testing installation..."

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

# Step 9: Run Delta setup
echo ""
echo "⚙️  Step 9: Running Delta setup..."
if python3 -m delta.cli setup; then
    echo "✅ Delta setup completed"
else
    echo "⚠️  Delta setup failed, but installation may still work"
fi

echo ""
echo "🎉 iSH-shell installation completed successfully!"
echo ""
echo "You can now use Delta with:"
echo "  python3 -m delta.cli --help"
echo "  python3 -m delta.cli setup"
echo "  python3 -m delta.cli run"
echo ""
echo "For troubleshooting, run:"
echo "  python3 -m delta.cli doctor"
