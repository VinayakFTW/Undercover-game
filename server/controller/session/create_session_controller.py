import uuid
from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session
from server.models.request_models import SessionCreateRequest

def create_session(request: SessionCreateRequest):
    with SessionLocal() as db:
        session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"
        existing_session = db.query(Session).filter(Session.session_id == session_id).first()
        if existing_session:
            raise HTTPException(status_code=400, detail="Session already exists.")

        new_session = Session(session_id=session_id, status=request.status)
        db.add(new_session)
        db.commit()

        return {
            "status": "success",
            "message": f"Session '{session_id}' created successfully.",
            "session_id": session_id
        }