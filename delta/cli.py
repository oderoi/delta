import click
from pathlib import Path

from .models import pull_model, list_models, get_model_path
from .inference import interactive_chat
from .search import search_and_ask

@click.group()
def cli():
    """Delta: Run LLMs locally with llama.cpp"""
    pass

@cli.command()
@click.argument("model_name")
@click.option("--repo", required=True, help="HF repo ID")
@click.option("--file", "filename", required=True, help="GGUF filename")
def pull(model_name: str, repo: str, filename: str):
    pull_model(model_name, repo, filename)

@cli.command()
def list():
    models = list_models()
    if not models:
        click.echo("No models. Pull one with 'delta pull'.")
        return
    click.echo("Models:")
    for name, path in models.items():
        click.echo(f"  {name}: {Path(path).relative_to(Path.home())}")

@cli.command()
@click.argument("model_name")
def run(model_name: str):
    model_path = get_model_path(model_name)
    if not model_path or not model_path.exists():
        click.echo(f"Model '{model_name}' not found. Run 'delta pull {model_name}'.")
        return
    interactive_chat(str(model_path))

@cli.command()
@click.argument("model_name")
@click.argument("query")
def search(model_name: str, query: str):
    """Search Wikipedia and ask the model"""
    response = search_and_ask(model_name, query)
    if response:
        click.echo(f"Delta: {response}")

if __name__ == "__main__":
    cli()