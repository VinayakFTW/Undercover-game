from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session, Round
from server.models.request_models import sessionUpdateRequest
from server.constants.db_enums import SessionStatus
import datetime

def update_session(request: sessionUpdateRequest):
    with SessionLocal() as db:
        session_obj = db.query(Session).filter(Session.session_id == request.session_id).first()
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        session_obj.status = request.status
        
        if request.status in [SessionStatus.ROUND1, SessionStatus.ROUND2, SessionStatus.ROUND3]:
            session_obj.current_round_start_time = datetime.datetime.utcnow()
            
            # Auto-create the round if it doesn't exist
            round_id = request.status.value
            unique_round_id = f"{request.session_id}_{round_id}"
            existing_round = db.query(Round).filter(Round.round_id == unique_round_id, Round.session_id == request.session_id).first()
            if not existing_round:
                new_round = Round(
                    round_id=unique_round_id,
                    session_id=request.session_id,
                    multiplier=1.0,
                    bounty_phrase=""
                )
                db.add(new_round)
            
        db.commit()

        return {
            "status": "success",
            "message": f"Session updated to {request.status}",
            "session_id": request.session_id,
        }
