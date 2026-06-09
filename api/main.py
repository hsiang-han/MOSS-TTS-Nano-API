import io
import os
import struct
import tempfile
import threading
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

MODEL_ID = os.getenv("MODEL_ID", "OpenMOSS-Team/MOSS-TTS-Nano-100M")
DEVICE = os.getenv("DEVICE", "auto")
DTYPE = os.getenv("DTYPE", "auto")
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "zh_1")

# Map OpenAI standard voice names to MOSS presets
OPENAI_VOICE_MAP = {
    "alloy": "en_1",
    "echo": "en_2",
    "fable": "en_3",
    "onyx": "en_4",
    "nova": "en_5",
    "shimmer": "zh_1",
}

_service = None
_model_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _service
    from moss_tts_nano_runtime import NanoTTSService

    _service = NanoTTSService(
        checkpoint_path=MODEL_ID,
        device=DEVICE,
        dtype=DTYPE,
    )
    yield
    _service = None


app = FastAPI(title="MOSS-TTS-Nano-API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok" if _service else "loading",
        "model": MODEL_ID,
        "device": DEVICE,
        "default_voice": DEFAULT_VOICE,
    }


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "owned_by": "OpenMOSS",
            }
        ],
    }


@app.get("/v1/voices")
async def list_voices():
    if not _service:
        return {"voices": []}
    voices = [name for name in _service.voice_presets.keys()]
    return {"voices": voices}


class SpeechRequest(BaseModel):
    model: Optional[str] = None
    input: str
    voice: str = Field(default="", description="Voice preset name (e.g. zh_1, en_1). Empty = use DEFAULT_VOICE")
    language: Optional[str] = Field(default=None, description="Not used (voice determines language)")
    response_format: str = "wav"
    speed: float = Field(default=1.0, description="Accepted for OpenAI compatibility but not applied")


@app.post("/v1/audio/speech")
async def text_to_speech(req: SpeechRequest):
    if not _service:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not req.input.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    voice = req.voice if req.voice else DEFAULT_VOICE
    voice = OPENAI_VOICE_MAP.get(voice, voice)

    with _model_lock:
        result = _service.synthesize(
            text=req.input,
            voice=voice,
            mode="voice_clone",
        )

    audio = result["waveform_numpy"]
    sr = result["sample_rate"]

    if req.response_format == "pcm":
        return Response(content=_to_pcm16(audio), media_type="audio/pcm")
    return Response(content=_to_wav(audio, sr), media_type="audio/wav")


@app.post("/v1/audio/speech/clone")
async def clone_speech(
    input: str = Form(...),
    ref_audio: UploadFile = File(...),
    voice: str = Form(default=""),
):
    if not _service:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not input.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    audio_bytes = await ref_audio.read()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with _model_lock:
            result = _service.synthesize(
                text=input,
                voice=voice if voice else None,
                mode="voice_clone",
                prompt_audio_path=tmp_path,
            )
    finally:
        os.unlink(tmp_path)

    audio = result["waveform_numpy"]
    sr = result["sample_rate"]
    return Response(content=_to_wav(audio, sr), media_type="audio/wav")


def _to_pcm16(audio: np.ndarray) -> bytes:
    return np.clip(audio * 32768, -32768, 32767).astype(np.int16).tobytes()


def _to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
    if audio.ndim == 1:
        raw = _to_pcm16(audio)
        n_channels = 1
    else:
        raw = _to_pcm16(audio.T.flatten() if audio.shape[0] == 2 else audio.flatten())
        n_channels = audio.shape[0] if audio.shape[0] <= 2 else 1

    bits = 16
    byte_rate = sample_rate * n_channels * bits // 8
    block_align = n_channels * bits // 8

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + len(raw)))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, n_channels, sample_rate, byte_rate, block_align, bits))
    buf.write(b"data")
    buf.write(struct.pack("<I", len(raw)))
    buf.write(raw)
    return buf.getvalue()
