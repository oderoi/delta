"""
Enhanced llama.cpp wrapper with full feature support
Provides comprehensive access to all llama.cpp capabilities
"""

import subprocess
import json
import os
import platform
import threading
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Iterator, Any
from dataclasses import dataclass
from enum import Enum

class GPUBackend(Enum):
    """GPU acceleration backends"""
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    OPENCL = "opencl"

class QuantizationType(Enum):
    """Model quantization types"""
    Q4_0 = "Q4_0"
    Q4_1 = "Q4_1"
    Q4_K_M = "Q4_K_M"
    Q4_K_S = "Q4_K_S"
    Q5_0 = "Q5_0"
    Q5_1 = "Q5_1"
    Q5_K_M = "Q5_K_M"
    Q5_K_S = "Q5_K_S"
    Q6_K = "Q6_K"
    Q8_0 = "Q8_0"
    F16 = "F16"
    F32 = "F32"

@dataclass
class ModelInfo:
    """Model information and metadata"""
    name: str
    path: str
    size: int
    format: str
    quantization: str
    parameters: str
    family: str
    chat_format: str
    context_size: int = 2048
    created_at: str = ""

@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_tokens: int = 512
    stop_sequences: List[str] = None
    seed: int = -1
    threads: int = None
    batch_size: int = 512
    gpu_layers: int = 0
    gpu_backend: GPUBackend = GPUBackend.CPU

class LlamaCppWrapper:
    """Enhanced wrapper for llama.cpp with full feature support"""
    
    def __init__(self, binary_path: str = None):
        self.binary_path = binary_path or self._find_binary()
        self.config = GenerationConfig()
        self._process = None
        self._server_process = None
        
    def _find_binary(self) -> str:
        """Find llama.cpp binary"""
        possible_paths = [
            Path.home() / ".delta" / "bin" / "llama-main",
            Path.home() / ".delta" / "bin" / "llama-main.exe",
            shutil.which("llama-main"),
            shutil.which("llama-cli"),
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return str(path)
        
        raise FileNotFoundError("llama.cpp binary not found")
    
    def _build_command(self, model_path: str, **kwargs) -> List[str]:
        """Build llama.cpp command with all available options"""
        cmd = [self.binary_path, "-m", model_path]
        
        # Basic options
        if kwargs.get('interactive', False):
            cmd.append("-i")
        
        if kwargs.get('chat_format'):
            cmd.extend(["--chat-template", kwargs['chat_format']])
        
        # Generation parameters
        if kwargs.get('temperature'):
            cmd.extend(["--temp", str(kwargs['temperature'])])
        
        if kwargs.get('top_p'):
            cmd.extend(["--top-p", str(kwargs['top_p'])])
        
        if kwargs.get('top_k'):
            cmd.extend(["--top-k", str(kwargs['top_k'])])
        
        if kwargs.get('repeat_penalty'):
            cmd.extend(["--repeat-penalty", str(kwargs['repeat_penalty'])])
        
        if kwargs.get('max_tokens'):
            cmd.extend(["--n-predict", str(kwargs['max_tokens'])])
        
        if kwargs.get('seed') is not None:
            cmd.extend(["--seed", str(kwargs['seed'])])
        
        # Context and memory
        if kwargs.get('context_size'):
            cmd.extend(["--ctx-size", str(kwargs['context_size'])])
        
        if kwargs.get('threads'):
            cmd.extend(["--threads", str(kwargs['threads'])])
        
        if kwargs.get('batch_size'):
            cmd.extend(["--batch-size", str(kwargs['batch_size'])])
        
        # GPU acceleration
        if kwargs.get('gpu_layers'):
            cmd.extend(["--n-gpu-layers", str(kwargs['gpu_layers'])])
        
        if kwargs.get('gpu_backend'):
            backend = kwargs['gpu_backend']
            if backend == GPUBackend.CUDA:
                cmd.append("--cuda")
            elif backend == GPUBackend.ROCM:
                cmd.append("--rocm")
            elif backend == GPUBackend.METAL:
                cmd.append("--metal")
            elif backend == GPUBackend.OPENCL:
                cmd.append("--opencl")
        
        # Advanced options
        if kwargs.get('verbose'):
            cmd.append("--verbose")
        
        if kwargs.get('no_display_prompt'):
            cmd.append("--no-display-prompt")
        
        if kwargs.get('color'):
            cmd.append("--color")
        
        if kwargs.get('instruct'):
            cmd.append("--instruct")
        
        if kwargs.get('multiline'):
            cmd.append("--multiline-input")
        
        # Stop sequences
        if kwargs.get('stop_sequences'):
            for stop in kwargs['stop_sequences']:
                cmd.extend(["--stop", stop])
        
        return cmd
    
    def generate(self, model_path: str, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        # Ensure non-interactive mode for generation
        kwargs['interactive'] = False
        cmd = self._build_command(model_path, **kwargs)
        cmd.extend(["--prompt", prompt])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get('timeout', 300)
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"llama.cpp failed: {result.stderr}")
            
            # Clean up the output to remove conversation formatting
            output = result.stdout.strip()
            
            # Remove conversation markers if present
            lines = output.split('\n')
            cleaned_lines = []
            in_assistant_response = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for conversation markers
                if line == "assistant":
                    in_assistant_response = True
                    continue
                elif line == "user":
                    in_assistant_response = False
                    continue
                elif line.startswith("user") or line.startswith("assistant"):
                    # Handle cases where there might be text after the marker
                    if line.startswith("assistant"):
                        in_assistant_response = True
                        # Extract text after "assistant"
                        remaining = line[9:].strip()
                        if remaining:
                            cleaned_lines.append(remaining)
                    elif line.startswith("user"):
                        in_assistant_response = False
                    continue
                elif in_assistant_response:
                    cleaned_lines.append(line)
            
            # If we found assistant response, return it
            if cleaned_lines:
                return '\n'.join(cleaned_lines)
            
            # If no assistant response found, try to extract from the last part
            # This handles cases where the output format is different
            if "assistant" in output.lower():
                # Find the last occurrence of "assistant" and extract everything after it
                parts = output.split("assistant")
                if len(parts) > 1:
                    last_part = parts[-1].strip()
                    if last_part:
                        return last_part
            
            # Otherwise return the original output
            return output
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Generation timed out")
    
    def generate_stream(self, model_path: str, prompt: str, **kwargs) -> Iterator[str]:
        """Stream text generation"""
        # Ensure non-interactive mode for generation
        kwargs['interactive'] = False
        cmd = self._build_command(model_path, **kwargs)
        cmd.extend(["--prompt", prompt])
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            in_assistant_response = False
            
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for conversation markers
                if line == "assistant":
                    in_assistant_response = True
                    continue
                elif line == "user":
                    in_assistant_response = False
                    continue
                
                # Only yield lines from assistant response
                if in_assistant_response:
                    yield line
            
            process.wait()
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise RuntimeError(f"llama.cpp failed: {stderr}")
                
        except Exception as e:
            if process:
                process.terminate()
            raise e
    
    def chat(self, model_path: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with model using conversation format"""
        # Convert messages to prompt format
        if kwargs.get('chat_format') == 'chatml':
            prompt = self._format_chatml(messages)
        elif kwargs.get('chat_format') == 'llama3':
            prompt = self._format_llama3(messages)
        else:
            prompt = self._format_default(messages)
        
        return self.generate(model_path, prompt, **kwargs)
    
    def _format_chatml(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as ChatML"""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"<|im_start|>{role}\n{content}<|im_end|>")
        return '\n'.join(formatted) + '\n<|im_start|>assistant\n'
    
    def _format_llama3(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as Llama3 format"""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                formatted.append(f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>")
            elif role == 'assistant':
                formatted.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>")
        return '\n'.join(formatted) + '\n<|start_header_id|>assistant<|end_header_id|>\n\n'
    
    def _format_default(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as default format"""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
        return '\n'.join(formatted) + '\nassistant: '
    
    def start_server(self, model_path: str, host: str = "localhost", port: int = 8080, **kwargs) -> bool:
        """Start llama.cpp server"""
        if self._server_process:
            return True
        
        # Use llama-server binary instead of llama-main with --server
        server_binary = self._get_server_binary()
        if not server_binary:
            print("❌ llama-server binary not found!")
            return False
        
        cmd = [server_binary, "-m", model_path, "--host", host, "--port", str(port)]
        
        # Add Delta branding
        cmd.extend(["--alias", "delta"])
        
        # Add server-specific options
        if kwargs.get('threads'):
            cmd.extend(["--threads", str(kwargs['threads'])])
        
        if kwargs.get('gpu_layers'):
            cmd.extend(["--n-gpu-layers", str(kwargs['gpu_layers'])])
        
        try:
            self._server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(2)
            
            if self._server_process.poll() is None:
                print(f"🚀 Delta server started at http://{host}:{port}")
                print(f"📡 Server alias: delta")
                return True
            else:
                stderr = self._server_process.stderr.read().decode()
                raise RuntimeError(f"Failed to start server: {stderr}")
                
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop llama.cpp server"""
        if self._server_process:
            self._server_process.terminate()
            self._server_process.wait()
            self._server_process = None
    
    def _get_server_binary(self) -> str:
        """Find the llama-server binary"""
        import platform
        import os
        from pathlib import Path
        
        # Check if we're using Homebrew installation
        if platform.system() == "Darwin":
            homebrew_server = "/opt/homebrew/bin/llama-server"
            if os.path.exists(homebrew_server):
                return homebrew_server
        
        # Check in the same directory as the main binary
        if self.binary_path:
            binary_dir = Path(self.binary_path).parent
            server_binary = binary_dir / "llama-server"
            if server_binary.exists():
                return str(server_binary)
            
            # Try with .exe extension on Windows
            if platform.system() == "Windows":
                server_binary_exe = binary_dir / "llama-server.exe"
                if server_binary_exe.exists():
                    return str(server_binary_exe)
        
        # Try to find llama-server in PATH
        import shutil
        server_path = shutil.which("llama-server")
        if server_path:
            return server_path
        
        return None
    
    def get_embeddings(self, model_path: str, text: str, **kwargs) -> List[float]:
        """Get embeddings for text"""
        cmd = [self.binary_path, "-m", model_path, "--embeddings", "--prompt", text]
        
        if kwargs.get('threads'):
            cmd.extend(["--threads", str(kwargs['threads'])])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to get embeddings: {result.stderr}")
            
            # Parse embeddings from output
            lines = result.stdout.strip().split('\n')
            embeddings = []
            for line in lines:
                if line.strip() and not line.startswith('['):
                    try:
                        embeddings.append(float(line.strip()))
                    except ValueError:
                        continue
            
            return embeddings
            
        except Exception as e:
            raise RuntimeError(f"Failed to get embeddings: {e}")
    
    def quantize_model(self, input_path: str, output_path: str, quantization: QuantizationType) -> bool:
        """Quantize model to specified format"""
        cmd = [self.binary_path, "-m", input_path, "-o", output_path, "-q", quantization.value]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Quantization failed: {e}")
            return False
    
    def get_model_info(self, model_path: str) -> ModelInfo:
        """Get detailed information about a model"""
        cmd = [self.binary_path, "-m", model_path, "--verbose"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to get model info: {result.stderr}")
            
            # Parse model information from verbose output
            info = {
                'name': Path(model_path).stem,
                'path': model_path,
                'size': Path(model_path).stat().st_size,
                'format': 'GGUF',
                'quantization': 'Unknown',
                'parameters': 'Unknown',
                'family': 'Unknown',
                'chat_format': 'chatml'
            }
            
            # Extract information from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'quantization' in line.lower():
                    info['quantization'] = line.split(':')[-1].strip()
                elif 'parameters' in line.lower():
                    info['parameters'] = line.split(':')[-1].strip()
            
            return ModelInfo(**info)
            
        except Exception as e:
            raise RuntimeError(f"Failed to get model info: {e}")
    
    def benchmark(self, model_path: str, **kwargs) -> Dict[str, Any]:
        """Benchmark model performance"""
        cmd = [self.binary_path, "-m", model_path, "--benchmark"]
        
        if kwargs.get('threads'):
            cmd.extend(["--threads", str(kwargs['threads'])])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Benchmark failed: {result.stderr}")
            
            # Parse benchmark results
            lines = result.stdout.split('\n')
            results = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    results[key.strip()] = value.strip()
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Benchmark failed: {e}")

# Convenience functions for common operations
def quick_generate(model_path: str, prompt: str, **kwargs) -> str:
    """Quick text generation"""
    wrapper = LlamaCppWrapper()
    return wrapper.generate(model_path, prompt, **kwargs)

def quick_chat(model_path: str, message: str, **kwargs) -> str:
    """Quick chat with model"""
    wrapper = LlamaCppWrapper()
    messages = [{"role": "user", "content": message}]
    return wrapper.chat(model_path, messages, **kwargs)

def start_chat_server(model_path: str, host: str = "localhost", port: int = 8080, **kwargs) -> bool:
    """Start chat server"""
    wrapper = LlamaCppWrapper()
    return wrapper.start_server(model_path, host, port, **kwargs)
