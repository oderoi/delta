# delta

# delta

# For Ubuntu

## 1: Install System Dependencies

'''bash

    sudo apt update && sudo apt install -y python3 python3-venv curl

## 2: Install Ollama

'''bash 

    curl -fsSL https://ollama.ai/install.sh | sh

## #: Download Delta

'''bash

    mkdir -p ~/delta-cli && cd ~/delta-cli
    wget https://gist.githubusercontent.com/yourusername/.../raw/delta.py -O delta.py
    chmod +x delta.py

## 4: Run Setup

'''bash

   python delta.py setup

## %: Verify installation

'''bash

    delta list

## 6: Pull a Model

'''bash

    delta pull mistra

# 7: Run Delta

'''bash

    delta run mistral --wiki

## 8: See Some help and other ifnormation

 '''bash
 
    delta -h


# For macos (intel & Apple Silicon)

# 1: Install System Dependencies

'''bash

    # Install Homebrew (package manager)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Install core dependencies
    brew install python3 ollama

# 2: Install image Processing Dependendies

'''bash

    brew install libjpeg webp little-cms2i

# 3: Clone & Setup Delta

'''bash

    git clone https://github.com/oderoi/delta.git
    cd delta

    # Create virtual environment
    python3 -m venv delta_env
    source delta_env/bin/activate

    # Install requirements
    pip install -r requirements.txt

## 4: Start Ollama Service

'''bash
    
