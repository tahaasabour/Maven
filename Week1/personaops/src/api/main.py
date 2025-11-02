from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
import logging
import sys
from .models import GenRequest, GenResponse
from .llm import call_llm
from .moderation import pre_redact_pii, post_moderate

# Initialize logging: place logs under the package `src/logs` so it's
# relative to the package and consistent when the app is started from repo root.
LOG_PATH = Path(__file__).parent.parent / "logs" / "runs.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PersonaOps")

# Configure module logger to emit to terminal (stdout). This keeps logs
# visible when running uvicorn in development or directly with Python.
logger = logging.getLogger("personaops.api")
if not logger.handlers:
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.post("/generate", response_model=GenResponse)
def generate(req: GenRequest):
    """Generate content based on input and persona."""
    # Clean input
    clean = pre_redact_pii(req.input_text)
    payload = req.model_dump()
    payload["input_text"] = clean
    
    try:
        # Generate content
        data = call_llm(payload)
        
        # Apply moderation
        data = post_moderate(data)
        
        # Log request
        LOG_PATH.open("a", encoding="utf-8").write(json.dumps({
            "provider": req.provider,
            "model": req.model,
            "latency_ms": data["latency_ms"],
            "tokens": data["tokens"],
            "cost_est": data["cost_est"],
            "req": data["request_id"]
        }) + "\n")
        
        return GenResponse(**data)
        
    except Exception as e:
        # Log full traceback and error details to terminal for easier debugging
        logger.exception("Error generating content for request: %s", getattr(req, 'input_text', '<no-input>'))
        raise HTTPException(500, f"provider_error: {str(e)}")