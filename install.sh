#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Delta installation...${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Check for required commands
for cmd in python3 curl git; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is not installed${NC}"
        exit 1
    fi
done

# Create installation directory
INSTALL_DIR="$HOME/.delta"
mkdir -p "$INSTALL_DIR"

# Clone repository
echo -e "${GREEN}Cloning Delta repository...${NC}"
git clone https://github.com/oderoi/delta.git "$INSTALL_DIR"

# Create virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
cd "$INSTALL_DIR"
python3 -m venv delta_env
source delta_env/bin/activate

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo -e "${GREEN}Installing Ollama...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Run setup
echo -e "${GREEN}Running Delta setup...${NC}"
python delta.py setup

# Download default model
echo -e "${GREEN}Downloading default model (deepseek-r1:1.5b)...${NC}"
ollama pull deepseek-r1:1.5b

# Create symlink to delta command
echo -e "${GREEN}Creating system symlink...${NC}"
sudo ln -sf "$INSTALL_DIR/delta.py" /usr/local/bin/delta

echo -e "${GREEN}Installation complete!${NC}"
echo -e "By default, Delta comes with the deepseek-r1:1.5b model pre-installed."
echo -e "You can now use Delta by typing 'delta' in your terminal." 