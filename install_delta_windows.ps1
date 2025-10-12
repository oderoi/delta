# Delta CLI Windows PowerShell Installation Script
# This script installs Delta CLI on Windows using PowerShell

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Delta CLI - Windows PowerShell Installation Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
Write-Host ""
Write-Host "🔍 Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip is available" -ForegroundColor Green
    } else {
        throw "pip not found"
    }
} catch {
    Write-Host "❌ pip is not available!" -ForegroundColor Red
    Write-Host "Please reinstall Python with pip included." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for conflicting packages
Write-Host ""
Write-Host "🔍 Checking for conflicting packages..." -ForegroundColor Yellow
try {
    $installedPackages = python -m pip list 2>&1
    if ($installedPackages -match "delta-0.4.2") {
        Write-Host "⚠️  Found conflicting package: delta-0.4.2" -ForegroundColor Yellow
        Write-Host "Uninstalling conflicting package..." -ForegroundColor Yellow
        python -m pip uninstall delta-0.4.2 -y
    }
} catch {
    Write-Host "⚠️  Could not check for conflicting packages" -ForegroundColor Yellow
}

# Install Delta
Write-Host ""
Write-Host "📦 Installing Delta CLI..." -ForegroundColor Yellow
try {
    python -m pip install delta
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta installed successfully!" -ForegroundColor Green
    } else {
        throw "Installation failed"
    }
} catch {
    Write-Host "❌ Failed to install Delta!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running as Administrator or use:" -ForegroundColor Yellow
    Write-Host "python -m pip install --user delta" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Test Delta command
Write-Host ""
Write-Host "🧪 Testing Delta installation..." -ForegroundColor Yellow
try {
    $deltaVersion = python -m delta.cli --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta Python module works!" -ForegroundColor Green
        Write-Host "Use: python -m delta.cli [command]" -ForegroundColor Cyan
    } else {
        throw "Delta not working"
    }
} catch {
    Write-Host "⚠️  Delta command not found, but Python module should work" -ForegroundColor Yellow
}

# Setup Delta
Write-Host ""
Write-Host "🔧 Setting up Delta environment..." -ForegroundColor Yellow
try {
    python -m delta.cli setup
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta setup completed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Delta setup failed, but you can try manually:" -ForegroundColor Yellow
        Write-Host "python -m delta.cli setup" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Delta setup failed" -ForegroundColor Yellow
}

# Test basic functionality
Write-Host ""
Write-Host "🧪 Testing basic functionality..." -ForegroundColor Yellow
try {
    python -m delta.cli list
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta list command works!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Delta list command failed, but installation may still work" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not test Delta functionality" -ForegroundColor Yellow
}

# Print usage guide
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Usage Guide:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Download a model:" -ForegroundColor White
Write-Host "   python -m delta.cli pull qwen2:0.5b" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start chatting:" -ForegroundColor White
Write-Host "   python -m delta.cli run qwen2:0.5b" -ForegroundColor Gray
Write-Host ""
Write-Host "3. List available models:" -ForegroundColor White
Write-Host "   python -m delta.cli list" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Get help:" -ForegroundColor White
Write-Host "   python -m delta.cli --help" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 For more information, see:" -ForegroundColor Cyan
Write-Host "   - README.md" -ForegroundColor Gray
Write-Host "   - WINDOWS_INSTALLATION_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "🆘 If you have issues:" -ForegroundColor Cyan
Write-Host "   - Check WINDOWS_INSTALLATION_GUIDE.md for troubleshooting" -ForegroundColor Gray
Write-Host "   - Run: python -m delta.cli doctor" -ForegroundColor Gray
Write-Host "   - Report issues on GitHub" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
