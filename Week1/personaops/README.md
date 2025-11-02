# PersonaOps

PersonaOps is a content-generation microservice + CLI that uses prompt templates to produce persona-controlled, structured JSON responses.

## Project layout (important files)

```
personaops/
├── src/                   # Python package code (importable as `src`)
│   ├── api/               # FastAPI app and LLM integration
│   │   ├── prompts/       # Jinja2 templates (base.j2, persona_*.j2)
│   │   ├── llm.py
│   │   ├── main.py        # FastAPI app (uvicorn entrypoint)
│   │   └── models.py      # Pydantic request/response models
│   ├── cli/               # Typer-based CLI
│   │   └── app.py         # `python -m src.cli.app` entrypoint
│   └── eval/              # Evaluation tests and goldens
├── .env                   # (optional) environment variables (OPENAI_API_KEY)
├── requirements.txt       # Python dependencies
├── pyproject.toml
├── test_input.md          # Example input used in this README
└── README.md
```

## Quick start (Windows / PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies in editable mode:

```powershell
pip install -e .
```

3. Provide your OpenAI API key. You can either set the environment variable for the current PowerShell session:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

or create a `.env` file in the project root with:

```
OPENAI_API_KEY=sk-...
```

Note: the app currently reads environment variables from the process environment. If you prefer automatic `.env` loading, see the Notes section below.

4. Start the API server (from the project root so `src` is importable):

```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```

5. In a second PowerShell, run the CLI to generate content from `test_input.md`:

```powershell
python -m src.cli.app "test_input.md" --persona witty_marketer --provider openai
```

If the server is not running, the CLI will attempt to POST to `http://127.0.0.1:8000/generate` and will fail.

## Example input (`test_input.md`)

The file `test_input.md` in this repository contains the following text (used in examples above):

```markdown
We are excited to announce our new AI-powered code completion tool that helps developers write better code faster. It uses machine learning to understand context and provide relevant suggestions in real-time.
```

## Example generated output (CLI)

When you run the CLI with the `witty_marketer` persona, the service returns a structured JSON response. An example (formatted) output looks like this:

```json
{
  "title": "AI-Powered Code Completion — Ship Faster, Code Smarter",
  "body": "We built an AI-powered code completion tool that helps developers write better code, faster. By understanding the context of your file, it suggests relevant snippets, reduces boilerplate, and speeds up common workflows. Integrates with your editor and learns from your code patterns to keep suggestions useful and on-target.",
  "style": "witty_marketer",
  "citations": [],
  "moderation_flags": [],
  "tokens": { "prompt": 45, "completion": 78 },
  "latency_ms": 420,
  "cost_est": 0.01234,
  "request_id": "00000000-0000-0000-0000-000000000000"
}
```

Notes:
- The real output will vary depending on the model/provider you choose and your `OPENAI_API_KEY`.
- If no OpenAI key is available, the server falls back to a deterministic local response (it will echo/truncate the input to meet the requested length).

## API: `/generate` (request shape)

POST `/generate` expects a JSON body matching `GenRequest`:

```json
{
  "input_text": "string",
  "persona": "witty_marketer",
  "audience": "devs",
  "length": 120,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "context": ["optional fact 1", "optional fact 2"]
}
```

## Troubleshooting

- If you get a `500 Internal Server Error`, check the terminal where `uvicorn` is running — server-side tracebacks are now logged to stdout for easier debugging.
- Ensure you run `uvicorn` from the project root so `src` is importable (e.g. `python -m uvicorn src.api.main:app`).
- On Windows/PowerShell, use `$env:OPENAI_API_KEY = "sk-..."` to set the key for the current session.

## Tests

Run unit tests for evaluation code:

```powershell
pytest src/eval/tests/
```

## Next improvements

- Optionally load `.env` automatically at app startup (via python-dotenv).
- Add a file logger to persist error traces to `logs/` as well as stdout.
- Provide a small example script that runs the server, calls the CLI, and saves the output to `outputs/` for reproducible demos.
