from datetime import date, datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from server.constants.db_enums import SessionStatus

class Stake(BaseModel):
    roundId: str = Field(..., description="Foreign Key -> Round.roundId")
    candidate: str
    amount: float
    timestamp: datetime

class Round(BaseModel):
    roundId: str = Field(..., description="Unique identifier for the round")
    sessionId: str = Field(..., description="Foreign Key -> Session.sessionId")
    questions: List[Any]
    responses: List[Any]
    stakingDistribution: Dict[str, float]
    multiplier: float
    bountyPhrase: str
    bountyTriggered: bool
    triggeredBy: Optional[str] = None

# Main Collections

class Team(BaseModel):
    """Teams Collection"""
    teamId: str
    teamName: str
    branch: str
    sessionId: str = Field(..., description="Foreign Key -> Session.sessionId")
    coins: int = Field(default=10000, description="UPDATED from 1000") 
    lifelineUsed: bool = False
    lifelineType: Optional[str] = None
    currentStake: float
    stakes: List[Stake] = []
    bountyTriggered: bool = False
    totalScore: float = Field(default=0.0, description="(NEW)")
    rawScore: float = Field(default=0.0, description="(NEW)")
    speedBonus: float = Field(default=0.0, description="(NEW)")
    convictionBonus: float = Field(default=0.0, description="(NEW)")
    riskBonus: float = Field(default=0.0, description="(NEW)")    
    promptSubmitted: bool = False 


class Session(BaseModel):
    """Sessions Collection"""
    sessionId: str = Field(..., description="Unique identifier for the session")
    date: date
    timeSlot: str
    status: SessionStatus
    teams: List[str]
    candidates: Dict[str, str] 
    rounds: List[Round] = []
    finalLeaderboard: List[Any] = []
    revealOrder: List[str] = []


class MasterLeaderboard(BaseModel):
    """Master Leaderboard"""
    teamName: str
    branch: str
    totalCoins: int = Field(default=0, description="(NEW)")
    rawTotalCoins: int = Field(default=0, description="(NEW)")
    sessionsPlayed: int = 0
    highestScore: float = Field(default=0.0, description="(NEW)")
    highestRawScore: float = Field(default=0.0, description="(NEW)")
    rank: int
    lastUpdated: datetime