import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env
root_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(root_dir / ".env")

# Add backend/app to path
sys.path.append(str(Path(__file__).resolve().parent))
from stt_service import STTService

async def test_stt():
    print("===========================================================================")
    print("SCAAR DUAL-TIER SPEECH-TO-TEXT (STT) & EARS VERIFICATION")
    print("===========================================================================")
    
    wav_path = Path(__file__).resolve().parent / "turn1_reply.wav"
    if not wav_path.exists():
        print(f"[ERROR] Could not find test audio file: {wav_path}")
        return
        
    audio_bytes = wav_path.read_bytes()
    print(f"[STEP 1] Loaded audio recording '{wav_path.name}' ({len(audio_bytes):,} bytes)...")
    
    print("[STEP 2] Transcribing audio through SCAAR STT Engine...")
    text, provider, latency = await STTService.transcribe_audio(audio_bytes, filename="turn1_reply.wav")
    
    print("\n---------------------------------------------------------------------------")
    print(f"[STT RESULT]: \"{text}\"")
    print(f"[PROVIDER]:   {provider}")
    print(f"[LATENCY]:    {latency:.1f} ms")
    print("---------------------------------------------------------------------------\n")
    
    if "TITAN" in text.upper() or "SAHAKAR" in text.upper() or "CENTRAL" in text.upper():
        print("[SUCCESS] STT Engine accurately transcribed spoken words from audio!")
    else:
        print("[NOTICE] Transcription returned different text or fallback used.")
        
    print("===========================================================================\n")

if __name__ == "__main__":
    asyncio.run(test_stt())
