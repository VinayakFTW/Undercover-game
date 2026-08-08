from fastapi import APIRouter, HTTPException, Response
from server.models.request_models import CandidateSpeechRequest
from server.utils.tts_utils import tts_service

router = APIRouter()

session_voice_map = {}

@router.post("/api/session/{session_id}/init")
async def init_session_voices(session_id: str):
    """
    Calls the TTS service to assign random voices for this session 
    and saves them to the map.
    """
    try:
        voices = tts_service.randomize_session_voices()
        session_voice_map[session_id] = voices
        if session_id not in session_voice_map:
            raise HTTPException(status_code=500, detail="Failed to initialize session voices.")
        return {"message": f"Voices initialized for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/candidate/speech")
async def generate_candidate_speech(request: CandidateSpeechRequest):
    """
    Renders speech for both human and AI candidate text using assigned session voices.
    """
    session_voices = session_voice_map.get(request.session_id)
    if not session_voices:
        # Auto-initialize session voices to prevent 404
        session_voices = tts_service.randomize_session_voices()
        session_voice_map[request.session_id] = session_voices

    speaker_embedding = session_voices.get(request.candidate_id)
    if speaker_embedding is None:
        # Fallback to random voice if candidate ID is unconventional
        import random
        speaker_embedding = random.choice(list(session_voices.values()))

    # Truncate text to avoid SpeechT5 600 char limit (which causes 400 Bad Request)
    text_to_speak = request.text
    if len(text_to_speak) > 600:
        text_to_speak = text_to_speak[:597] + "..."

    # 3. Generate the audio
    try:
        audio_bytes = await tts_service.generate_speech(text_to_speak, speaker_embedding)
        return Response(content=audio_bytes, media_type="audio/wav")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating speech.")