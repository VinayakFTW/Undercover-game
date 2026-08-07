from fastapi import FastAPI

from server.controller.core.game_controller import generate_candidate_speech,session_voice_map
from server.controller.team.registerTeam_controller import register_team
from server.controller.session.start_session_controller import start_session
from server.controller.session.join_session_controller import join_session
from server.controller.core.allocate_stake_controller import allocate_stake
from server.controller.core.submit_prompt_controller import submit_prompt
from server.controller.core.check_bounty_controller import check_bounty
from server.controller.core.lifeline_controller import use_lifeline
from server.controller.leaderboard.getCurrentSessionLeaderboard import get_current_session_leaderboard
from server.controller.leaderboard.getGlobalLeaderboard import get_global_leaderboard
from server.controller.candidate.revealCandidate import reveal_candidate

from server.utils.tts_utils import tts_service

app = FastAPI(title="UNDERCOVER AI Game Show Backend")

def add_to_route(path: str, endpoint, methods: list):
    app.add_api_route(path=path, endpoint=endpoint, methods=methods)

# --- ROUTE REGISTRATION ---
add_to_route("/api/team/register", register_team, methods=["POST"])
add_to_route("/api/session/start", start_session, methods=["POST"])
add_to_route("/api/session/join", join_session, methods=["POST"])
add_to_route("/api/round/allocate", allocate_stake, methods=["POST"])
add_to_route("/api/round/prompt", submit_prompt, methods=["POST"])
add_to_route("/api/round/bounty", check_bounty, methods=["POST"])
add_to_route("/api/lifeline/use", use_lifeline, methods=["POST"])
add_to_route("/api/leaderboard/session", get_current_session_leaderboard, methods=["GET"])
add_to_route("/api/leaderboard/global", get_global_leaderboard, methods=["GET"])
add_to_route("/api/candidate/reveal", reveal_candidate, methods=["POST"])
add_to_route("/api/candidate/speech", generate_candidate_speech, methods=["POST"])

@app.post("/api/session/init-voices/{session_id}")

async def init_session_voices(session_id: str):
    """
    Initializes 4 randomized candidate voices for a new session.
    """
    session_voice_map[session_id] = tts_service.randomize_session_voices()
    return {"status": "success", "session_id": session_id, "message": "Voices randomized."}