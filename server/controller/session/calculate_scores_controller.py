from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.config.db import SessionLocal
from server.models.db_models import Session, Team, Round, Stake
from server.utils.game_utils import (
    calculate_multiplier,
    calculate_speed_bonus,
    calculate_risk_bonus,
    get_round_weight
)

router = APIRouter()

class CalculateScoresRequest(BaseModel):
    session_id: str
    ai_candidate_id: str

@router.post("/api/session/calculate_scores")
def calculate_scores(request: CalculateScoresRequest):
    with SessionLocal() as db:
        session_obj = db.query(Session).filter(Session.session_id == request.session_id).first()
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found.")
            
        teams = db.query(Team).filter(Team.session_id == request.session_id).all()
        rounds = db.query(Round).filter(Round.session_id == request.session_id).all()
        
        # Sort rounds to ensure correct ordering (Round 1, 2, 3)
        # Assuming round_id contains some sort of ordering or we can just rely on stakes. 
        # Actually, let's map round names to 1, 2, 3 based on creation order or ID.
        rounds = sorted(rounds, key=lambda r: r.round_id)
        
        for team in teams:
            total_round_scores = 0.0
            total_weighted_stakes = 0.0
            
            primary_candidates = []
            max_r1_stake = 0.0
            avg_speed_bonus = 0.0
            rounds_played = 0
            
            for i, round_obj in enumerate(rounds):
                round_number = i + 1
                weight = get_round_weight(round_number)
                
                # Room stakes for this round
                all_stakes = db.query(Stake).filter(Stake.round_id == round_obj.round_id).all()
                total_room_coins = sum(s.amount for s in all_stakes)
                ai_coins = sum(s.amount for s in all_stakes if s.candidate == request.ai_candidate_id)
                
                round_multiplier = calculate_multiplier(total_room_coins, ai_coins)
                
                # Team stakes for this round
                team_stakes = [s for s in all_stakes if s.team_id == team.team_id]
                if not team_stakes:
                    continue
                    
                rounds_played += 1
                
                # Find primary candidate
                primary_candidate = max(team_stakes, key=lambda s: s.amount).candidate
                primary_candidates.append(primary_candidate)
                
                if round_number == 1:
                    max_r1_stake = max(s.amount for s in team_stakes)
                
                # Calculate team's stake on AI and speed bonus
                ai_team_stakes = [s for s in team_stakes if s.candidate == request.ai_candidate_id]
                ai_stake = sum(s.amount for s in ai_team_stakes)
                
                # Average speed bonus for the team in this round
                if team_stakes:
                    avg_lock_in = sum(s.lock_in_time for s in team_stakes) / len(team_stakes)
                    speed_bonus = calculate_speed_bonus(avg_lock_in)
                else:
                    speed_bonus = 1.0
                    
                avg_speed_bonus += speed_bonus
                
                round_score = ai_stake * weight * round_multiplier * speed_bonus
                total_round_scores += round_score
                total_weighted_stakes += ai_stake * weight
            
            if rounds_played > 0:
                avg_speed_bonus /= rounds_played
            else:
                avg_speed_bonus = 1.0
                
            risk_bonus = calculate_risk_bonus(max_r1_stake)
            
            unique_candidates = len(set(primary_candidates))
            if unique_candidates == 1 and len(primary_candidates) == 3:
                conviction_bonus = 1.15
            elif unique_candidates == 2 and len(primary_candidates) == 3:
                conviction_bonus = 1.10
            elif unique_candidates == 3:
                conviction_bonus = 1.05
            else:
                conviction_bonus = 1.00 # fallback if not all rounds played
                
            bounty_bonus = 0
            if team.bounty_triggered:
                bounty_bonus += 2500
            if team.prompt_submitted:
                bounty_bonus += 50
                
            final_score = (total_round_scores * risk_bonus * conviction_bonus) + bounty_bonus
            raw_score = total_weighted_stakes + bounty_bonus + avg_speed_bonus + conviction_bonus + risk_bonus
            
            team.total_score = round(final_score, 2)
            team.raw_score = round(raw_score, 2)
            team.speed_bonus = round(avg_speed_bonus, 2)
            team.conviction_bonus = conviction_bonus
            team.risk_bonus = risk_bonus
            
        db.commit()
        return {"status": "success", "message": "Scores calculated successfully."}
