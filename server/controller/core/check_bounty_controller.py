from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Round, Team
from server.models.request_models import RoundBountyRequest


def check_bounty(request: RoundBountyRequest):
    with SessionLocal() as db:
        round_obj = (
            db.query(Round).filter(Round.round_id == request.round_id).first()
        )
        if not round_obj:
            raise HTTPException(status_code=404, detail="Round not found.")

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

        # Check if phrase matches bounty phrase
        is_triggered = (
            round_obj.bounty_phrase
            and round_obj.bounty_phrase.strip().lower()
            == request.triggered_phrase.strip().lower()
        )

        if is_triggered:
            round_obj.bounty_triggered = True
            round_obj.triggered_by = request.team_id
            team.bounty_triggered = True
            db.commit()
            return {
                "status": "success",
                "bounty_triggered": True,
                "message": "Bounty phrase matched successfully!",
            }
        else:
            return {
                "status": "failed",
                "bounty_triggered": False,
                "message": "Incorrect bounty phrase.",
            }