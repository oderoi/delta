import pytest
from click.testing import CliRunner
from delta.cli import cli

def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    assert "Delta v1.0.0" in result.output

def test_list():
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "No models installed" in result.output or "Name" in result.output

def test_setup():
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    assert result.exit_code == 0
    assert "Setting up Delta CLI environment" in result.output