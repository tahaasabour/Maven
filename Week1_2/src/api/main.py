
from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import JSONResponse
from .llm.implementations import hugging_face_moderator
from .models.generaterequest import GenerateRequest
from .models.generateresponse import GenerateResponse
from .llm.implementations.general_prompt_moderator import general_prompt_moderator
from .prompts_templates.prompt_template_helper import prompt_template_helper
from pathlib import Path
from .llm.llm_service import llm_service
from .llm.implementations.hugging_face_moderator import hugging_face_moderator
from .helpers.utils import save_json_to_file
from .helpers.json_formatter import JsonFormatter
import time
import logging
from .controllers import content_generation_controller


from .middlewares.log_middleware import log_requests
from .middlewares.exception_handler_middleware import global_exception_handler


app = FastAPI()

app.middleware("http")(log_requests)
app.exception_handler(Exception)(global_exception_handler)

app.include_router(content_generation_controller.router)