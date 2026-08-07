from fastapi import HTTPException, Response
from server.models.request_models import CandidateSpeechRequest
from server.utils.tts_utils import tts_service

session_voice_map = {}

async def generate_candidate_speech(request: CandidateSpeechRequest):
    """
    Renders speech for both human and AI candidate text using assigned session voices.
    """
    session_voices = session_voice_map.get(request.session_id)
    if not session_voices:
        raise HTTPException(status_code=404, detail="Session voice map not initialized.")

    speaker_embedding = session_voices.get(request.candidate_id)
    if speaker_embedding is None:
        raise HTTPException(status_code=400, detail="Invalid candidate identifier.")

    audio_bytes = await tts_service.generate_speech(request.text, speaker_embedding)
    
    return Response(content=audio_bytes, media_type="audio/wav")