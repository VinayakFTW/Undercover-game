from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Candidate

def delete_candidate(candidate_id: str):
    """
    Controller to delete a candidate by their ID.
    """
    with SessionLocal() as db:
        candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")
            
        db.delete(candidate)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Candidate '{candidate_id}' deleted successfully."
        }