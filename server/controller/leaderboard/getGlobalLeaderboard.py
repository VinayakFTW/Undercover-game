from server.config.db import SessionLocal
from server.models.db_models import MasterLeaderboard


def get_global_leaderboard():
    with SessionLocal() as db:
        entries = (
            db.query(MasterLeaderboard)
            .order_by(
                MasterLeaderboard.rank.asc(),
                MasterLeaderboard.total_coins.desc(),
            )
            .all()
        )

        leaderboard = [
            {
                "rank": entry.rank,
                "team_name": entry.team_name,
                "branch": entry.branch,
                "total_coins": entry.total_coins,
                "raw_total_coins": entry.raw_total_coins,
                "sessions_played": entry.sessions_played,
                "highest_score": entry.highest_score,
                "highest_raw_score": entry.highest_raw_score,
                "last_updated": entry.last_updated.isoformat()
                if entry.last_updated
                else None,
            }
            for entry in entries
        ]

        return {"status": "success", "global_leaderboard": leaderboard}