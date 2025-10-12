# Delta CLI - Simple Windows Installation (PowerShell)
# This is the ONLY working installation method

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Delta CLI - Windows Installation" -ForegroundColor Cyan
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

# Clean conflicting packages
Write-Host ""
Write-Host "🧹 Cleaning conflicting packages..." -ForegroundColor Yellow
try {
    python -m pip uninstall delta delta-0.4.2 delta-cli delta-ai -y 2>$null
    Write-Host "✅ Cleaned conflicting packages" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not clean all packages" -ForegroundColor Yellow
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
$dependencies = @(
    "requests>=2.31.0",
    "click>=8.1.0",
    "tabulate>=0.9.0",
    "colorama>=0.4.6",
    "huggingface_hub>=0.20.0",
    "tqdm>=4.66.0",
    "psutil>=5.9.0"
)

foreach ($dep in $dependencies) {
    try {
        Write-Host "   Installing $dep..." -ForegroundColor Gray
        python -m pip install $dep 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $dep" -ForegroundColor Green
        } else {
            Write-Host "❌ $dep" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Failed to install $dep" -ForegroundColor Red
    }
}

# Install Delta manually
Write-Host ""
Write-Host "🚀 Installing Delta CLI..." -ForegroundColor Yellow
try {
    python final_windows_install.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta CLI installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Delta installation failed!" -ForegroundColor Red
        Write-Host "Please check the error messages above" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Delta installation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Test installation
Write-Host ""
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
try {
    python -m delta.cli --help 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Delta installation test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Delta test failed!" -ForegroundColor Red
        Write-Host "Try running: python -m delta.cli --help" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Delta test failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Print success message
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Usage Instructions:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. List available models:" -ForegroundColor White
Write-Host "   python -m delta.cli list" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Download a model (requires build tools):" -ForegroundColor White
Write-Host "   python -m delta.cli pull qwen2:0.5b" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start chatting:" -ForegroundColor White
Write-Host "   python -m delta.cli run qwen2:0.5b" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Get help:" -ForegroundColor White
Write-Host "   python -m delta.cli --help" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 For more information, see WINDOWS_INSTALLATION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Delta CLI is ready to use on Windows!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"