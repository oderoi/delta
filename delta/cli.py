import click
from .models import pull_model, list_models, remove_model, DEFAULT_MODEL
from .chat import run_chat
from .setup_delta import setup_environment
import platform
import psutil
from tabulate import tabulate
import json
from . import __version__

@click.group()
def cli():
    pass

@cli.command()
def setup():
    """Set up Delta environment (downloads llama.cpp binary, creates config)."""
    setup_environment()

@cli.command()
@click.argument('model', required=False)
@click.option('--wiki', is_flag=True, help='Search Wikipedia first')
@click.option('--ddg', is_flag=True, help='Search DuckDuckGo first')
@click.option('--docs', type=click.Path(exists=True), help='Local doc path to summarize/search')
def run(model, wiki, ddg, docs):
    """Run chat with MODEL (downloads if needed)."""
    if not model:
        model = DEFAULT_MODEL
    model_path = pull_model(model)
    flags = [arg for arg in [wiki and '--wiki', ddg and '--ddg', docs and f"--docs {docs}"] if arg]
    run_chat(model_path, flags)

@cli.command()
@click.argument('model')
def pull(model):
    """Download MODEL from Hugging Face."""
    pull_model(model)

@cli.command()
def list():
    """List installed and available models."""
    models = list_models()
    
    # Display installed models
    print("\n📋 Installed Models:")
    if models['installed']:
        table = [[
            m['name'],
            m['size'],
            m['modified_at'],
            # m['format'],
            # m['family'],
            # m['parameters'],
            # m['quant']
        ] for m in models['installed']]
        print(tabulate(table, headers=['Model Name', 'Size', 'Modified At', 'Format', 'Family', 'Parameters', 'Quantization'], tablefmt='grid'))
    else:
        print("No models installed.")

    # Display available models
    print("\n📋 Available Models (use 'delta pull <name>'):")
    table = [[m['name'], m['repo_id'], m['quant']] for m in models['available']]
    print(tabulate(table, headers=['Name', 'Hugging Face Repository', 'Quantization'], tablefmt='grid'))

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

if __name__ == '__main__':
    cli()