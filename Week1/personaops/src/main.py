from fastapi import FastAPI, HTTPException
from api.models import GenRequest, GenResponse
from api.llm import call_llm
from api.moderation import pre_redact_pii, post_moderate
import json, pathlib

LOG_PATH = pathlib.Path("logs/runs.jsonl"); LOG_PATH.parent.mkdir(exist_ok=True)

app = FastAPI(title="PersonaOps")

@app.post("/generate", response_model=GenResponse)
def generate(req: GenRequest):
    clean = pre_redact_pii(req.input_text)
    payload = req.model_dump()
    payload["input_text"] = clean
    try:
        data = call_llm(payload)
    except Exception as e:
        raise HTTPException(500, f"provider_error: {e}")
    data = post_moderate(data)
    LOG_PATH.open("a", encoding="utf-8").write(json.dumps({
        "provider": req.provider, "model": req.model, "latency_ms": data["latency_ms"],
        "tokens": data["tokens"], "cost_est": data["cost_est"], "req": data["request_id"]
    }) + "\n")
    return GenResponse(**data)