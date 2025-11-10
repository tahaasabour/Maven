import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from ..helpers.json_formatter import JsonFormatter
from pathlib import Path

log_file_path = Path(__file__).parent.parent / "logs.json"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, mode="a")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
