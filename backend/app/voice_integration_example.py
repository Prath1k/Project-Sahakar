#!/usr/bin/env python3
"""
voice_integration_example.py — ATLAS Voice Service Integration & 8-Second Handoff Loop

This script demonstrates how to integrate the Kokoro TTS Voice Service and
Dynamic Voice Router into our backend chat handlers and frontend interfaces.

Key Features Demonstrated:
  1. Backend API Calling: Requesting dynamic voice routing and synthesized audio
     from `/api/tts/speak` based on persona, context, and urgency.
  2. The 8-Second Conversational Handoff Loop:
     - After TTS audio playback completes, the microphone automatically opens
       for an 8-second listening window without requiring a wake word.
     - If speech is detected within 8 seconds, the turn is processed immediately.
     - If 8 seconds of silence elapse, the microphone closes gracefully with an audio cue ("bloop").
  3. Frontend Web Integration Reference: Complete JavaScript / React implementation
     guide for web browser audio playback and microphone listening loops.

========================================================================================
FRONTEND WEB INTEGRATION REFERENCE (React / Next.js / Vanilla JS)
========================================================================================
```javascript
// 1. Call ATLAS TTS API with dynamic routing metadata
async function speakAtlasResponse(text, agentRole, messageType, urgency) {
  const response = await fetch('/api/tts/speak', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      agent_role: agentRole,
      message_type: messageType,
      urgency: urgency
    })
  });

  // Extract routing decisions from custom headers
  const assignedVoice = response.headers.get('X-Assigned-Voice');
  const voiceReason = response.headers.get('X-Voice-Reason');
  console.log(`[ATLAS TTS] Routed to: ${assignedVoice} | Reason: ${voiceReason}`);

  // Play synthesized audio
  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);

  audio.onended = () => {
    console.log('[ATLAS TTS] Playback finished. Initiating 8-Second Conversational Handoff Loop...');
    startEightSecondListeningLoop();
  };

  audio.play();
}

// 2. The 8-Second Conversational Handoff Loop (No Wake Word Required)
let listeningTimer = null;
let mediaRecorder = null;

async function startEightSecondListeningLoop() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
    
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop());
      clearTimeout(listeningTimer);
      
      if (audioChunks.length > 0) {
        console.log('[ATLAS Mic] Speech detected! Sending to Whisper STT...');
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        // Send audioBlob to backend STT endpoint...
      }
    };

    mediaRecorder.start();
    console.log('[ATLAS Mic] Microphone OPEN. Listening for 8 seconds...');

    // Set 8-Second Silence Timeout
    listeningTimer = setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        console.log('[ATLAS Mic] 8 seconds of silence elapsed. Closing mic gracefully.');
        mediaRecorder.stop();
        playGracefulCloseCue(); // Play gentle "bloop" audio cue
      }
    }, 8000);

    // Optional: Use Web Audio API AnalyserNode to detect speech threshold
    // and reset or trigger turn processing early when speech ends.
  } catch (err) {
    console.error('[ATLAS Mic] Microphone access denied or error:', err);
  }
}

function playGracefulCloseCue() {
  // Play gentle acoustic bloop indicating mic closure
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(440, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(220, ctx.currentTime + 0.15);
  gain.gain.setValueAtTime(0.1, ctx.currentTime);
  gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.15);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + 0.15);
}
```
========================================================================================
"""

import time
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [VoiceDemo] %(message)s")
logger = logging.getLogger("VoiceDemo")


class SimulatedAudioPlayer:
    """Simulates client-side audio playback and microphone interaction for testing."""
    
    @staticmethod
    async def play_audio(audio_bytes: bytes, profile_name: str, latency_ms: str):
        logger.info(f"▶️ PLAYING AUDIO ({len(audio_bytes)} bytes) | Voice: {profile_name} | Latency: {latency_ms}ms")
        # Simulate playback time based on file size (approx 24kB/sec for 24kHz 16-bit mono)
        duration_est = max(1.0, min(5.0, len(audio_bytes) / 48000.0))
        await asyncio.sleep(duration_est)
        logger.info("⏹️ AUDIO PLAYBACK COMPLETED.")

    @staticmethod
    async def run_8sec_handoff_loop(simulate_user_speech: bool = False, speech_delay_sec: float = 3.0):
        """
        Simulates the 8-Second Conversational Handoff Loop.
        """
        logger.info("🎙️ [HANDOFF LOOP] Microphone automatically OPENED for 8-second listening window (No wake word required).")
        
        start_listen = time.perf_counter()
        timeout_sec = 8.0
        
        while (time.perf_counter() - start_listen) < timeout_sec:
            elapsed = time.perf_counter() - start_listen
            if simulate_user_speech and elapsed >= speech_delay_sec:
                logger.info(f"🗣️ [HANDOFF LOOP] Speech detected at {elapsed:.1f}s! Processing turn immediately.")
                logger.info("🔒 [HANDOFF LOOP] Microphone closed -> Transitioning to STT / LLM processing.")
                return True
            await asyncio.sleep(0.5)
            logger.info(f"  ... listening ({elapsed:.1f}s / {timeout_sec:.1f}s) ...")
            
        logger.info("⏳ [HANDOFF LOOP] 8 seconds of silence elapsed without speech.")
        logger.info("🔔 [HANDOFF LOOP] Playing graceful audio cue ('bloop') & closing microphone.")
        return False


async def demonstrate_voice_routing_and_handoff():
    """
    Runs a full end-to-end simulation of ATLAS dynamic voice routing across
    different personas and urgency levels, followed by the 8-second handoff loop.
    """
    try:
        from voice_service import VoiceRouter, KokoroTTSService
    except ImportError:
        logger.error("Could not import voice_service. Please run from the server directory.")
        return

    test_cases = [
        {
            "title": "Scenario 1: Default General Assistance Mode",
            "text": "Hello Sricharan! I am ATLAS, your autonomous AI assistant. All systems are operational.",
            "agent_role": "GeneralAssistant",
            "message_type": "general",
            "urgency": "normal",
            "simulate_speech": True,
            "speech_delay": 2.5
        },
        {
            "title": "Scenario 2: Analytical Code Review / Devil's Advocate Mode",
            "text": "I reviewed your authentication logic in parameter_extractor.py. There is a potential timing attack vulnerability on line 142.",
            "agent_role": "CareerArchitect",
            "message_type": "code_review",
            "urgency": "normal",
            "persona_mode": "devils_advocate",
            "simulate_speech": False
        },
        {
            "title": "Scenario 3: High Urgency System Alert / Security Warning",
            "text": "ALERT: Unauthorized access attempt detected on database endpoint! Engaging E2B sandbox isolation protocol immediately.",
            "agent_role": "FiscalSentinel",
            "message_type": "security",
            "urgency": "critical",
            "simulate_speech": False
        },
        {
            "title": "Scenario 4: Coaching & Onboarding Mode",
            "text": "Welcome to ATLAS! You did a fantastic job completing the study schedule today. Let's review your flashcards.",
            "agent_role": "ScholarCore",
            "message_type": "onboarding",
            "urgency": "normal",
            "simulate_speech": True,
            "speech_delay": 4.0
        }
    ]

    logger.info("====================================================================")
    logger.info("STARTING ATLAS VOICE SERVICE & 8-SEC HANDOFF LOOP INTEGRATION DEMO")
    logger.info("====================================================================")

    for idx, tc in enumerate(test_cases, 1):
        logger.info(f"\n--- {tc['title']} ---")
        logger.info(f"Input Text   : \"{tc['text']}\"")
        logger.info(f"Metadata     : role='{tc.get('agent_role')}', type='{tc.get('message_type')}', urgency='{tc.get('urgency')}', persona='{tc.get('persona_mode', '')}'")
        
        # 1. Dynamic Routing
        route = VoiceRouter.get_voice_profile(
            text=tc["text"],
            agent_role=tc.get("agent_role", ""),
            message_type=tc.get("message_type", ""),
            urgency=tc.get("urgency", ""),
            persona_mode=tc.get("persona_mode", "")
        )
        logger.info(f"✅ ROUTING DECISION: Assigned Voice -> '{route.assigned_voice}' ({route.profile_name})")
        logger.info(f"   Reason: {route.reason}")
        
        # 2. Synthesize Audio
        audio_bytes, is_gpu, synth_latency = await KokoroTTSService.synthesize_audio(
            text=tc["text"],
            voice=route.assigned_voice
        )
        total_latency = round(route.latency_ms + synth_latency, 2)
        source_str = "Kokoro-GPU-FastAPI" if is_gpu else "Local-Acoustic-Fallback"
        
        # 3. Simulate Client Playback & 8-Second Handoff Loop
        await SimulatedAudioPlayer.play_audio(audio_bytes, route.profile_name, str(total_latency))
        await SimulatedAudioPlayer.run_8sec_handoff_loop(
            simulate_user_speech=tc["simulate_speech"],
            speech_delay_sec=tc.get("speech_delay", 3.0)
        )
        logger.info("--------------------------------------------------------------------")
        await asyncio.sleep(1.0)

    logger.info("\n✅ INTEGRATION DEMO COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    asyncio.run(demonstrate_voice_routing_and_handoff())
