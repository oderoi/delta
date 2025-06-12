# PowerShell script to create Windows executable

# Function to handle errors
function Handle-Error {
    param($Message)
    Write-Host "Error: $Message" -ForegroundColor Red
    exit 1
}

# Function to check if file exists
function Test-FileExists {
    param($FilePath)
    if (-not (Test-Path $FilePath)) {
        Handle-Error "Required file not found: $FilePath"
    }
}

Write-Host "Creating Windows executable..." -ForegroundColor Green

# Check for required files
Write-Host "Checking required files..." -ForegroundColor Green
Test-FileExists "delta.py"
Test-FileExists "requirements.txt"

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Handle-Error "Python is not installed. Please install Python 3.8 or later."
}

# Create virtual environment
Write-Host "Setting up build environment..." -ForegroundColor Green
python -m venv build_env
if (-not $?) {
    Handle-Error "Failed to create virtual environment"
}

# Activate virtual environment
& .\build_env\Scripts\Activate.ps1
if (-not $?) {
    Handle-Error "Failed to activate virtual environment"
}

# Install build dependencies
Write-Host "Installing build dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install pyinstaller
pip install pillow  # For icon conversion
pip install -r requirements.txt

# Convert PNG to ICO if needed
if (Test-Path "delta.png") {
    Write-Host "Converting PNG to ICO format..." -ForegroundColor Green
    $python_script = @'
from PIL import Image
import os

# Open the PNG image
img = Image.open('delta.png')

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Create ICO file with multiple sizes
sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
img.save('delta.ico', sizes=sizes)
'@
    Set-Content -Path "convert_icon.py" -Value $python_script
    python convert_icon.py
    Remove-Item "convert_icon.py"
}

# Build executable
Write-Host "Building executable..." -ForegroundColor Green
$icon_param = if (Test-Path "delta.ico") { "--icon=delta.ico" } else { "" }
pyinstaller --onefile --name delta $icon_param --add-data "delta.py;." --add-data "requirements.txt;." --hidden-import=venv --hidden-import=virtualenv delta.py

# Create distribution package
Write-Host "Creating distribution package..." -ForegroundColor Green
$dist_dir = "dist"
if (-not (Test-Path $dist_dir)) {
    New-Item -ItemType Directory -Force -Path $dist_dir
}

# Copy necessary files to dist directory
Write-Host "Copying files to distribution directory..." -ForegroundColor Green
Copy-Item "requirements.txt" -Destination $dist_dir -Force
Copy-Item "delta.py" -Destination $dist_dir -Force
if (Test-Path "delta.ico") {
    Copy-Item "delta.ico" -Destination $dist_dir -Force
}

# Create zip file
Write-Host "Creating zip package..." -ForegroundColor Green
Compress-Archive -Path "$dist_dir\*" -DestinationPath "delta.zip" -Force

# Cleanup
Write-Host "Cleaning up..." -ForegroundColor Green
Remove-Item -Recurse -Force build_env
Remove-Item -Recurse -Force build
Remove-Item -Force *.spec

Write-Host "Build complete! The executable is available in the dist directory." -ForegroundColor Green
Write-Host "A zip package has been created at delta.zip" -ForegroundColor Green 