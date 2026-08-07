import uuid
from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session, Team
from server.models.request_models import TeamRegisterRequest


def register_team(request: TeamRegisterRequest):
    with SessionLocal() as db:
        session_obj = (
            db.query(Session)
            .filter(Session.session_id == request.session_id)
            .first()
        )
        if not session_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Session with id '{request.session_id}' does not exist.",
            )

        team_id = f"team_{uuid.uuid4().hex[:8]}"

        new_team = Team(
            team_id=team_id,
            team_name=request.team_name,
            branch=request.branch,
            session_id=request.session_id,
            coins=10000,
        )

        db.add(new_team)
        db.commit()
        db.refresh(new_team)

        return {
            "status": "success",
            "message": "Team registered successfully.",
            "team": {
                "team_id": new_team.team_id,
                "team_name": new_team.team_name,
                "branch": new_team.branch,
                "session_id": new_team.session_id,
                "coins": new_team.coins,
            },
        }