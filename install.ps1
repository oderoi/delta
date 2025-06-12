# PowerShell script for Delta installation

# Function to handle errors
function Handle-Error {
    param($Message)
    Write-Host "Error: $Message" -ForegroundColor Red
    exit 1
}

# Function to check if a command exists
function Test-Command {
    param($Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

# Function to add to PATH
function Add-ToPath {
    param($Path)
    $UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($UserPath -notlike "*$Path*") {
        [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$Path", "User")
        Write-Host "Added $Path to user PATH" -ForegroundColor Green
    }
}

Write-Host "Starting Delta installation..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "Please do not run as administrator" -ForegroundColor Red
    exit 1
}

# Check for Python
if (-not (Test-Command python)) {
    Write-Host "Python not found. Please install Python 3.8 or later from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        exit 1
    }

# Check for Git
if (-not (Test-Command git)) {
    Write-Host "Git not found. Installing Git..." -ForegroundColor Green
    winget install --id Git.Git -e --source winget
    if (-not $?) {
        Handle-Error "Failed to install Git"
    }
}

# Check for Ollama
if (-not (Test-Command ollama)) {
    Write-Host "Ollama not found. Installing Ollama..." -ForegroundColor Green
    winget install --id Ollama.Ollama -e --source winget
    if (-not $?) {
        Handle-Error "Failed to install Ollama"
    }
} else {
    Write-Host "Ollama is already installed" -ForegroundColor Green
}

# Create installation directory
$InstallDir = "$env:USERPROFILE\.delta"
if (Test-Path $InstallDir) {
    Write-Host "Installation directory already exists. Backing up..." -ForegroundColor Yellow
    $BackupDir = "$InstallDir.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Move-Item -Path $InstallDir -Destination $BackupDir
}
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Clone repository
Write-Host "Cloning Delta repository..." -ForegroundColor Green
git clone https://github.com/oderoi/delta.git $InstallDir
if (-not $?) {
    Handle-Error "Failed to clone repository"
}

# Check if requirements.txt exists
if (-not (Test-Path "$InstallDir\requirements.txt")) {
    Handle-Error "requirements.txt not found in the repository"
}

# Create virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Green
Set-Location $InstallDir
python -m venv delta_env
if (-not $?) {
    Handle-Error "Failed to create virtual environment"
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
& "$InstallDir\delta_env\Scripts\Activate.ps1"
if (-not $?) {
    Handle-Error "Failed to activate virtual environment"
}

python -m pip install --upgrade pip
if (-not $?) {
    Handle-Error "Failed to upgrade pip"
}

pip install -r requirements.txt
if (-not $?) {
    Handle-Error "Failed to install Python dependencies"
}

# Run setup
Write-Host "Running Delta setup..." -ForegroundColor Green
python delta.py setup
if (-not $?) {
    Handle-Error "Failed to run setup"
}

# Create PowerShell wrapper script
Write-Host "Creating executable wrapper..." -ForegroundColor Green
$WrapperContent = @"
# PowerShell wrapper for Delta
`$env:VIRTUAL_ENV = "$InstallDir\delta_env"
& "$InstallDir\delta_env\Scripts\python.exe" "$InstallDir\delta.py" `$args
"@

Set-Content -Path "$InstallDir\delta.ps1" -Value $WrapperContent

# Create batch file wrapper for easier command-line usage
$BatchContent = @"
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0delta.ps1" %*
"@

Set-Content -Path "$InstallDir\delta.bat" -Value $BatchContent

# Add to PATH
Write-Host "Setting up system-wide access..." -ForegroundColor Green
Add-ToPath $InstallDir

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "By default, Delta comes with the deepseek-r1:1.5b model pre-installed."
Write-Host "You can now use Delta by typing 'delta' in your terminal." 
Write-Host "Note: You may need to restart your terminal for the PATH changes to take effect." -ForegroundColor Yellow 