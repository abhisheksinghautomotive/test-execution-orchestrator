"""Comprehensive CLI tests."""

from typer.testing import CliRunner
from orchestrator.cli import app
from unittest.mock import patch

runner = CliRunner()


def test_version_command():
    """Test version command output."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.3.0" in result.stdout


def test_serve_command():
    """Test serve command invokes uvicorn."""
    # Mock uvicorn at the module where it's imported
    with patch("uvicorn.run") as mock_run:
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_serve_command_help():
    """Test serve command help text."""
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "Start the API server" in result.stdout
