from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Session, Team


def get_current_session_leaderboard(session_id: str):
    with SessionLocal() as db:
        session_obj = (
            db.query(Session).filter(Session.session_id == session_id).first()
        )
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")

        teams = (
            db.query(Team)
            .filter(Team.session_id == session_id)
            .order_by(Team.total_score.desc(), Team.coins.desc())
            .all()
        )

        leaderboard = [
            {
                "rank": idx + 1,
                "team_id": team.team_id,
                "team_name": team.team_name,
                "branch": team.branch,
                "coins": team.coins,
                "total_score": team.total_score,
                "raw_score": team.raw_score,
                "speed_bonus": team.speed_bonus,
                "conviction_bonus": team.conviction_bonus,
                "risk_bonus": team.risk_bonus,
            }
            for idx, team in enumerate(teams)
        ]

        return {
            "status": "success",
            "session_id": session_id,
            "leaderboard": leaderboard,
        }