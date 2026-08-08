import uuid
from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Team
from server.models.request_models import TeamRegisterRequest


def register_team(request: TeamRegisterRequest):
    with SessionLocal() as db:
        team_id = f"team_{uuid.uuid4().hex[:8]}"

        new_team = Team(
            team_id=team_id,
            team_name=request.team_name,
            branch="",
            session_id=None,
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