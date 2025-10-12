"""
Delta Installer - Automated installation system for cross-platform support
Handles binary downloads, dependency management, and platform-specific optimizations
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import hashlib

class DeltaInstaller:
    """Handles automated installation of Delta with pre-built binaries"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".delta"
        self.bin_dir = self.home_dir / "bin"
        self.config_file = self.home_dir / "config.json"
        self.platform_info = self._detect_platform()
        
    def _detect_platform(self) -> Dict[str, str]:
        """Detect platform and architecture for binary selection"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map common architectures
        arch_map = {
            'x86_64': 'x64',
            'amd64': 'x64', 
            'aarch64': 'arm64',
            'arm64': 'arm64',
            'armv7l': 'armv7'
        }
        
        architecture = arch_map.get(machine, machine)
        
        # Detect GPU capabilities
        gpu_support = self._detect_gpu_support()
        
        return {
            'system': system,
            'architecture': architecture,
            'machine': machine,
            'gpu_support': gpu_support,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}"
        }
    
    def _detect_gpu_support(self) -> Dict[str, bool]:
        """Detect available GPU acceleration support"""
        gpu_support = {
            'cuda': False,
            'rocm': False,
            'metal': False,
            'opencl': False
        }
        
        try:
            # Check for CUDA
            if shutil.which('nvidia-smi'):
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                gpu_support['cuda'] = result.returncode == 0
        except:
            pass
            
        try:
            # Check for Metal (macOS)
            if platform.system() == 'Darwin':
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True)
                gpu_support['metal'] = 'Metal' in result.stdout
        except:
            pass
            
        try:
            # Check for ROCm (Linux)
            if platform.system() == 'Linux':
                gpu_support['rocm'] = shutil.which('rocm-smi') is not None
        except:
            pass
            
        return gpu_support
    
    def _get_binary_url(self) -> str:
        """Get the appropriate binary URL based on platform"""
        # For now, skip binary downloads and go straight to building from source
        # This avoids the 404 errors with incorrect binary URLs
        return None
    
    def _detect_actual_binary_name(self, extracted_path: Path) -> Optional[Path]:
        """Detect the actual binary name in the extracted archive"""
        # Common binary names used by llama.cpp
        possible_names = [
            "llama-cli",      # Most common
            "llama-main", 
            "main", 
            "llama",
            "llama-server",
            "llama-bench",
            "llama-embedding"
        ]
        
        for name in possible_names:
            binary_path = extracted_path / name
            if binary_path.exists() and binary_path.is_file():
                return binary_path
        
        # Look for any executable file
        for item in extracted_path.iterdir():
            if item.is_file() and item.stat().st_mode & 0o111:  # Executable
                return item
        
        return None
    
    def _download_binary(self, url: str, dest_path: Path) -> bool:
        """Download and extract binary from URL"""
        try:
            print(f"Downloading binary from {url}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading: {progress:.1f}%", end='', flush=True)
                
                print()  # New line after progress
            
            # Extract the downloaded file
            tmp_path = Path(tmp_file.name)
            try:
                if tmp_path.suffix == '.zip':
                    with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                        zip_ref.extractall(dest_path)
                elif tmp_path.suffix in ['.tar.gz', '.tgz']:
                    with tarfile.open(tmp_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(dest_path)
                else:
                    # Assume it's a direct binary
                    shutil.copy(tmp_path, dest_path / "llama-main")
                
                # Detect the actual binary name
                actual_binary = self._detect_actual_binary_name(dest_path)
                if actual_binary:
                    # Rename to standard name
                    final_binary = dest_path / "llama-main"
                    if actual_binary != final_binary:
                        shutil.move(str(actual_binary), str(final_binary))
                    
                    # Make binary executable on Unix systems
                    if platform.system() != 'Windows':
                        final_binary.chmod(0o755)
                    
                    return True
                else:
                    print("Could not find executable binary in downloaded archive")
                    return False
                
            except Exception as extract_error:
                print(f"Failed to extract binary: {extract_error}")
                return False
            finally:
                # Clean up
                if tmp_path.exists():
                    tmp_path.unlink()
            
        except requests.exceptions.RequestException as e:
            print(f"Network error downloading binary: {e}")
            return False
        except Exception as e:
            print(f"Failed to download binary: {e}")
            return False
    
    def _build_from_source(self) -> bool:
        """Build llama.cpp from source as fallback"""
        print("Building llama.cpp from source...")
        
        build_dir = self.home_dir / "llama.cpp"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        try:
            # Clone repository
            subprocess.run([
                'git', 'clone', '--depth', '1', 
                'https://github.com/ggerganov/llama.cpp.git',
                str(build_dir)
            ], check=True)
            
            # Create build directory inside the cloned repo
            build_subdir = build_dir / "build"
            build_subdir.mkdir(exist_ok=True)
            
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(build_subdir)
            
            try:
                # Configure build based on platform and GPU support
                cmake_args = ['cmake', '..', '-DCMAKE_BUILD_TYPE=Release']
                
                # For macOS, use CPU-only build to avoid Metal compilation issues
                if platform.system() == 'Darwin':
                    # Use CPU-only build to avoid Metal linking issues
                    cmake_args.extend([
                        '-DGGML_METAL=OFF', 
                        '-DGGML_CUDA=OFF', 
                        '-DGGML_ROCM=OFF',
                        '-DGGML_OPENCL=OFF',
                        '-DGGML_VULKAN=OFF',
                        '-DGGML_LLAMAFILE=OFF'
                    ])
                elif platform.system() == 'Linux' and self.platform_info['gpu_support']['cuda']:
                    cmake_args.extend(['-DGGML_CUDA=ON'])
                elif platform.system() == 'Linux' and self.platform_info['gpu_support']['rocm']:
                    cmake_args.extend(['-DGGML_ROCM=ON'])
                
                subprocess.run(cmake_args, check=True)
                subprocess.run(['make', '-j'], check=True)
                
                # Copy binary - llama.cpp builds 'llama-cli' not 'main'
                binary_source = build_subdir / "llama-cli"
                binary_dest = self.bin_dir / "llama-main"
                
                if not binary_source.exists():
                    # Try alternative binary names
                    possible_names = ["llama-cli", "main", "llama", "llama-server"]
                    for name in possible_names:
                        alt_source = build_subdir / name
                        if alt_source.exists():
                            binary_source = alt_source
                            break
                    else:
                        print(f"❌ No binary found in {build_subdir}")
                        return False
                
                shutil.copy(binary_source, binary_dest)
                
                if platform.system() != 'Windows':
                    binary_dest.chmod(0o755)
                
                return True
                
            finally:
                # Always return to original directory
                os.chdir(original_cwd)
            
        except Exception as e:
            print(f"Failed to build from source: {e}")
            return False
        finally:
            # Clean up build directory
            if build_dir.exists():
                shutil.rmtree(build_dir)
    
    def install_binary(self) -> bool:
        """Install llama.cpp binary with automatic fallback"""
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if binary already exists
        binary_path = self.bin_dir / "llama-main"
        if binary_path.exists():
            print("llama.cpp binary already installed")
            return True
        
        # Try Homebrew installation first (most reliable)
        if self._try_homebrew_installation():
            return True
        
        # Skip binary downloads for now due to URL issues
        # Go straight to building from source
        print("Building llama.cpp from source...")
        return self._build_from_source()
    
    def _try_homebrew_installation(self) -> bool:
        """Try to install llama.cpp via Homebrew (most reliable method)"""
        try:
            print("🔍 Checking for Homebrew installation...")
            
            # Check if Homebrew is available
            result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Homebrew not found")
                return False
            
            print("✅ Homebrew found, installing llama.cpp...")
            
            # Install llama.cpp via Homebrew
            result = subprocess.run(['brew', 'install', 'llama.cpp'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ llama.cpp installed via Homebrew")
                
                # Find the llama-cli binary
                result = subprocess.run(['which', 'llama-cli'], capture_output=True, text=True)
                if result.returncode == 0:
                    llama_cli_path = result.stdout.strip()
                    
                    # Create symlink to expected location
                    binary_dest = self.bin_dir / "llama-main"
                    if not binary_dest.exists():
                        import os
                        os.symlink(llama_cli_path, str(binary_dest))
                        print(f"✅ Created symlink: {binary_dest} -> {llama_cli_path}")
                    
                    return True
                else:
                    print("❌ llama-cli binary not found after Homebrew installation")
                    return False
            else:
                print(f"❌ Homebrew installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Homebrew installation timed out")
            return False
        except Exception as e:
            print(f"❌ Homebrew installation error: {e}")
            return False
    
    def _get_alternative_binary_urls(self) -> List[str]:
        """Get alternative binary URLs to try if the primary fails"""
        system = self.platform_info['system']
        arch = self.platform_info['architecture']
        gpu_support = self.platform_info['gpu_support']
        
        alternatives = []
        
        # Try different naming conventions
        if system == 'darwin':
            if gpu_support['metal']:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-metal.zip",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.zip",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-macos.zip"
                ])
            else:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.zip",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-macos.zip"
                ])
        elif system == 'linux':
            if gpu_support['cuda']:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-cuda.tar.gz",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.tar.gz"
                ])
            elif gpu_support['rocm']:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-rocm.tar.gz",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.tar.gz"
                ])
            else:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.tar.gz"
                ])
        elif system == 'windows':
            if gpu_support['cuda']:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}-cuda.zip",
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.zip"
                ])
            else:
                alternatives.extend([
                    f"https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b{arch}.zip"
                ])
        
        return alternatives
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        try:
            if platform.system() == 'Windows':
                # Use winget or chocolatey
                if shutil.which('winget'):
                    print("Installing Git via winget...")
                    subprocess.run(['winget', 'install', 'Git.Git'], check=True)
                    print("Installing CMake via winget...")
                    subprocess.run(['winget', 'install', 'Kitware.CMake'], check=True)
                elif shutil.which('choco'):
                    print("Installing dependencies via chocolatey...")
                    subprocess.run(['choco', 'install', 'git', 'cmake'], check=True)
                else:
                    print("Please install Git and CMake manually on Windows")
                    return False
            elif platform.system() == 'Darwin':
                # Use Homebrew
                if shutil.which('brew'):
                    print("Installing dependencies via Homebrew...")
                    # Check if already installed to avoid warnings
                    try:
                        subprocess.run(['brew', 'list', 'git'], check=True, capture_output=True)
                        print("Git already installed")
                    except subprocess.CalledProcessError:
                        subprocess.run(['brew', 'install', 'git'], check=True)
                    
                    try:
                        subprocess.run(['brew', 'list', 'cmake'], check=True, capture_output=True)
                        print("CMake already installed")
                    except subprocess.CalledProcessError:
                        subprocess.run(['brew', 'install', 'cmake'], check=True)
                else:
                    print("Please install Homebrew first: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                    return False
            elif platform.system() == 'Linux':
                # Use package manager
                if shutil.which('apt'):
                    print("Installing dependencies via apt...")
                    subprocess.run(['sudo', 'apt', 'update'], check=True)
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'git', 'cmake', 'build-essential'], check=True)
                elif shutil.which('yum'):
                    print("Installing dependencies via yum...")
                    subprocess.run(['sudo', 'yum', 'install', '-y', 'git', 'cmake', 'gcc', 'gcc-c++'], check=True)
                elif shutil.which('dnf'):
                    print("Installing dependencies via dnf...")
                    subprocess.run(['sudo', 'dnf', 'install', '-y', 'git', 'cmake', 'gcc', 'gcc-c++'], check=True)
                elif shutil.which('pacman'):
                    print("Installing dependencies via pacman...")
                    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'git', 'cmake', 'base-devel'], check=True)
                else:
                    print("Please install Git and CMake manually on your Linux distribution")
                    return False
            
            return True
        except Exception as e:
            print(f"Failed to install dependencies: {e}")
            print("Please install Git and CMake manually and try again")
            return False
    
    def setup_environment(self) -> bool:
        """Setup environment variables and PATH"""
        try:
            # Create config
            config = {
                'platform': self.platform_info,
                'binary_path': str(self.bin_dir / "llama-main"),
                'models_dir': str(self.home_dir / "models"),
                'version': '1.0.0'
            }
            
            with self.config_file.open('w') as f:
                json.dump(config, f, indent=2)
            
            # Setup PATH
            self._setup_path()
            
            return True
        except Exception as e:
            print(f"Failed to setup environment: {e}")
            return False
    
    def _setup_path(self):
        """Setup PATH for the binary"""
        bin_path = str(self.bin_dir)
        
        if platform.system() == 'Windows':
            print(f"Add {bin_path} to your PATH environment variable")
            print("You can do this by running:")
            print(f'setx PATH "%PATH%;{bin_path}"')
        else:
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell:
                profile = Path.home() / '.bashrc'
            elif 'zsh' in shell:
                profile = Path.home() / '.zshrc'
            else:
                profile = Path.home() / '.profile'
            
            export_line = f'export PATH="$PATH:{bin_path}"'
            
            if profile.exists():
                content = profile.read_text()
                if bin_path not in content:
                    with profile.open('a') as f:
                        f.write(f'\n# Delta CLI\n{export_line}\n')
                    print(f"Added {bin_path} to {profile}")
            else:
                print(f"Add {export_line} to your shell profile")
    
    def _validate_installation(self) -> bool:
        """Validate that the installation was successful"""
        binary_path = self.bin_dir / "llama-main"
        
        if not binary_path.exists():
            print("❌ Binary not found")
            return False
        
        if not binary_path.is_file():
            print("❌ Binary is not a file")
            return False
        
        # Check if binary is executable
        if platform.system() != 'Windows':
            if not (binary_path.stat().st_mode & 0o111):
                print("❌ Binary is not executable")
                return False
        
        # Try to run the binary to check if it works
        try:
            result = subprocess.run([str(binary_path), '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Binary validation successful")
                return True
            else:
                print(f"❌ Binary execution failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Binary execution timed out")
            return False
        except Exception as e:
            print(f"❌ Binary execution error: {e}")
            return False
    
    def install(self) -> bool:
        """Complete installation process"""
        print("Installing Delta CLI...")
        print(f"Platform: {self.platform_info['system']} {self.platform_info['architecture']}")
        print(f"GPU Support: {self.platform_info['gpu_support']}")
        
        # Install dependencies
        print("\n📦 Installing dependencies...")
        if not self.install_dependencies():
            print("⚠️  Warning: Some dependencies may not be installed")
        
        # Install binary
        print("\n🔧 Installing llama.cpp binary...")
        if not self.install_binary():
            print("❌ Failed to install llama.cpp binary")
            return False
        
        # Validate installation
        print("\n✅ Validating installation...")
        if not self._validate_installation():
            print("❌ Installation validation failed")
            return False
        
        # Setup environment
        print("\n⚙️  Setting up environment...")
        if not self.setup_environment():
            print("❌ Failed to setup environment")
            return False
        
        print("\n🎉 Delta CLI installation completed successfully!")
        print("Run 'delta --help' to get started")
        
        return True

def main():
    """Main installation entry point"""
    installer = DeltaInstaller()
    success = installer.install()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
