
import json
import re
from pathlib import Path
import logging




def extract_json(text: str) -> dict:
    """Extract JSON from model output."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise ValueError("No JSON found in model output")
        return json.loads(m.group(0))


def save_json_to_file(data: dict,folder_name:str, file_name: str) -> None:
    try:
        folder_path = Path(folder_name)
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / file_name
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4,  ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Failed to save JSON to file: {e}")


def write_log_to_file(data: dict):
    try:
        LOG_FILE = Path(__file__).parent / "requests_log.jsonl"
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        raise RuntimeError(f"Logging operation failed :{e}")