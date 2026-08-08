from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Team

def get_all_teams():
    """
    Controller to fetch all teams across all sessions for host management purposes.
    """
    with SessionLocal() as db:
        teams = db.query(Team).all()
        
        team_list = [
            {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "branch": team.branch,
                "session_id": team.session_id,
                "coins": team.coins,
                "total_score": team.total_score,
                "raw_score": team.raw_score,
                "bounty_triggered": team.bounty_triggered
            }
            for team in teams
        ]
        
        return {
            "status": "success",
            "total_teams": len(team_list),
            "teams": team_list
        }

def edit_team(team_id: str, updated_data: dict):
    """
    Controller to edit a team's details by their ID.
    """
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
        
        # Update the team's attributes based on the provided data
        for key, value in updated_data.items():
            if hasattr(team, key):
                setattr(team, key, value)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Team '{team_id}' updated successfully."
        }