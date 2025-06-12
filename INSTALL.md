# Delta Installation Guide

This guide provides instructions for installing Delta on macOS, Linux, and Windows operating systems.

## Prerequisites

Before installing Delta, ensure your system meets the following requirements:

- Python 3.8 or later
- Git
- Sufficient disk space (at least 2GB recommended)
- Internet connection for downloading dependencies

## Installation Methods

### macOS Installation

1. Open Terminal
2. Download the installation script:
   ```bash
   curl -O https://nileagi.com/product/delta/delta-installer-macos.sh
   ```
3. Make the script executable:
   ```bash
   chmod +x delta-installer-macos.sh
   ```
4. Run the installation script:
   ```bash
   ./delta-installer-macos.sh
   ```

The script will:
- Install required dependencies using Homebrew
- Set up Python virtual environment
- Install Delta and its dependencies
- Configure system-wide access

### Linux Installation

1. Open Terminal
2. Download the installation script:
   ```bash
   curl -O https://nileagi.com/product/delta/delta-installer-linux.sh
   ```
3. Make the script executable:
   ```bash
   chmod +x delta-installer-linux.sh
   ```
4. Run the installation script:
   ```bash
   ./delta-installer-linux.sh
   ```

The script supports the following package managers:
- apt (Debian/Ubuntu)
- dnf (Fedora)
- yum (RHEL/CentOS)
- pacman (Arch Linux)

### Windows Installation

1. Open PowerShell as a regular user (not administrator)
2. Download the installation script:
   ```powershell
   Invoke-WebRequest -Uri "https://nileagi.com/product/delta/delta-installer.ps1" -OutFile "delta-installer.ps1"
   ```
3. Set the execution policy (if not already set):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Run the installation script:
   ```powershell
   .\delta-installer.ps1
   ```

## Post-Installation

After installation:

1. Restart your terminal or run:
   - For macOS/Linux:
     ```bash
     source ~/.zshrc  # for zsh
     source ~/.bashrc  # for bash
     ```
   - For Windows:
     ```powershell
     refreshenv
     ```

2. Verify the installation:
   ```bash
   delta --version
   ```

## Default Model

Delta comes with the `deepseek-r1:1.5b` model pre-installed. The model will be downloaded automatically during installation.

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure you're not running the installation script as root/administrator
   - Check file permissions: `chmod +x delta-installer-*.sh`

2. **Python Not Found**
   - Install Python 3.8 or later
   - Ensure Python is added to your system PATH

3. **Git Not Found**
   - Install Git using your system's package manager
   - For Windows, Git will be installed automatically via winget

4. **Ollama Installation Issues**
   - For macOS: Try `brew install ollama`
   - For Linux: Run `curl -fsSL https://ollama.com/install.sh | sh`
   - For Windows: Use winget: `winget install Ollama.Ollama`

### Getting Help

If you encounter any issues:
1. Check the error messages in the terminal
2. Ensure all prerequisites are installed
3. Try running the installation script with verbose output:
   ```bash
   bash -x delta-installer-*.sh
   ```

## Uninstallation

To uninstall Delta:

1. Remove the installation directory:
   ```bash
   rm -rf ~/.delta
   ```

2. Remove the system symlink (if created):
   ```bash
   sudo rm /usr/local/bin/delta
   ```

3. Remove from PATH (if added):
   - Edit your shell's RC file (~/.bashrc, ~/.zshrc, etc.)
   - Remove the line containing `~/.delta`

## Support

For additional support:
- Open an issue on GitHub
- Check the documentation
- Contact the development team

## License

Delta is licensed under the MIT License. See the LICENSE file for details. 