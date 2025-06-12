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
        ollama serve &
        sleep 5  # Wait for Ollama to start
    fi
}

# Function to download and install Ollama on macOS
install_ollama_macos() {
    local temp_dir=$(mktemp -d)
    local ollama_zip="$temp_dir/Ollama-darwin.zip"
    local ollama_app="/Applications/Ollama.app"
    
    echo -e "${GREEN}Downloading Ollama...${NC}"
    curl -L -o "$ollama_zip" https://ollama.com/download/Ollama-darwin.zip || handle_error "Failed to download Ollama"
    
    echo -e "${GREEN}Extracting Ollama...${NC}"
    unzip -q "$ollama_zip" -d "$temp_dir" || handle_error "Failed to extract Ollama"
    
    echo -e "${GREEN}Installing Ollama...${NC}"
    if [ -d "$ollama_app" ]; then
        rm -rf "$ollama_app" || handle_error "Failed to remove existing Ollama installation"
    fi
    mv "$temp_dir/Ollama.app" "/Applications/" || handle_error "Failed to install Ollama"
    
    # Clean up
    rm -rf "$temp_dir"
    
    # Start Ollama
    open -a Ollama || handle_error "Failed to start Ollama"
    sleep 5  # Wait for Ollama to start
    
    # Verify Ollama is running
    if ! curl -s http://localhost:11434/api/tags >/dev/null; then
        echo -e "${YELLOW}Ollama failed to start automatically. Please start it manually from Applications folder.${NC}"
        handle_error "Ollama installation completed but failed to start"
    fi
}

echo -e "${GREEN}Starting Delta installation...${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Check if Homebrew is installed
if ! command_exists brew; then
    echo -e "${GREEN}Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || handle_error "Failed to install Homebrew"
    
    # Add Homebrew to PATH if needed
    if [[ "$SHELL" == *"zsh"* ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ "$SHELL" == *"bash"* ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.bashrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

# Install system dependencies
echo -e "${GREEN}Installing system dependencies...${NC}"
brew update || handle_error "Failed to update Homebrew"
brew install python@3.11 git || handle_error "Failed to install dependencies"

# Check if Python virtual environment is available
if ! python3 -c "import venv" 2>/dev/null; then
    echo -e "${GREEN}Installing Python virtual environment package...${NC}"
    brew install python@3.11 || handle_error "Failed to install Python virtual environment"
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo -e "${GREEN}Installing pip...${NC}"
    brew install python@3.11 || handle_error "Failed to install pip"
fi

# Check if Ollama is installed
if ! command_exists ollama; then
    echo -e "${GREEN}Installing Ollama...${NC}"
    install_ollama_macos
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