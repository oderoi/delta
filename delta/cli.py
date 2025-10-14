import click
import sys
import os
import threading
import time
from pathlib import Path
from .models import pull_model, list_models, remove_model, DEFAULT_MODEL
from .chat import run_chat
from .delta import setup_delta
from .llama_cpp_wrapper import LlamaCppWrapper, GPUBackend, QuantizationType, quick_generate, quick_chat, start_chat_server
from .installer import DeltaInstaller
import platform
import psutil
from tabulate import tabulate
import json
import requests
from . import __version__

@click.group()
def cli():
    """Delta CLI - A lightweight, privacy-focused CLI for running local LLMs using llama.cpp"""
    pass

@cli.command()
def setup():
    """Set up Delta environment (downloads llama.cpp binary, creates config)."""
    installer = DeltaInstaller()
    installer.install()

@cli.command()
@click.argument('model', required=False)
@click.option('--wiki', is_flag=True, help='Search Wikipedia first')
@click.option('--ddg', is_flag=True, help='Search DuckDuckGo first')
@click.option('--docs', type=click.Path(exists=True), help='Local doc path to summarize/search')
def run(model, wiki, ddg, docs):
    """Run chat with MODEL (downloads if needed)."""
    if not model:
        model = DEFAULT_MODEL
    model_path, chat_format = pull_model(model, quiet=True)
    flags = [arg for arg in [wiki and '--wiki', ddg and '--ddg', docs and f"--docs {docs}"] if arg]
    run_chat(model_path, chat_format, flags)

@cli.command()
@click.argument('model')
def pull(model):
    """Download MODEL from Hugging Face."""
    model_path, _ = pull_model(model)
    print(f"Model downloaded to {model_path}")

@cli.command()
@click.option('--installed', '-i', 'only_installed', is_flag=True, help='Show only installed models')
@click.option('--available', '-a', 'only_available', is_flag=True, help='Show only available models')
def list(only_installed: bool, only_available: bool):
    """List installed and/or available models."""
    models = list_models()

    # If no filters provided, show both
    show_installed = only_installed or not (only_installed or only_available)
    show_available = only_available or not (only_installed or only_available)

    if show_installed:
        print("\nInstalled Models:")
        if models['installed']:
            table = [[
                m['name'],
                m['size'],
                m['modified_at']
            ] for m in models['installed']]
            print(tabulate(table, headers=['Model Name', 'Size', 'Modified At'], tablefmt='grid'))
        else:
            print("No models installed.")

    if show_available:
        print("\nAvailable Models (use 'delta pull <name>'):")
        table = [[m['name'], m['size']] for m in models['available']]
        print(tabulate(table, headers=['Model Name', 'Size'], tablefmt='grid'))

@cli.command()
@click.argument('model')
def remove(model):
    """Remove MODEL."""
    remove_model(model)

@cli.command()
def check():
    """Check system specs."""
    ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    cpu = platform.processor()
    print(f"CPU: {cpu}\nRAM: {ram_gb:.1f} GB")
    rec = "7B models" if ram_gb >= 8 else "1-3B models" if ram_gb >= 4 else "0.5B models"
    print(f"Recommended: {rec}")

@cli.command()
@click.option('--limit', '-l', type=int, default=5, help='Number of recent sessions to show')
@click.option('--session', '-s', help='Show specific session by ID')
@click.option('--all', 'show_all', is_flag=True, help='Show all available history')
def hist(limit, session, show_all):
    """View chat history."""
    from .chat import load_history
    history = load_history()
    
    if not history:
        print("No chat history found.")
        return
    
    if show_all:
        # Show all sessions with requested format
        for sess in history:
            print(f"Session: {sess['id']} ({sess['timestamp']})")
            if not sess['messages']:
                print("user: ")
                print("delta(response): ")
            else:
                for msg in sess['messages']:
                    user_text = msg.get('user', '') or ''
                    assistant_text = msg.get('assistant', '') or ''
                    print(f"user: {user_text}")
                    print(f"delta(response): {assistant_text}")
            print("-" * 50)
        return
    
    if session:
        # Show specific session
        found = False
        for sess in history:
            if sess['id'].startswith(session):
                print(f"Session {sess['id'][:10]} ({sess['timestamp']}):")
                print("=" * 50)
                for msg in sess['messages']:
                    if msg.get('user'):
                        print(f"User: {msg['user']}")
                    if msg.get('assistant'):
                        print(f"Assistant: {msg['assistant']}")
                    print("-" * 30)
                found = True
                break
        if not found:
            print(f"Session {session} not found.")
    else:
        # Show recent sessions
        print(f"Recent {min(limit, len(history))} chat sessions:")
        print("=" * 50)
        for sess in history[-limit:]:
            print(f"Session {sess['id'][:10]} ({sess['timestamp']}):")
            if not sess['messages']:
                print("  (No conversation recorded)")
            else:
                for msg in sess['messages'][-3:]:  # Show last 3 messages per session
                    if msg.get('user'):
                        print(f"  User: {msg['user']}")
                    if msg.get('assistant'):
                        print(f"  Assistant: {msg['assistant']}")
                    print("  " + "-" * 40)
            print("-" * 50)

@cli.command()
@click.option('--clear', is_flag=True, help='Clear history')
@click.option('--session', '-s', help='Clear specific session by ID')
def hist_clear(clear, session):
    """Clear chat history."""
    from .chat import load_history, save_history, HISTORY_FILE
    import json
    
    if clear and session:
        # Clear specific session
        history = load_history()
        original_count = len(history)
        history = [sess for sess in history if not sess['id'].startswith(session)]
        if len(history) < original_count:
            with HISTORY_FILE.open('w') as f:
                json.dump(history, f, indent=2)
            print(f"Session {session} cleared.")
        else:
            print(f"Session {session} not found.")
    elif clear:
        # Clear all history
        HISTORY_FILE.unlink(missing_ok=True)
        print("All chat history cleared.")
    else:
        print("Use --clear to clear all history or --clear --session <id> to clear specific session.")

@cli.command()
def version():
    """Show version."""
    print(f"Delta v{__version__}")

# Enhanced commands with full llama.cpp capabilities

@cli.command()
@click.argument('model')
@click.argument('prompt')
@click.option('--temperature', type=float, default=0.7, help='Sampling temperature')
@click.option('--top-p', type=float, default=0.9, help='Top-p sampling')
@click.option('--top-k', type=int, default=40, help='Top-k sampling')
@click.option('--max-tokens', type=int, default=512, help='Maximum tokens to generate')
@click.option('--threads', type=int, help='Number of threads to use')
@click.option('--gpu-layers', type=int, default=0, help='Number of layers to offload to GPU')
@click.option('--gpu-backend', type=click.Choice(['cpu', 'cuda', 'rocm', 'metal', 'opencl']), default='cpu', help='GPU backend to use')
@click.option('--stream', is_flag=True, default=True, help='Stream output as it generates')
def generate(model, prompt, temperature, top_p, top_k, max_tokens, threads, gpu_layers, gpu_backend, stream):
    """Generate text from a prompt using the specified model."""
    try:
        model_path, chat_format = pull_model(model)
        wrapper = LlamaCppWrapper()
        
        kwargs = {
            'temperature': temperature,
            'top_p': top_p,
            'top_k': top_k,
            'max_tokens': max_tokens,
            'threads': threads,
            'gpu_layers': gpu_layers,
            'gpu_backend': GPUBackend(gpu_backend),
            'stream': stream,
            'allow_stdin_exit': True
        }
        
        if stream:
            # Start stdin watcher to allow 'exit'/'quit'/'q' to terminate immediately
            stop_event = threading.Event()
            def _stdin_watch():
                try:
                    while not stop_event.is_set():
                        line = sys.stdin.readline()
                        if not line:
                            break
                        if line.strip().lower() in {"exit", "quit", "q"}:
                            os._exit(0)
                except Exception:
                    pass
            watcher = threading.Thread(target=_stdin_watch, daemon=True)
            watcher.start()
            try:
                for chunk in wrapper.generate_stream(model_path, prompt, **kwargs):
                    print(chunk, end='', flush=True)
                print()
            finally:
                stop_event.set()
        else:
            result = wrapper.generate(model_path, prompt, **kwargs)
            print(result)
            
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
@click.argument('model')
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', type=int, default=8080, help='Server port')
@click.option('--threads', type=int, help='Number of threads to use')
@click.option('--gpu-layers', type=int, default=0, help='Number of layers to offload to GPU')
def server(model, host, port, threads, gpu_layers):
    """Start a chat server with the specified model."""
    try:
        model_path, chat_format = pull_model(model)
        
        kwargs = {
            'threads': threads,
            'gpu_layers': gpu_layers
        }
        
        print(f"Starting server with model: {model}")
        print(f"Server will be available at: http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        success = start_chat_server(model_path, host, port, **kwargs)
        if success:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping server...")
        else:
            print("Failed to start server")
            
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
@click.argument('model')
@click.argument('text')
@click.option('--threads', type=int, help='Number of threads to use')
def embeddings(model, text, threads):
    """Get embeddings for text using the specified model."""
    try:
        model_path, chat_format = pull_model(model)
        wrapper = LlamaCppWrapper()
        
        kwargs = {'threads': threads} if threads else {}
        embeddings = wrapper.get_embeddings(model_path, text, **kwargs)
        
        print(f"Generated {len(embeddings)} dimensional embeddings:")
        print(f"First 10 values: {embeddings[:10]}")
        print(f"Embedding norm: {sum(x**2 for x in embeddings)**0.5:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
@click.argument('model')
@click.option('--threads', type=int, help='Number of threads to use')
def benchmark(model, threads):
    """Benchmark model performance."""
    try:
        model_path, chat_format = pull_model(model)
        wrapper = LlamaCppWrapper()
        
        kwargs = {'threads': threads} if threads else {}
        results = wrapper.benchmark(model_path, **kwargs)
        
        print(f"Benchmark results for {model}:")
        for key, value in results.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
@click.argument('model')
@click.option('--threads', type=int, help='Number of threads to use')
def info(model, threads):
    """Get detailed information about a model."""
    try:
        # Check if model is installed first
        installed_models = list_models()['installed']
        model_found = False
        for installed_model in installed_models:
            if installed_model['name'] == model:
                model_found = True
                break
        
        if not model_found:
            print(f"Model {model} not found.")
            print("Available models:")
            for installed_model in installed_models:
                print(f"  - {installed_model['name']}")
            return
        
        # Try to get model info without loading the full model
        try:
            model_path, chat_format = pull_model(model)
            wrapper = LlamaCppWrapper()
            
            # Get basic file info without running llama.cpp
            try:
                file_size = Path(model_path).stat().st_size
                file_name = Path(model_path).stem
            except OSError:
                file_size = 0
                file_name = model
            
            print(f"Model Information for {model}:")
            print(f"  Name: {file_name}")
            print(f"  Path: {model_path}")
            print(f"  Size: {file_size / (1024**3):.2f} GB")
            print(f"  Format: GGUF")
            print(f"  Quantization: Unknown")
            print(f"  Parameters: Unknown")
            print(f"  Family: Unknown")
            print(f"  Chat Format: {chat_format}")
            print(f"  Context Size: 2048")
            
        except Exception as e:
            print(f"Error getting model info: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
@click.argument('input_model')
@click.argument('output_model')
@click.option('--quantization', type=click.Choice([q.value for q in QuantizationType]), default='Q4_K_M', help='Quantization type')
def quantize(input_model, output_model, quantization):
    """Quantize a model to reduce size."""
    try:
        input_path, _ = pull_model(input_model)
        output_path = Path(input_path).parent / f"{output_model}.gguf"
        
        wrapper = LlamaCppWrapper()
        success = wrapper.quantize_model(input_path, str(output_path), QuantizationType(quantization))
        
        if success:
            print(f"Model quantized successfully: {output_path}")
            print(f"Original size: {Path(input_path).stat().st_size / (1024**3):.2f} GB")
            print(f"Quantized size: {output_path.stat().st_size / (1024**3):.2f} GB")
        else:
            print("Quantization failed")
            
    except Exception as e:
        print(f"Error: {e}")

@cli.command()
def doctor():
    """Diagnose system and installation issues."""
    print("Delta Doctor - System Diagnostics")
    print("=" * 40)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python Version: {python_version}")
    if sys.version_info < (3, 8):
        print("  WARNING: Python 3.8+ recommended")
    else:
        print("  OK: Python version OK")
    
    # Check system info
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Check GPU support
    try:
        wrapper = LlamaCppWrapper()
        print("  OK: llama.cpp binary found")
    except FileNotFoundError:
        print("  ERROR: llama.cpp binary not found - run 'delta setup'")
    
    # Check models
    models = list_models()
    print(f"Installed Models: {len(models['installed'])}")
    for model in models['installed']:
        print(f"  - {model['name']} ({model['size']})")
    
    # Check dependencies
    required_packages = ['requests', 'click', 'tabulate', 'huggingface_hub']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  OK: {package}")
        except ImportError:
            print(f"  ERROR: {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages: pip install {' '.join(missing_packages)}")
    
    print("\nDiagnosis complete!")

@cli.command()
@click.argument('model')
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8080, type=int, help='Port to bind to')
@click.option('--threads', type=int, help='Number of threads to use')
def server(model, host, port, threads):
    """Start a chat server with the specified model."""
    try:
        model_path, chat_format = pull_model(model)
        print(f"Starting server with model: {model}")
        print(f"Server will be available at: http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Start the server
        start_chat_server(model_path, host, port, threads=threads)
        
    except Exception as e:
        print(f"Failed to start server: {e}")

def main():
    """Main entry point for the delta CLI"""
    try:
        # Use standalone_mode=False so exceptions propagate and show useful errors
        cli(standalone_mode=False)
    except SystemExit as e:
        # Preserve Click's exit codes
        raise
    except Exception as e:
        # Fallback diagnostic
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    cli()