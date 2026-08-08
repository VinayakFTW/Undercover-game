from server.config.db import SessionLocal
from server.models.db_models import Candidate


def get_all_candidates():
    with SessionLocal() as db:
        candidates = db.query(Candidate).all()
        return {
            "status": "success",
            "candidates": [
                {
                    "candidate_id": candidate.candidate_id,
                    "name": candidate.name,
                    "ai": candidate.ai,
                }
                for candidate in candidates
            ],
        }