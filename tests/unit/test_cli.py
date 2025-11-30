"""Tests for CLI."""

from typer.testing import CliRunner

from orchestrator.cli import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "orchestrator version" in result.stdout
