from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Round, Session
from server.models.request_models import CandidateAnswerRequest


def submit_candidate_answer(request: CandidateAnswerRequest):
    with SessionLocal() as db:
        session_obj = db.query(Session).filter(Session.session_id == request.session_id).first()
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        round_obj = db.query(Round).filter(Round.round_id == request.round_id, Round.session_id == request.session_id).first()
        if not round_obj:
            raise HTTPException(status_code=404, detail="Round not found.")

        answers = dict(round_obj.candidate_answers or {})
        answers[request.candidate_id] = request.text
        round_obj.candidate_answers = answers

        db.commit()

        return {
            "status": "success",
            "message": "Answer submitted successfully.",
            "candidate_id": request.candidate_id,
            "round_id": request.round_id,
        }
