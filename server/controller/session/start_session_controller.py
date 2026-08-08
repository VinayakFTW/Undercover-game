from fastapi import HTTPException
from server.config.db import SessionLocal
from server.constants.db_enums import SessionStatus
from server.models.db_models import Session
import datetime

def start_session(session_id: str):
    with SessionLocal() as db:
        session_obj = (
            db.query(Session).filter(Session.session_id == session_id).first()
        )
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        session_obj.status = SessionStatus.ROUND1
        session_obj.current_round_start_time = datetime.datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "message": f"Session {session_id} started successfully.",
            "session_id": session_id,
            "session_status": session_obj.status.value
            if hasattr(session_obj.status, "value")
            else str(session_obj.status),
        }