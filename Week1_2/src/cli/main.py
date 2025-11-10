import logging
from pathlib import Path
import sys
import typer
from .commands.generate import generate


log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file_path = log_dir / "logs.json"

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    handlers=[
        logging.FileHandler(log_file_path, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="content-generator",
    help="Generate content using LLM APIs with customizable personas",
    add_completion=False,
)

app.command(name="generate")(generate)


def main():
    """Entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("Operation cancelled by user", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    main()