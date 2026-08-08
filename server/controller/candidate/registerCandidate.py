from fastapi import HTTPException
from pydantic import BaseModel
from server.config.db import SessionLocal
from server.models.db_models import Candidate
from server.models.request_models import CandidateRegisterRequest
from server.utils.ai_utils import generate_ai_candidate_response

async def register_candidate(request: CandidateRegisterRequest):
    response_text = request.response
    is_ai = request.ai

    if request.prompt:
        response_text = await generate_ai_candidate_response(prompt=request.prompt, conversation_history=[])
        is_ai = True

    with SessionLocal() as db:
        existing = (
            db.query(Candidate)
            .filter(Candidate.candidate_id == request.candidate_id)
            .first()
        )
        if existing:
            existing.response = response_text
            existing.ai = is_ai
            new_candidate = existing
        else:
            new_candidate = Candidate(
                candidate_id=request.candidate_id, response=response_text, ai=is_ai
            )
            db.add(new_candidate)
            
        db.commit()
        db.refresh(new_candidate)

        return {
            "status": "success",
            "message": "Candidate registered successfully",
            "candidate": {
                "candidate_id": new_candidate.candidate_id,
                "response": new_candidate.response,
                "ai": new_candidate.ai,
            },
        }