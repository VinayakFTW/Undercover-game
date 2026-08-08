from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.controller.core.game_controller import router as speech_router
from server.controller.team.registerTeam_controller import register_team
from server.controller.session.start_session_controller import start_session
from server.controller.session.join_session_controller import join_session
from server.controller.core.allocate_stake_controller import allocate_stake
from server.controller.core.submit_prompt_controller import submit_prompt
from server.controller.core.check_bounty_controller import check_bounty
from server.controller.session.calculate_scores_controller import calculate_scores
from server.controller.leaderboard.getCurrentSessionLeaderboard import get_current_session_leaderboard
from server.controller.leaderboard.getGlobalLeaderboard import get_global_leaderboard
from server.controller.candidate.revealCandidate import reveal_candidate
from server.controller.candidate.getAllCandiates import get_all_candidates
from server.controller.candidate.registerCandidate import register_candidate
from server.controller.team.createPlayer_controller import create_player
from server.controller.host.delete_candidate_controller import delete_candidate
from server.controller.host.delete_team_controller import delete_team
from server.controller.host.team_management_controller import get_all_teams, edit_team
from server.controller.session.create_session_controller import create_session
from server.controller.candidate.submit_answer_controller import submit_candidate_answer
from server.controller.session.update_session_controller import update_session
from server.controller.session.get_session_state_controller import get_session_state
from server.controller.candidate.generate_ai_response_controller import generate_ai_response

app = FastAPI(title="UNDERCOVER AI Game Show Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_to_route(path: str, endpoint, methods: list):
    app.add_api_route(path=path, endpoint=endpoint, methods=methods)


# --- ROUTE REGISTRATION ---
add_to_route("/api/team/register", register_team, methods=["POST"])
add_to_route("/api/session/start", start_session, methods=["POST"])
add_to_route("/api/session/join", join_session, methods=["POST"])
add_to_route("/api/round/allocate", allocate_stake, methods=["POST"])
add_to_route("/api/round/prompt", submit_prompt, methods=["POST"])
add_to_route("/api/round/bounty", check_bounty, methods=["POST"])
add_to_route("/api/session/calculate_scores", calculate_scores, methods=["POST"])
add_to_route("/api/leaderboard/session", get_current_session_leaderboard, methods=["GET"])
add_to_route("/api/leaderboard/global", get_global_leaderboard, methods=["GET"])
add_to_route("/api/candidate/reveal", reveal_candidate, methods=["POST"])
add_to_route("/api/candidate/all", get_all_candidates, methods=["GET"])
add_to_route("/api/candidate/register", register_candidate, methods=["POST"])
add_to_route("/api/team/createPlayer", create_player, methods=["POST"])
add_to_route("/api/host/delete_candidate/{candidate_id}", delete_candidate, methods=["DELETE"])
add_to_route("/api/host/delete_team/{team_id}", delete_team, methods=["DELETE"])
add_to_route("/api/host/teams", get_all_teams, methods=["GET"])
add_to_route("/api/host/edit_team/{team_id}", edit_team, methods=["PUT"])
add_to_route("/api/session/create", create_session, methods=["POST"])
add_to_route("/api/candidate/answer", submit_candidate_answer, methods=["POST"])
add_to_route("/api/candidate/generate", generate_ai_response, methods=["POST"])
add_to_route("/api/session/update_status", update_session, methods=["POST"])
add_to_route("/api/session/{session_id}/state", get_session_state, methods=["GET"])
app.include_router(speech_router)
