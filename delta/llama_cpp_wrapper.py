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
            Path.home() / ".delta" / "bin" / "llama-cli.exe",  # Real binary
            Path.home() / ".delta" / "bin" / "llama-main.exe",  # Fallback
            Path.home() / ".delta" / "bin" / "llama-main",     # Fallback
            shutil.which("llama-cli"),
            shutil.which("llama-main"),
        ]
        
        for path in possible_paths:
            if not path:
                continue
            p = Path(path)
            if p.exists():
                # On Windows, optionally verify PE header; on Unix, just ensure executable
                try:
                    if os.name == 'nt':
                        with open(p, 'rb') as f:
                            if f.read(2) == b'MZ':
                                return str(p)
                        # If not PE, still return if executable (could be shim)
                        if os.access(p, os.X_OK):
                            return str(p)
                    else:
                        if os.access(p, os.X_OK):
                            return str(p)
                except Exception:
                    # If any check fails but file exists, assume it's runnable
                    return str(p)
        
        raise FileNotFoundError("llama.cpp binary not found")
    
    def _build_command(self, model_path: str, **kwargs) -> List[str]:
        """Build llama.cpp command with all available options"""
        cmd = [self.binary_path, "-m", model_path]
        
        # Basic options
        if kwargs.get('interactive', False):
            cmd.append("-i")
        
        if kwargs.get('chat_format'):
            cmd.extend(["--chatml"] if kwargs['chat_format'] == 'chatml' 
                      else [f"--prompt-format={kwargs['chat_format']}"])
        
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
            # Monitor stdin to allow early termination via 'exit'/'quit'/'q'
            allow_stdin_exit = kwargs.get('allow_stdin_exit', True)
            stop_event = threading.Event()
            stdin_thread = None
            if allow_stdin_exit:
                def _monitor_stdin():
                    try:
                        while not stop_event.is_set():
                            line = sys.stdin.readline()
                            if not line:
                                break
                            if line.strip().lower() in {"exit", "quit", "q"}:
                                try:
                                    process.terminate()
                                except Exception:
                                    pass
                                stop_event.set()
                                break
                    except Exception:
                        pass
                stdin_thread = threading.Thread(target=_monitor_stdin, daemon=True)
                stdin_thread.start()
            output_lines = []
            for line in process.stdout:
                if line:
                    output_lines.append(line)
                    if kwargs.get('stream'):
                        print(line, end='', flush=True)
            process.wait(timeout=kwargs.get('timeout', 300))
            stop_event.set()
            if stdin_thread:
                try:
                    stdin_thread.join(timeout=0.2)
                except Exception:
                    pass
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise RuntimeError(f"llama.cpp failed: {stderr}")
            return ''.join(output_lines).strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Generation timed out")
    
    def generate_stream(self, model_path: str, prompt: str, **kwargs) -> Iterator[str]:
        """Stream text generation"""
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
            
            for line in process.stdout:
                if line.strip():
                    yield line.strip()
            
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
        
        # Use the dedicated server binary (platform-aware)
        server_candidates = []
        if os.name == 'nt':
            server_candidates.extend([
                Path(self.binary_path).parent / "llama-server.exe",
                Path(self.binary_path).parent / "server.exe",
                shutil.which("llama-server"),
                shutil.which("server"),
            ])
        else:
            server_candidates.extend([
                Path(self.binary_path).parent / "llama-server",
                Path(self.binary_path).parent / "server",
                shutil.which("llama-server"),
                shutil.which("server"),
            ])

        server_binary = None
        for cand in server_candidates:
            if not cand:
                continue
            p = Path(cand)
            if p.exists() and os.access(p, os.X_OK):
                server_binary = str(p)
                break

        if not server_binary:
            print("llama-server not found. Please run 'delta setup' or install via Homebrew: 'brew install llama.cpp'.")
            return False
        
        cmd = [server_binary, "-m", model_path, "--host", host, "--port", str(port)]
        
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
                print(f"Server started at http://{host}:{port}")
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
        # Use a simpler command that doesn't load the full model
        cmd = [self.binary_path, "-m", model_path, "--help"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # If help doesn't work, try with --verbose but with shorter timeout
            if result.returncode != 0:
                cmd = [self.binary_path, "-m", model_path, "--verbose"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to get model info: {result.stderr}")
            
            # Get basic file information
            try:
                file_size = Path(model_path).stat().st_size
            except OSError:
                file_size = 0
            
            # Parse model information from output
            info = {
                'name': Path(model_path).stem,
                'path': model_path,
                'size': file_size,
                'format': 'GGUF',
                'quantization': 'Unknown',
                'parameters': 'Unknown',
                'family': 'Unknown',
                'chat_format': 'chatml',
                'context_size': 2048
            }
            
            # Extract information from output
            lines = result.stdout.split('\n')
            for line in lines:
                line_lower = line.lower()
                if 'quantization' in line_lower or 'quantize' in line_lower:
                    if ':' in line:
                        info['quantization'] = line.split(':')[-1].strip()
                elif 'parameters' in line_lower or 'params' in line_lower:
                    if ':' in line:
                        info['parameters'] = line.split(':')[-1].strip()
                elif 'context' in line_lower and 'length' in line_lower:
                    if ':' in line:
                        try:
                            ctx_size = int(line.split(':')[-1].strip())
                            info['context_size'] = ctx_size
                        except ValueError:
                            pass
                elif 'architecture' in line_lower:
                    if ':' in line:
                        arch = line.split(':')[-1].strip()
                        if 'llama' in arch.lower():
                            info['family'] = 'Llama'
                        elif 'qwen' in arch.lower():
                            info['family'] = 'Qwen'
                        elif 'gemma' in arch.lower():
                            info['family'] = 'Gemma'
                        elif 'phi' in arch.lower():
                            info['family'] = 'Phi'
                        elif 'mistral' in arch.lower():
                            info['family'] = 'Mistral'
                        else:
                            info['family'] = arch
            
            return ModelInfo(**info)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Model info request timed out")
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
