from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Team

def get_team(team_id: str):
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
        
        return {
            "status": "success",
            "team": {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "branch": team.branch,
                "session_id": team.session_id,
                "coins": team.coins
            }
        }
