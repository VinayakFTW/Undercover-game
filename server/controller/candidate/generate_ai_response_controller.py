from pydantic import BaseModel
from fastapi import HTTPException
from server.utils.ai_utils import generate_ai_candidate_response

class GenerateAIResponseRequest(BaseModel):
    prompt: str
    conversation_history: list = []

async def generate_ai_response(request: GenerateAIResponseRequest):
    try:
        response_text = await generate_ai_candidate_response(
            prompt=request.prompt,
            conversation_history=request.conversation_history
        )
        return {"status": "success", "response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
