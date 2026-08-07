from pydantic import BaseModel, Field, field_validator
from typing import List

class CandidateRegisterRequest(BaseModel):
    candidate_id: str
    name: str
    

class TeamRegisterRequest(BaseModel):
    team_name: str
    branch: str
    session_id: str

class SessionJoinRequest(BaseModel):
    session_id: str
    team_id: str

class StakeAllocation(BaseModel):
    candidate_id: str = Field(..., description="Candidate identifier (matches Candidate.candidate_id)")
    amount: float = Field(..., ge=0.0, le=10000.0)

class RoundAllocateRequest(BaseModel):
    team_id: str
    round_id: str
    allocations: List[StakeAllocation]
    lock_in_time_seconds: float = Field(..., ge=0, le=25.0)

    @field_validator('allocations')
    def validate_total_allocation(cls, allocations):
        total = sum(alloc.amount for alloc in allocations)
        if total != 10000.0:
            raise ValueError("Total allocation must equal exactly 10,000 coins.")
        if not any(alloc.amount >= 1.0 for alloc in allocations):
            raise ValueError("At least 1 coin must be allocated.")
        return allocations

class RoundPromptRequest(BaseModel):
    team_id: str
    round_id: str
    prompt: str = Field(..., max_length=500)

class RoundBountyRequest(BaseModel):
    team_id: str
    round_id: str
    candidate_id: str
    triggered_phrase: str

class LifelineUseRequest(BaseModel):
    team_id: str
    lifeline_type: str = Field(..., description="50:50, Phone a Friend, or Double Check")

class CandidateSpeechRequest(BaseModel):
    round_id: str
    candidate_id: str = Field(..., description="Candidate identifier: A, B, C, or D")
    text: str = Field(..., max_length=1000, description="Typed text from human or AI candidate")