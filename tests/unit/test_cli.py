"""Tests for CLI."""

from typer.testing import CliRunner

from orchestrator.cli import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "orchestrator version" in result.stdout


def test_serve_command():
    """Test serve command prints help message."""
    # Just test that the command is registered, don't actually start server
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "serve" in result.stdout.lower()
