import time
import uuid
import os
from jinja2 import Environment, FileSystemLoader
import json
import re
from pathlib import Path

# Try to initialize OpenAI client if API key is present. If not, we
# will use a local deterministic fallback so the service can run
# without network or keys (useful for tests and local dev).
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    if OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        client = None
except Exception:
    client = None

def extract_json(text: str) -> dict:
    """Extract JSON from model output."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise ValueError("No JSON found in model output")
        return json.loads(m.group(0))

def render_prompt(template_path: str, **vars) -> str:
    """Render a Jinja2 template with variables using a FileSystemLoader.

    This allows templates to use `{% include %}` and `{% extends %}`.
    """
    tpl_path = Path(template_path)
    tpl_dir = str(tpl_path.parent)
    env = Environment(loader=FileSystemLoader(tpl_dir))
    try:
        template = env.get_template(tpl_path.name)
    except Exception as e:
        raise RuntimeError(f"Error loading template '{template_path}': {e}")
    return template.render(**vars)

MODEL_PRICES = {
    "gpt-4o-mini": {"in": 0.00015, "out": 0.0006}
}

def call_llm(payload: dict) -> dict:
    """Call LLM with proper prompt template and tracking."""
    t0 = time.time()
    
    # Get prompt template
    base_path = Path(__file__).parent
    tpl = base_path / f"prompts/persona_{payload['persona'].split('_')[0]}.j2"
    
    # Render prompt
    prompt = render_prompt(
        str(tpl),
        role=payload.get("persona", "writer").replace("_", " "),
        style=payload.get("persona", "writer"),
        tone="balanced",
        audience=payload.get("audience", "general"),
        input_text=payload["input_text"],
        context=payload.get("context", []),
        length=payload.get("length", 120),
    )
    
    # If no client is available (no API key or import failure), produce
    # a deterministic fallback response so the app remains usable offline.
    if client is None:
        elapsed = int((time.time() - t0) * 1000)
        # build a simple structured response
        title = (payload.get("input_text", "")[:60].split('\n')[0]).strip()
        body = payload.get("input_text", "").strip()
        # enforce length budget (words)
        max_words = payload.get("length", 120)
        words = body.split()
        if len(words) > max_words:
            body = " ".join(words[:max_words])

        data = {
            "title": title or "Generated Content",
            "body": body,
            "style": payload.get("persona", "writer"),
            "citations": payload.get("context", []),
        }
        data["tokens"] = {"prompt": 0, "completion": len(data["body"].split())}
        data["latency_ms"] = elapsed
        data["cost_est"] = 0.0
        data["request_id"] = str(uuid.uuid4())
        return data

    # Call API (wrapped to fail cleanly)
    try:
        resp = client.chat.completions.create(
            model=payload.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
    except Exception as e:
        # surface a helpful error to the caller
        raise RuntimeError(f"LLM provider error: {e}")

    # Process response
    txt = getattr(resp.choices[0].message, "content", None) or resp.choices[0].message.content
    elapsed = int((time.time() - t0) * 1000)

    # Calculate usage and cost
    usage = getattr(resp, "usage", None)
    tokens = {
        "prompt": getattr(usage, "prompt_tokens", 0),
        "completion": getattr(usage, "completion_tokens", 0)
    }
    m = payload.get("model", "gpt-4o-mini")
    price = MODEL_PRICES.get(m, {"in": 0, "out": 0})
    cost = (tokens["prompt"] * price["in"] + tokens["completion"] * price["out"]) / 1000.0

    # Format output
    data = extract_json(txt)
    data["tokens"] = tokens
    data["latency_ms"] = elapsed
    data["cost_est"] = round(cost, 6)
    data["request_id"] = str(uuid.uuid4())
    return data