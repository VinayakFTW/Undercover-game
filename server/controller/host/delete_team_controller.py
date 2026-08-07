from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Team, Stake

def delete_team(team_id: str):
    """
    Controller to delete a team by their ID. 
    Cleans up associated stakes to prevent foreign key constraint violations.
    """
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
            
        # Delete related stakes first to avoid foreign key violations 
        # (if cascade delete isn't set up at the DB level)
        db.query(Stake).filter(Stake.team_id == team_id).delete()
        
        db.delete(team)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Team '{team_id}' deleted successfully."
        }