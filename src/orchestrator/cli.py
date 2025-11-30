"""CLI entrypoint using Typer."""

import typer

app = typer.Typer(help="Test Execution Orchestrator CLI")


@app.command()
def version():
    """Show version."""
    from orchestrator import __version__

    typer.echo(f"orchestrator version {__version__}")


@app.command()
def serve():
    """Start the API server."""
    import uvicorn
    from orchestrator.main import app as fastapi_app

    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    app()
