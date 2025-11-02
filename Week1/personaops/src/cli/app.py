import typer
import json
from pathlib import Path
import logging
import requests
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def generate(
    input_file: str = typer.Argument(..., help="Input markdown file path"),
    persona: str = typer.Option("witty_marketer", "--persona", "-p", help="Persona to use for generation"),
    provider: str = typer.Option("openai", "--provider", help="LLM provider to use"),
    length: int = typer.Option(120, "--length", "-l", help="Maximum length of generated content")
):
    """Generate content using the PersonaOps API."""
    try:
        # Read input file
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            raise typer.Exit(1)
            
        # Prepare request
        data = {
            "input_text": input_path.read_text(encoding="utf-8"),
            "persona": persona,
            "audience": "devs",
            "provider": provider,
            "model": "gpt-4o-mini",
            "length": length
        }
        
        # Call API
        logger.info(f"Generating content with {persona} persona...")
        r = requests.post(
            "http://127.0.0.1:8000/generate",
            json=data,
            timeout=60
        )
        r.raise_for_status()
        out = r.json()
        
        # Save output
        out_path = Path("outputs") / f"{out['request_id']}.json"
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        
        # Print summary
        print("\nGeneration Summary:")
        print(f"Title: {out['title']}")
        print(f"Style: {out['style']}")
        print(f"Length: {len(out['body'].split())} words")
        print(f"Cost: ${out['cost_est']:.4f}")
        print(f"Latency: {out['latency_ms']}ms")
        print(f"Output saved to: {out_path}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()