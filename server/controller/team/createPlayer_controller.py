from fastapi import HTTPException
from pydantic import BaseModel
from server.config.db import SessionLocal
from server.models.db_models import Player


class CreatePlayerRequest(BaseModel):
    player_id: str
    name: str


def create_player(request: CreatePlayerRequest):
    with SessionLocal() as db:
        existing = (
            db.query(Player).filter(Player.player_id == request.player_id).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Player ID already exists."
            )

        new_player = Player(player_id=request.player_id, name=request.name)
        db.add(new_player)
        db.commit()
        db.refresh(new_player)

        return {
            "status": "success",
            "message": "Player created successfully.",
            "player": {
                "player_id": new_player.player_id,
                "name": new_player.name,
            },
        }