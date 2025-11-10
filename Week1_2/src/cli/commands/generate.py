import typer
from pathlib import Path
import requests
import json
import logging




logger = logging.getLogger(__name__)


def generate(
    input_file: str = typer.Argument(..., help="Path to text file containing your prompt"),
    persona: str = typer.Option("witty_marketer", "--persona", "-p", help="Persona for content generation"),
    provider: str = typer.Option("openai", "--provider", help="LLM provider to use"),
    length: int = typer.Option(120, "--length", "-l", help="Maximum length of generated content"),
):
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            typer.echo(f"Error: Input file '{input_file}' does not exist", err=True)
            raise typer.Exit(1)

        if not input_path.is_file():
            logger.error(f"Path is not a file: {input_file}")
            typer.echo(f"Error: '{input_file}' is not a file", err=True)
            raise typer.Exit(1)

        try:
            prompt_text = input_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode file {input_file}: {e}")
            typer.echo(f"Error: Unable to read file (encoding issue)", err=True)
            raise typer.Exit(1)

        data = {
            "input_text": prompt_text,
            "persona": persona,
            "audience": "general",
            "provider": provider,
            "model": "gpt-4o-mini",
            "length": length,
        }

        logger.info(f"Generating content with '{persona}' persona using {provider}...")
        typer.echo(f"Generating content with '{persona}' persona...")

        try:
            res = requests.post("http://127.0.0.1:8000/generate", json=data, timeout=120)
            res.raise_for_status()
        except requests.Timeout:
            logger.error("API request timed out")
            typer.echo("Error: Request timed out (120s)", err=True)
            raise typer.Exit(1)
        except requests.ConnectionError:
            logger.error("Failed to connect to API server")
            typer.echo("Error: Cannot connect to API at http://127.0.0.1:8000", err=True)
            typer.echo("API server maybe not running?", err=True)
            raise typer.Exit(1)
        except requests.HTTPError as e:
            logger.error(f"API returned error: {e}")
            typer.echo(f"API Error: {e}", err=True)
            raise typer.Exit(1)

        try:
            out = res.json()
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from API")
            typer.echo("Error: Invalid response from API", err=True)
            raise typer.Exit(1)

        if "request_id" not in out:
            logger.error("Response missing request_id field")
            typer.echo("Error: Invalid response structure", err=True)
            raise typer.Exit(1)

        out_path = Path(__file__).parent.parent / "outputs" / f"{out['request_id']}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
            typer.echo(f"Error: Unable to save output file", err=True)
            raise typer.Exit(1)

        logger.info(f"Content generated successfully: {out['request_id']}")

        typer.echo(f"Content generated successfully!")
        typer.echo(f"Output saved to: {out_path}")
        typer.echo(f"Request ID: {out['request_id']}")

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)