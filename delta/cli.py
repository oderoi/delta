import click
import sys
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
    model_path, chat_format = pull_model(model)
    flags = [arg for arg in [wiki and '--wiki', ddg and '--ddg', docs and f"--docs {docs}"] if arg]
    run_chat(model_path, chat_format, flags)

@cli.command()
@click.argument('model')
def pull(model):
    """Download MODEL from Hugging Face."""
    model_path, _ = pull_model(model)
    print(f"Model downloaded to {model_path}")

@cli.command()
def list():
    """List installed and available models."""
    models = list_models()
    
    # COMMENTED OUT: Original implementation with detailed formatting
    # print("\n📋 Installed Models:")
    # if models['installed']:
    #     table = [[
    #         m['name'],
    #         m['size'],
    #         m['modified_at'],
    #         # m['format'],
    #         # m['family'],
    #         # m['parameters'],
    #         # m['quant']
    #     ] for m in models['installed']]
    #     print(tabulate(table, headers=['Model Name', 'Size', 'Modified At', 'Format', 'Family', 'Parameters', 'Quantization'], tablefmt='grid'))
    # else:
    #     print("No models installed.")

    # print("\n📋 Available Models (use 'delta pull <name>'):")
    # # table = [[m['name'], m['repo_id'], m['quant']] for m in models['available']]
    # # print(tabulate(table, headers=['Name', 'Hugging Face Repository', 'Quantization'], tablefmt='grid'))
    # table = [[m['name'], m['size']] for m in models['available']]
    # print(tabulate(table, headers=['Name', 'Size'], tablefmt='grid'))
    
    # NEW SIMPLIFIED IMPLEMENTATION
    print("\n📋 Installed Models:")
    if models['installed']:
        table = [[
            m['name'],
            m['size'],
            m['modified_at']
        ] for m in models['installed']]
        print(tabulate(table, headers=['Model Name', 'Size', 'Modified At'], tablefmt='grid'))
    else:
        print("No models installed.")

    print("\n📋 Available Models (use 'delta pull <name>'):")
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
def hist():
    """View chat history."""
    from .chat import load_history
    history = load_history()
    for sess in history[-5:]:
        print(f"Session {sess['id'][:10]}:")
        for msg in sess['messages'][-3:]:
            print(f"User: {msg['user'][:50]}...\nAssist: {msg['assistant'][:50]}...\n")

@cli.command()
@click.option('--clear', is_flag=True, help='Clear history')
def hist_clear(clear):
    """Clear chat history."""
    if clear:
        from .chat import HISTORY_FILE
        HISTORY_FILE.unlink(missing_ok=True)
        print("History cleared.")

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
@click.option('--stream', is_flag=True, help='Stream output as it generates')
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
            'chat_format': chat_format
        }
        
        if stream:
            for chunk in wrapper.generate_stream(model_path, prompt, **kwargs):
                print(chunk, end='', flush=True)
            print()  # New line after streaming
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
        
        print(f"🚀 Starting Delta server with model: {model}")
        print(f"📡 Server will be available at: http://{host}:{port}")
        print(f"🏷️  Server alias: delta")
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
        model_path, chat_format = pull_model(model)
        wrapper = LlamaCppWrapper()
        
        kwargs = {'threads': threads} if threads else {}
        info = wrapper.get_model_info(model_path)
        
        print(f"Model Information for {model}:")
        print(f"  Name: {info.name}")
        print(f"  Path: {info.path}")
        print(f"  Size: {info.size / (1024**3):.2f} GB")
        print(f"  Format: {info.format}")
        print(f"  Quantization: {info.quantization}")
        print(f"  Parameters: {info.parameters}")
        print(f"  Family: {info.family}")
        print(f"  Chat Format: {info.chat_format}")
        print(f"  Context Size: {info.context_size}")
        
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
        print("  ⚠️  Warning: Python 3.8+ recommended")
    else:
        print("  ✅ Python version OK")
    
    # Check system info
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Check GPU support
    try:
        wrapper = LlamaCppWrapper()
        print("  ✅ llama.cpp binary found")
    except FileNotFoundError:
        print("  ❌ llama.cpp binary not found - run 'delta setup'")
    
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
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages: pip install {' '.join(missing_packages)}")
    
    print("\nDiagnosis complete!")

def main():
    """Main entry point for the delta CLI"""
    cli()

if __name__ == '__main__':
    cli()