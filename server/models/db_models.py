import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    String, Integer, Float, Boolean, Date, DateTime, 
    ForeignKey, JSON, Enum, Table, Column, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import BASE
from server.constants.db_enums import SessionStatus

# Association table for the Many-to-Many relationship between Rounds and Players
round_players = Table(
    "round_players",
    BASE.metadata,
    Column("round_id", ForeignKey("rounds.round_id"), primary_key=True),
    Column("player_id", ForeignKey("players.player_id"), primary_key=True),
)

session_candidates = Table(
    "session_candidates",
    BASE.metadata,
    Column("session_id", ForeignKey("sessions.session_id"), primary_key=True),
    Column("candidate_id", ForeignKey("candidates.candidate_id"), primary_key=True),
)

class Session(BASE):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date)
    time_slot: Mapped[str] = mapped_column(String)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus))
    
    final_leaderboard: Mapped[list] = mapped_column(JSON, default=list)
    reveal_order: Mapped[list] = mapped_column(JSON, default=list)

    # Relationships
    teams: Mapped[List["Team"]] = relationship(back_populates="session")
    rounds: Mapped[List["Round"]] = relationship(back_populates="session")
    candidates: Mapped[List["Candidate"]] = relationship(
        secondary=session_candidates, back_populates="sessions"
    )
    players: Mapped[List["Player"]] = relationship(
        secondary="round_players", viewonly=True, back_populates="rounds"
    )


class Candidate(BASE):
    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        secondary=session_candidates, back_populates="candidates"
    )


class Player(BASE):
    __tablename__ = "players"

    player_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    
    # Relationships
    rounds: Mapped[List["Round"]] = relationship(
        secondary=round_players, back_populates="players"
    )


class Round(BASE):
    __tablename__ = "rounds"

    round_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.session_id"))
    
    questions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    responses: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    staking_distribution: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    multiplier: Mapped[float] = mapped_column(Float)
    bounty_phrase: Mapped[str] = mapped_column(String)
    bounty_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="rounds")
    stakes: Mapped[List["Stake"]] = relationship(back_populates="round")
    players: Mapped[List["Player"]] = relationship(
        secondary=round_players, back_populates="rounds"
    )


class Team(BASE):
    __tablename__ = "teams"

    team_id: Mapped[str] = mapped_column(String, primary_key=True)
    team_name: Mapped[str] = mapped_column(String)
    branch: Mapped[str] = mapped_column(String)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.session_id"))
    
    coins: Mapped[int] = mapped_column(Integer, default=10000)
    lifeline_used: Mapped[bool] = mapped_column(Boolean, default=False)
    lifeline_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_stake: Mapped[float] = mapped_column(Float, default=0.0)
    bounty_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    raw_score: Mapped[float] = mapped_column(Float, default=0.0)
    speed_bonus: Mapped[float] = mapped_column(Float, default=0.0)
    conviction_bonus: Mapped[float] = mapped_column(Float, default=0.0)
    risk_bonus: Mapped[float] = mapped_column(Float, default=0.0)
    prompt_submitted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="teams")
    stakes: Mapped[List["Stake"]] = relationship(back_populates="team")


class Stake(BASE):
    __tablename__ = "stakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_id: Mapped[str] = mapped_column(ForeignKey("rounds.round_id"))
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.team_id"))
    candidate: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    round: Mapped["Round"] = relationship(back_populates="stakes")
    team: Mapped["Team"] = relationship(back_populates="stakes")


class MasterLeaderboard(BASE):
    __tablename__ = "master_leaderboard"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_name: Mapped[str] = mapped_column(String)
    branch: Mapped[str] = mapped_column(String)
    
    total_coins: Mapped[int] = mapped_column(Integer, default=0)
    raw_total_coins: Mapped[int] = mapped_column(Integer, default=0)
    sessions_played: Mapped[int] = mapped_column(Integer, default=0)
    highest_score: Mapped[float] = mapped_column(Float, default=0.0)
    highest_raw_score: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer)
    
    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )