from fastapi import HTTPException
from server.config.db import SessionLocal
from server.models.db_models import Round, Stake, Team
from server.models.request_models import RoundAllocateRequest


def allocate_stake(request: RoundAllocateRequest):
    with SessionLocal() as db:
        team = db.query(Team).filter(Team.team_id == request.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")

        round_obj = (
            db.query(Round).filter(Round.round_id == request.round_id).first()
        )
        if not round_obj:
            raise HTTPException(status_code=404, detail="Round not found.")

        total_allocated = sum(alloc.amount for alloc in request.allocations)

        # Remove existing stakes for this team and round if re-allocating
        db.query(Stake).filter(
            Stake.round_id == request.round_id, Stake.team_id == request.team_id
        ).delete()

        created_stakes = []
        for alloc in request.allocations:
            stake = Stake(
                round_id=request.round_id,
                team_id=request.team_id,
                candidate=alloc.candidate_id,
                amount=alloc.amount,
            )
            db.add(stake)
            created_stakes.append(
                {"candidate_id": alloc.candidate_id, "amount": alloc.amount}
            )

        team.current_stake = total_allocated
        db.commit()

        return {
            "status": "success",
            "message": "Stakes allocated successfully.",
            "team_id": request.team_id,
            "round_id": request.round_id,
            "lock_in_time_seconds": request.lock_in_time_seconds,
            "allocations": created_stakes,
        }