from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Round, Team
from server.models.request_models import RoundPromptRequest


def submit_prompt(request: RoundPromptRequest):
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == request.team_id).first()
        if not team:
            team = Team(
                team_id=request.team_id,
                session_id='DEFAULT_SESSION',
                team_name=request.team_id,
                branch="Default"
            )
            db.add(team)
            db.commit()
            db.refresh(team)

        round_obj = (
            db.query(Round).filter(Round.round_id == request.round_id).first()
        )
        if not round_obj:
            raise HTTPException(status_code=404, detail="Round not found.")

        team.prompt_submitted = True

        responses = list(round_obj.responses or [])
        responses.append({"team_id": request.team_id, "prompt": request.prompt})
        round_obj.responses = responses

        db.commit()

        return {
            "status": "success",
            "message": "Prompt submitted successfully.",
            "team_id": request.team_id,
            "round_id": request.round_id,
        }