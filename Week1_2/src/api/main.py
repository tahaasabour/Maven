
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from api.llm import hugging_face_moderator
from .models.generaterequest import GenerateRequest
from .models.generateresponse import GenerateResponse
from .llm.general_prompt_moderator import general_prompt_moderator
from .prompts_templates.prompt_template_helper import prompt_template_helper
from pathlib import Path
from .llm.ll_service import llm_service
from .llm.hugging_face_moderator import hugging_face_moderator
from .utils import save_json_to_file
import time
import logging



class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
        return json.dumps(log_record)




log_file_path = Path(__file__).parent / "logs.json"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, mode="a")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)


app = FastAPI()




@app.middleware("http")
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
            "request_body": body.decode("utf-8") if body else None
        }
        
        logger.info(f"{log_data}")
        return response
        
    except Exception as e:
        logger.error(f"Middleware error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
   



@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/generate", response_model= GenerateResponse)
async def generate_text(payload: GenerateRequest):
    try:
        prompt = payload.input_text
        redacted_prompt = general_prompt_moderator().pre_redact_pii(prompt)
        payload.input_text = redacted_prompt

        prompt_templates_path = str(Path(__file__).parent / "prompts_templates")
        target_prompt_template = payload.persona.value.split("_")[0] + ".j2"
        
        rendered_prompt = prompt_template_helper.render_template(
            template_path=prompt_templates_path,
            template_name=target_prompt_template,
            context=
            {
                "input_text": redacted_prompt, 
                "persona": payload.persona,
                "role": payload.persona, 
                "tone": "balanced", 
                "audience": payload.audience, 
                "context": payload.context, 
                "length": payload.length
            }
        )


        model_data  =  {
            "provider": payload.provider,
            "model": payload.model,
            "prompt": rendered_prompt,
        }

        response = llm_service().call_model(model_data)


        moderated_response = hugging_face_moderator().moderate(response)

        print(moderated_response)
        
        save_json_to_file(
            data=moderated_response,
            folder_name=Path(__file__).parent / "outputs",
            file_name=f"generate_response_{moderated_response.get('request_id')}.json"
        )
        return moderated_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )