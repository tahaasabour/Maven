import time, uuid
from jinja2 import Template
from utils import extract_json
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def render_prompt(template_path: str, **vars) -> str:
    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read()).render(**vars)

MODEL_PRICES = {  # USD per 1K tokens (example; adjust)
    "gpt-4o-mini": {"in": 0.00015, "out": 0.0006}
}

def call_llm(payload: dict) -> dict:
    t0 = time.time()
    tpl = f"{os.path.dirname(__file__)}/prompts/persona_{payload['persona'].split('_')[0]}.j2"
    prompt = render_prompt(tpl,
        role=payload.get("persona", "writer").replace("_", " "),
        style=payload.get("persona", "writer"),
        tone="balanced",
        audience=payload.get("audience", "general"),
        input_text=payload["input_text"],
        context=payload.get("context", []),
        length=payload.get("length", 120),
    )
    resp = client.chat.completions.create(
        model=payload.get("model", "gpt-4o-mini"),
        messages=[{"role":"user","content":prompt}],
        temperature=0.2
    )
    txt = resp.choices[0].message.content
    elapsed = int((time.time()-t0)*1000)
    usage = getattr(resp, "usage", None)
    tokens = {"prompt": getattr(usage,"prompt_tokens",0), "completion": getattr(usage,"completion_tokens",0)}
    m = payload.get("model","gpt-4o-mini")
    price = MODEL_PRICES.get(m, {"in":0,"out":0})
    cost = (tokens["prompt"]*price["in"] + tokens["completion"]*price["out"]) / 1000.0
    data = extract_json(txt)
    data["tokens"] = tokens
    data["latency_ms"] = elapsed
    data["cost_est"] = round(cost, 6)
    data["request_id"] = str(uuid.uuid4())
    return data