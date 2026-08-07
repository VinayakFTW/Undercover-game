import asyncio
import io
import os
import random
import re
import zipfile
from pathlib import Path
from typing import Dict

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download
from transformers import (
    SpeechT5ForTextToSpeech,
    SpeechT5HifiGan,
    SpeechT5Processor,
)


class TTSService:
    """
    SpeechT5-based Text-to-Speech service.

    Uses CMU ARCTIC X-vectors as speaker embeddings.
    Does not depend on the Hugging Face `datasets` package.
    """

    MODEL_NAME = "microsoft/speecht5_tts"
    VOCODER_NAME = "microsoft/speecht5_hifigan"

    HF_DATASET = "Matthijs/cmu-arctic-xvectors"
    EMBEDDING_ZIP = "spkrec-xvect.zip"

    SAMPLE_RATE = 16000

    def __init__(self):
        print("Initializing TTS service...")

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        print(f"TTS device: {self.device}")

        print("Loading SpeechT5 processor...")
        self.processor = SpeechT5Processor.from_pretrained(
            self.MODEL_NAME
        )

        print("Loading SpeechT5 model...")
        self.model = SpeechT5ForTextToSpeech.from_pretrained(
            self.MODEL_NAME
        ).to(self.device)
        self.model.eval()

        print("Loading SpeechT5 vocoder...")
        self.vocoder = SpeechT5HifiGan.from_pretrained(
            self.VOCODER_NAME
        ).to(self.device)
        self.vocoder.eval()

        print("Loading speaker embeddings...")
        self.speaker_embeddings = self._load_speaker_embeddings()

        print(
            f"Loaded {len(self.speaker_embeddings)} speaker voices."
        )

        # Print available speakers
        for speaker, embedding in self.speaker_embeddings.items():
            print(
                f"  {speaker}: embedding shape={tuple(embedding.shape)}"
            )

        print("TTS service ready.")

    def _load_speaker_embeddings(self) -> Dict[str, torch.Tensor]:
        """
        Downloads the CMU ARCTIC x-vector ZIP from Hugging Face,
        extracts the .npy files, and selects one embedding per
        distinct speaker.
        """
        zip_path = hf_hub_download(
            repo_id=self.HF_DATASET,
            filename=self.EMBEDDING_ZIP,
            repo_type="dataset",
        )
        print(f"Speaker embedding archive: {zip_path}")

        extract_dir = (
            Path(zip_path).parent
            / "cmu-arctic-xvectors-extracted"
        )

        extract_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        npy_files = list(extract_dir.rglob("*.npy"))

        if not npy_files:
            print("Extracting speaker embeddings...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            npy_files = list(
                extract_dir.rglob("*.npy")
            )

        if not npy_files:
            raise RuntimeError(
                "No .npy speaker embeddings were found "
                "inside spkrec-xvect.zip"
            )

        print(
            f"Found {len(npy_files)} speaker embedding files."
        )

        speakers = {}

        for file_path in npy_files:
            speaker = self._extract_speaker_id(
                file_path.name
            )
            if speaker is None:
                continue

            speakers.setdefault(
                speaker,
                [],
            ).append(file_path)

        if not speakers:
            raise RuntimeError(
                "Could not determine speaker IDs from "
                "the CMU ARCTIC embedding filenames."
            )

        print(
            "Available CMU ARCTIC speakers:",
            ", ".join(sorted(speakers.keys())),
        )

        speaker_embeddings = {}

        for speaker, files in speakers.items():
            selected_file = random.choice(files)
            vector = np.load(
                selected_file
            ).astype(np.float32)

            if vector.shape != (512,):
                raise RuntimeError(
                    f"Unexpected x-vector shape "
                    f"{vector.shape} in {selected_file}"
                )

            tensor = torch.from_numpy(vector)
            tensor = tensor.unsqueeze(0)
            tensor = tensor.to(self.device)

            speaker_embeddings[speaker] = tensor

        return speaker_embeddings

    @staticmethod
    def _extract_speaker_id(filename: str):
        """
        Extract CMU ARCTIC speaker ID from filenames.
        """
        match = re.search(
            r"cmu_[a-z]+_([a-z]{3})_arctic",
            filename.lower(),
        )
        if match:
            return match.group(1)
        return None

    def randomize_session_voices(
        self,
    ) -> Dict[str, torch.Tensor]:
        """
        Randomly assigns 4 distinct speakers to: A, B, C, D
        """
        available_speakers = list(
            self.speaker_embeddings.keys()
        )

        if len(available_speakers) < 4:
            raise RuntimeError(
                "At least 4 distinct speaker embeddings "
                "are required."
            )

        selected_speakers = random.sample(
            available_speakers,
            4,
        )

        return {
            "A": self.speaker_embeddings[selected_speakers[0]],
            "B": self.speaker_embeddings[selected_speakers[1]],
            "C": self.speaker_embeddings[selected_speakers[2]],
            "D": self.speaker_embeddings[selected_speakers[3]],
        }

    def _generate_speech_sync(
        self,
        text: str,
        speaker_embedding: torch.Tensor,
    ) -> bytes:
        """
        Synchronous core for generating speech to avoid blocking the event loop.
        """
        inputs = self.processor(
            text=text,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"].to(self.device)
        speaker_embedding = speaker_embedding.to(self.device)

        with torch.no_grad():
            speech = self.model.generate_speech(
                input_ids,
                speaker_embedding,
                vocoder=self.vocoder,
            )

        speech = speech.cpu().numpy()
        buffer = io.BytesIO()
        sf.write(
            buffer,
            speech,
            samplerate=self.SAMPLE_RATE,
            format="WAV",
        )
        buffer.seek(0)
        
        return buffer.getvalue()

    async def generate_speech(
        self,
        text: str,
        speaker_embedding: torch.Tensor,
    ) -> bytes:
        """
        Convert text into WAV audio bytes asynchronously.
        """
        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )
            
        if len(text) > 600:
            raise ValueError(
                "Text exceeds the maximum length of 600 characters for SpeechT5 generation."
            )

        return await asyncio.to_thread(
            self._generate_speech_sync, 
            text, 
            speaker_embedding
        )


tts_service = TTSService()