from fastapi import APIRouter, HTTPException
from pathlib import Path

from ..models.generaterequest import GenerateRequest
from ..models.generateresponse import GenerateResponse
from ..llm.implementations.general_prompt_moderator import general_prompt_moderator
from ..prompts_templates.prompt_template_helper import prompt_template_helper
from ..llm.llm_service import llm_service
from ..llm.implementations.hugging_face_moderator import hugging_face_moderator
from ..helpers.utils import save_json_to_file


router = APIRouter(prefix="/generate", tags=["Generate"])


@router.post("", response_model=GenerateResponse)
async def generate_text(payload: GenerateRequest):
    try:
        # Step 1: Moderate and redact PII
        prompt = payload.input_text
        redacted_prompt = general_prompt_moderator().pre_redact_pii(prompt)
        payload.input_text = redacted_prompt

        # Step 2: Render prompt from template
        prompt_templates_path = str(Path(__file__).parent.parent / "prompts_templates")
        target_prompt_template = payload.persona.value.split("_")[0] + ".j2"
        
        rendered_prompt = prompt_template_helper.render_template(
            template_path=prompt_templates_path,
            template_name=target_prompt_template,
            context={
                "input_text": redacted_prompt,
                "persona": payload.persona,
                "role": payload.persona,
                "tone": "balanced",
                "audience": payload.audience,
                "context": payload.context,
                "length": payload.length
            }
        )

        # Step 3: Call model
        model_data = {
            "provider": payload.provider,
            "model": payload.model,
            "prompt": rendered_prompt,
        }
        response = llm_service().call_model(model_data)

        # Step 4: Moderate model output
        moderated_response = hugging_face_moderator().moderate(response)

        # Step 5: Save response to file
        save_json_to_file(
            data=moderated_response,
            folder_name=Path(__file__).parent.parent / "outputs",
            file_name=f"generate_response_{moderated_response.get('request_id')}.json"
        )

        return moderated_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
