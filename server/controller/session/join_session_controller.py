from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session, Team
from server.models.request_models import SessionJoinRequest


def join_session(request: SessionJoinRequest):
    with SessionLocal() as db:
        session_obj = (
            db.query(Session)
            .filter(Session.session_id == request.session_id)
            .first()
        )
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        team = db.query(Team).filter(Team.team_id == request.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")

        team.session_id = request.session_id
        db.commit()

        return {
            "status": "success",
            "message": f"Team {request.team_id} joined session {request.session_id}.",
            "session_id": request.session_id,
            "team_id": request.team_id,
        }