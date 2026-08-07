from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Candidate, Session


def reveal_candidate(session_id: str, candidate_id: str):
    with SessionLocal() as db:
        session_obj = (
            db.query(Session).filter(Session.session_id == session_id).first()
        )
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        candidate = (
            db.query(Candidate)
            .filter(Candidate.candidate_id == candidate_id)
            .first()
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")

        reveal_order = session_obj.reveal_order or []
        if candidate_id not in reveal_order:
            reveal_order.append(candidate_id)
            session_obj.reveal_order = reveal_order
            db.commit()

        return {
            "status": "success",
            "message": f"Candidate {candidate_id} revealed.",
            "reveal_order": session_obj.reveal_order,
        }