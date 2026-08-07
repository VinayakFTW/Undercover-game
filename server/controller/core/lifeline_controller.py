from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Team
from server.models.request_models import LifelineUseRequest


def use_lifeline(request: LifelineUseRequest):
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == request.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")

        if team.lifeline_used:
            raise HTTPException(
                status_code=400,
                detail="Lifeline has already been used by this team.",
            )

        team.lifeline_used = True
        team.lifeline_type = request.lifeline_type
        db.commit()

        return {
            "status": "success",
            "message": f"Lifeline '{request.lifeline_type}' activated successfully.",
            "team_id": request.team_id,
            "lifeline_type": request.lifeline_type,
        }