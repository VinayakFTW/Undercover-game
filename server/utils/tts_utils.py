import io
import random
import torch
import soundfile as sf
from typing import Dict
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset

class TTSService:
    def __init__(self):
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        
        embeddings_dataset = load_dataset("Matthijs/cldg-voices", split="train")
        self.voice_indices = [7306, 5639, 6799, 1792, 3100]
        
        self.speaker_embeddings = [
            torch.tensor(embeddings_dataset[idx]["xvector"]).unsqueeze(0)
            for idx in self.voice_indices
        ]

    def randomize_session_voices(self) -> Dict[str, torch.Tensor]:
        """
        Randomly assigns 4 distinct voices out of the 5 available options 
        for Candidates A, B, C, and D at the start of each play/session.
        """
        selected_voices = random.sample(self.speaker_embeddings, 4)
        return {
            "A": selected_voices[0],
            "B": selected_voices[1],
            "C": selected_voices[2],
            "D": selected_voices[3]
        }

    async def generate_speech(self, text: str, speaker_embedding: torch.Tensor) -> bytes:
        """
        Converts typed text from AI or human candidates into WAV audio bytes.
        """
        inputs = self.processor(text=text, return_tensors="pt")
        
        with torch.no_grad():
            spectrogram = self.model.generate_speech(
                inputs["input_ids"], 
                speaker_embedding, 
                vocoder=self.vocoder
            )

        buffer = io.BytesIO()
        sf.write(buffer, spectrogram.numpy(), samplerate=16000, format="WAV")
        buffer.seek(0)
        return buffer.getvalue()

tts_service = TTSService()