from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session, Round, Candidate, session_candidates

def get_session_state(session_id: str):
    with SessionLocal() as db:
        session_obj = db.query(Session).filter(Session.session_id == session_id).first()
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        # Determine current round based on status
        current_round = None
        round_obj = None
        if session_obj.status.value.startswith("round"):
            round_num = session_obj.status.value.replace("round", "")
            # Assuming round_id format is like session_id_r1 or something. 
            # Or we can just get all rounds and pick the one with matching number.
            rounds = db.query(Round).filter(Round.session_id == session_id).all()
            rounds = sorted(rounds, key=lambda r: r.round_id)
            if len(rounds) >= int(round_num):
                round_obj = rounds[int(round_num) - 1]

        candidates = session_obj.candidates

        return {
            "status": session_obj.status,
            "current_round_start_time": session_obj.current_round_start_time,
            "candidates": [{"id": c.candidate_id, "name": c.name, "ai": c.ai} for c in candidates],
            "current_round": {
                "round_id": round_obj.round_id if round_obj else None,
                "candidate_answers": round_obj.candidate_answers if round_obj else {},
                "bounty_phrase": round_obj.bounty_phrase if round_obj else None,
            } if round_obj else None,
            "reveal_order": session_obj.reveal_order,
        }
