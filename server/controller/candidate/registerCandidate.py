from fastapi import HTTPException
from pydantic import BaseModel
from server.config.db import SessionLocal
from server.models.db_models import Candidate
from server.models.request_models import CandidateRegisterRequest

def register_candidate(request: CandidateRegisterRequest):
    with SessionLocal() as db:
        existing = (
            db.query(Candidate)
            .filter(Candidate.candidate_id == request.candidate_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Candidate ID already exists."
            )

        new_candidate = Candidate(
            candidate_id=request.candidate_id, name=request.name, ai=request.ai
        )
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        return {
            "status": "success",
            "message": "Candidate registered successfully",
            "candidate": {
                "candidate_id": new_candidate.candidate_id,
                "name": new_candidate.name,
                "ai": new_candidate.ai,
            },
        }