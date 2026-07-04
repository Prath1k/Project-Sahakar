import os
import time
import logging
import asyncio
from typing import Tuple, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx

logger = logging.getLogger("SCAAR.STT")

class STTService:
    """
    SCAAR Dual-Tier Speech-To-Text (STT) Engine & Ears Feature.
    Tier 1 (Primary): Groq Whisper API (whisper-large-v3-turbo) - Ultra-fast (<300ms), 100% Free.
    Tier 2 (Fallback): Local/Free SpeechRecognition Engine - Offline resilience.
    """
    
    GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    @classmethod
    async def transcribe_audio(
        cls, 
        audio_bytes: bytes, 
        filename: str = "input.wav",
        language: str = "en"
    ) -> Tuple[str, str, float]:
        """
        Transcribes audio bytes to text.
        Returns: (transcribed_text, provider_used, latency_ms)
        """
        start_time = time.perf_counter()
        groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_1") or os.getenv("GROQ_API_KEY_2")
        
        # ---------------------------------------------------------------------
        # Tier 1: Groq Whisper API (whisper-large-v3-turbo)
        # ---------------------------------------------------------------------
        if groq_key:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    logger.info(f"Requesting STT transcription from Groq Whisper API ({filename})...")
                    # Determine mime type
                    mime = "audio/mpeg" if (filename.endswith(".mp3") or len(audio_bytes) > 0 and audio_bytes[:2] == b'\xff\xfb') else "audio/wav"
                    files = {"file": ("audio.mp3" if mime == "audio/mpeg" else filename, audio_bytes, mime)}
                    data = {
                        "model": "whisper-large-v3-turbo",
                        "language": language,
                        "temperature": "0.0",
                        "response_format": "json"
                    }
                    headers = {"Authorization": f"Bearer {groq_key}"}
                    
                    res = await client.post(cls.GROQ_API_URL, headers=headers, files=files, data=data)
                    if res.status_code == 200:
                        text = res.json().get("text", "").strip()
                        latency = (time.perf_counter() - start_time) * 1000
                        logger.info(f"Groq Whisper STT Success | Text: '{text}' | Latency: {latency:.1f}ms")
                        return text, "groq_whisper_turbo", latency
                    else:
                        logger.warning(f"Groq Whisper returned status {res.status_code}: {res.text}. Engaging fallback STT.")
            except Exception as e:
                logger.warning(f"Groq Whisper API unreachable ({e}). Engaging fallback STT.")
        else:
            logger.info("No GROQ_API_KEY found. Engaging local STT fallback.")
            
        # ---------------------------------------------------------------------
        # Tier 2: Free Local/Offline SpeechRecognition Engine
        # ---------------------------------------------------------------------
        try:
            import speech_recognition as sr
            import tempfile
            
            temp_wav = os.path.join(tempfile.gettempdir(), f"atlas_stt_{os.getpid()}_{int(time.time()*1000)}.wav")
            with open(temp_wav, "wb") as f:
                f.write(audio_bytes)
                
            r = sr.Recognizer()
            with sr.AudioFile(temp_wav) as source:
                audio_data = r.record(source)
                
            try:
                os.remove(temp_wav)
            except Exception:
                pass
                
            # Uses Google Free Web Speech API (zero API key required, 100% free)
            text = r.recognize_google(audio_data, language=language)
            latency = (time.perf_counter() - start_time) * 1000
            logger.info(f"Local Fallback STT Success | Text: '{text}' | Latency: {latency:.1f}ms")
            return text, "local_speech_recognition", latency
            
        except Exception as fallback_err:
            latency = (time.perf_counter() - start_time) * 1000
            logger.error(f"All STT tiers failed: {fallback_err}")
            return "", "error", latency

# ---------------------------------------------------------------------------
# FastAPI Router Implementation
# ---------------------------------------------------------------------------
router = APIRouter()

@router.post("/v1/audio/transcribe", tags=["STT & Ears"])
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Endpoint for transcribing audio files (WAV/MP3/M4A) from microphone or client.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file provided.")
            
        text, provider, latency = await STTService.transcribe_audio(audio_bytes, filename=file.filename or "audio.wav")
        
        return {
            "success": True,
            "text": text,
            "provider": provider,
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        logger.error(f"STT endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
