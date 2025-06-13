#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Function to add to PATH if not already present
add_to_path() {
    local path_to_add="$1"
    local shell_rc=""
    
    # Determine which shell RC file to use
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
    fi
    
    if [ -n "$shell_rc" ]; then
        if ! grep -q "export PATH=\"$path_to_add:\$PATH\"" "$shell_rc"; then
            echo "export PATH=\"$path_to_add:\$PATH\"" >> "$shell_rc"
            echo -e "${GREEN}Added $path_to_add to PATH in $shell_rc${NC}"
        fi
    fi
}

# Function to check if Ollama is running
check_ollama_running() {
    if ! curl -s http://localhost:11434/api/tags >/dev/null; then
        echo -e "${YELLOW}Ollama server is not running. Starting it...${NC}"
        if command_exists systemctl; then
            sudo systemctl start ollama
            sleep 5  # Wait for Ollama to start
        else
            ollama serve &
            sleep 5  # Wait for Ollama to start
        fi
    fi
}

echo -e "${GREEN}Starting Delta installation...${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Detect package manager
if command_exists apt-get; then
    PKG_MANAGER="apt"
elif command_exists dnf; then
    PKG_MANAGER="dnf"
elif command_exists yum; then
    PKG_MANAGER="yum"
elif command_exists pacman; then
    PKG_MANAGER="pacman"
else
    handle_error "No supported package manager found"
fi

echo -e "${GREEN}Detected package manager: $PKG_MANAGER${NC}"

# Install system dependencies
echo -e "${GREEN}Installing system dependencies...${NC}"
case $PKG_MANAGER in
    "apt")
        sudo apt-get update || handle_error "Failed to update package lists"
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev git libjpeg-dev zlib1g-dev || handle_error "Failed to install dependencies"
        ;;
    "dnf")
        sudo dnf install -y python3 python3-pip python3-virtualenv python3-devel git libjpeg-devel zlib-devel || handle_error "Failed to install dependencies"
        ;;
    "yum")
        sudo yum install -y python3 python3-pip python3-virtualenv python3-devel git libjpeg-devel zlib-devel || handle_error "Failed to install dependencies"
        ;;
    "pacman")
        sudo pacman -Sy --noconfirm python python-pip python-virtualenv git libjpeg-turbo zlib || handle_error "Failed to install dependencies"
        ;;
esac

# Check if Python virtual environment is available
if ! python3 -c "import venv" 2>/dev/null; then
    echo -e "${GREEN}Installing Python virtual environment package...${NC}"
    case $PKG_MANAGER in
        "apt")
            sudo apt-get install -y python3-venv || handle_error "Failed to install Python virtual environment"
            ;;
        "dnf")
            sudo dnf install -y python3-virtualenv || handle_error "Failed to install Python virtual environment"
            ;;
        "yum")
            sudo yum install -y python3-virtualenv || handle_error "Failed to install Python virtual environment"
            ;;
        "pacman")
            sudo pacman -S --noconfirm python-virtualenv || handle_error "Failed to install Python virtual environment"
            ;;
    esac
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo -e "${GREEN}Installing pip...${NC}"
    case $PKG_MANAGER in
        "apt")
            sudo apt-get install -y python3-pip || handle_error "Failed to install pip"
            ;;
        "dnf")
            sudo dnf install -y python3-pip || handle_error "Failed to install pip"
            ;;
        "yum")
            sudo yum install -y python3-pip || handle_error "Failed to install pip"
            ;;
        "pacman")
            sudo pacman -S --noconfirm python-pip || handle_error "Failed to install pip"
            ;;
    esac
fi

# Check if Ollama is installed
if ! command_exists ollama; then
    echo -e "${GREEN}Installing Ollama...${NC}"
    # Download and run the official Ollama install script
    curl -fsSL https://ollama.com/install.sh | sh || handle_error "Failed to install Ollama"
    
    # Verify installation
    if ! command_exists ollama; then
        handle_error "Ollama installation completed but 'ollama' command not found. Please try restarting your terminal."
    fi
    
    # Start Ollama service
    if command_exists systemctl; then
        sudo systemctl enable ollama
        sudo systemctl start ollama
    else
        ollama serve &
    fi
    sleep 5  # Wait for Ollama to start
    
    # Verify Ollama is running
    if ! curl -s http://localhost:11434/api/tags >/dev/null; then
        handle_error "Ollama service failed to start. Please check the logs and try again."
    fi
else
    echo -e "${GREEN}Ollama is already installed${NC}"
    check_ollama_running
fi

# Create installation directory
INSTALL_DIR="$HOME/.delta"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Installation directory already exists. Backing up...${NC}"
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$INSTALL_DIR" || handle_error "Failed to create installation directory"

# Clone repository
echo -e "${GREEN}Cloning Delta repository...${NC}"
git clone https://github.com/oderoi/delta.git "$INSTALL_DIR" || handle_error "Failed to clone repository"

# Check if requirements.txt exists
if [ ! -f "$INSTALL_DIR/requirements.txt" ]; then
    handle_error "requirements.txt not found in the repository"
fi

# Create virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
cd "$INSTALL_DIR" || handle_error "Failed to change to installation directory"
python3 -m venv delta_env || handle_error "Failed to create virtual environment"
source delta_env/bin/activate || handle_error "Failed to activate virtual environment"

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
python3 -m pip install --upgrade pip || handle_error "Failed to upgrade pip"
python3 -m pip install -r requirements.txt || handle_error "Failed to install Python dependencies"

# Run setup
echo -e "${GREEN}Running Delta setup...${NC}"
python3 delta.py setup || handle_error "Failed to run setup"

# Download default model
echo -e "${GREEN}Downloading default model (deepseek-r1:1.5b)...${NC}"
ollama pull deepseek-r1:1.5b || handle_error "Failed to download model"

# Create executable wrapper script
echo -e "${GREEN}Creating executable wrapper...${NC}"
cat > "$INSTALL_DIR/delta" << 'EOF'
#!/bin/bash
source "$HOME/.delta/delta_env/bin/activate"
python "$HOME/.delta/delta.py" "$@"
EOF

chmod +x "$INSTALL_DIR/delta" || handle_error "Failed to make delta executable"

# Try to create symlink in /usr/local/bin
echo -e "${GREEN}Setting up system-wide access...${NC}"
if [ -w /usr/local/bin ]; then
    sudo ln -sf "$INSTALL_DIR/delta" /usr/local/bin/delta || handle_error "Failed to create symlink"
    echo -e "${GREEN}Successfully created system-wide symlink${NC}"
else
    echo -e "${YELLOW}Could not create system-wide symlink. Adding to user PATH instead...${NC}"
    add_to_path "$INSTALL_DIR"
    echo -e "${YELLOW}Please run the following command to create the symlink:${NC}"
    echo -e "sudo ln -sf \"$INSTALL_DIR/delta\" /usr/local/bin/delta"
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "By default, Delta comes with the deepseek-r1:1.5b model pre-installed."
echo -e "You can now use Delta by typing 'delta' in your terminal."
echo -e "${YELLOW}Note: If you just added Delta to your PATH, please restart your terminal or run:${NC}"
echo -e "source ~/.zshrc  # for zsh"
echo -e "source ~/.bashrc  # for bash" 