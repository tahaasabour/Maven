import time
import logging
from pathlib import Path
from fastapi import Request
from fastapi.responses import JSONResponse
from ..helpers.json_formatter import JsonFormatter  # adjust import if needed

log_file_path = Path(__file__).parent.parent / "logs.json"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, mode="a")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)


async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()

                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}

                request._receive = receive
            except Exception:
                pass

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "client": request.client.host if request.client else None,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "request_body": body.decode("utf-8") if body else None,
        }

        logger.info("Request processed", extra={"extra_data": log_data})
        return response

    except Exception as e:
        logger.error(f"Middleware error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
