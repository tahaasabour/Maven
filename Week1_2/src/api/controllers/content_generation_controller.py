from fastapi import APIRouter, HTTPException
from pathlib import Path

from ..models.generaterequest import GenerateRequest
from ..models.generateresponse import GenerateResponse
from ..llm.implementations.general_prompt_moderator import general_prompt_moderator
from ..prompts_templates.prompt_template_helper import prompt_template_helper
from ..llm.llm_service import llm_service
from ..llm.implementations.hugging_face_moderator import hugging_face_moderator
from ..helpers.utils import save_json_to_file
from ..llm.protocols.llm_moderator import llm_moderator
from ..llm.protocols.prompt_moderator import prompt_moderator



router = APIRouter(prefix="/generate", tags=["Generate"])


@router.post("", response_model=GenerateResponse)
async def generate_text(payload: GenerateRequest):
    try:

        prmpt_modt:prompt_moderator=general_prompt_moderator()
        llm_modt:llm_moderator=hugging_face_moderator()

        prompt = payload.input_text
        redacted_prompt = prmpt_modt.pre_redact_pii(prompt)
        payload.input_text = redacted_prompt

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

        model_data = {
            "provider": payload.provider,
            "model": payload.model,
            "prompt": rendered_prompt,
        }
        response = llm_service().call_model(model_data)

        moderated_response = llm_modt.moderate(response)

        save_json_to_file(
            data=moderated_response,
            folder_name=Path(__file__).parent.parent / "outputs",
            file_name=f"generate_response_{moderated_response.get('request_id')}.json"
        )

        return moderated_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
