#!/usr/bin/env python3
"""
test_voice_model.py — Comprehensive Test Suite for ATLAS Voice & TTS Architecture

This automated test suite verifies:
  1. PyTorch Custom 80/20 Voice Blending (tensor math, shape integrity, NaN/Inf checks).
  2. Dynamic Voice Router (context, persona, and urgency classification accuracy).
  3. Acoustic TTS Synthesis (WAV header validation, sample rate verification, audio file export).
  4. 8-Second Conversational Handoff Loop (speech detection vs. silence timeout behavior).
"""

import os
import sys
import time
import wave
import asyncio
import logging
from pathlib import Path

# Configure clean test logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [VoiceTest] %(message)s")
logger = logging.getLogger("VoiceTest")

try:
    import torch
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def test_1_pytorch_voice_blending():
    logger.info("====================================================================")
    logger.info("TEST 1: PYTORCH 80/20 CUSTOM VOICE BLENDING ENGINE")
    logger.info("====================================================================")
    
    if not TORCH_AVAILABLE:
        logger.error("❌ PyTorch is not available. Cannot test tensor blending.")
        return False
        
    from blend_voices import blend_voice_tensors, load_tensor_safe
    
    voice_dir = Path("voices")
    voice_dir.mkdir(exist_ok=True)
    
    jessica_path = voice_dir / "jessica.pt"
    sarah_path = voice_dir / "sarah.pt"
    custom_path = voice_dir / "custom_blend.pt"
    
    # 1. Execute blend
    start_t = time.perf_counter()
    blended_tensor = blend_voice_tensors(
        voice_a_path=jessica_path,
        voice_b_path=sarah_path,
        output_path=custom_path,
        weight_a=0.8,
        weight_b=0.2,
        create_mock_if_missing=True
    )
    elapsed_ms = (time.perf_counter() - start_t) * 1000
    
    # 2. Verify tensor properties
    jessica = load_tensor_safe(jessica_path)
    sarah = load_tensor_safe(sarah_path)
    
    assert blended_tensor.shape == jessica.shape == sarah.shape, "Shape mismatch between blended and base tensors!"
    assert blended_tensor.dtype == torch.float32, f"Expected float32 dtype, got {blended_tensor.dtype}"
    assert not torch.isnan(blended_tensor).any(), "Blended tensor contains NaN values!"
    assert not torch.isinf(blended_tensor).any(), "Blended tensor contains Inf values!"
    
    # 3. Verify mathematical accuracy: check if (jessica*0.8 + sarah*0.2) == blended_tensor
    expected_tensor = (jessica * 0.8) + (sarah * 0.2)
    max_diff = torch.max(torch.abs(blended_tensor - expected_tensor)).item()
    assert max_diff < 1e-6, f"Mathematical blend deviation exceeded threshold: {max_diff}"
    
    logger.info(f"✅ TEST 1 PASSED | Shape: {list(blended_tensor.shape)} | Dtype: {blended_tensor.dtype}")
    logger.info(f"   Max Mathematical Deviation: {max_diff:.8f} (Exact 80/20 linear combination verified)")
    logger.info(f"   Blending Latency: {elapsed_ms:.2f} ms | Saved to: '{custom_path.resolve()}'\n")
    return True


def test_2_dynamic_voice_routing():
    logger.info("====================================================================")
    logger.info("TEST 2: DYNAMIC VOICE ROUTER CLASSIFICATION ACCURACY")
    logger.info("====================================================================")
    
    from voice_service import VoiceRouter, DEFAULT_VOICE_BLEND, ANALYTICAL_VOICE, COACHING_VOICE
    
    test_cases = [
        # (text, role, msg_type, urgency, persona, expected_voice, expected_category)
        (
            "Hello, how can I help you today?",
            "GeneralAssistant", "general", "normal", "",
            DEFAULT_VOICE_BLEND, "Default / Conversational / General Assistance"
        ),
        (
            "I audited your SQL query and found an unindexed JOIN causing severe bottleneck.",
            "CareerArchitect", "code_review", "normal", "devils_advocate",
            ANALYTICAL_VOICE, "Analytical / Code Review / Devil's Advocate"
        ),
        (
            "ALERT: Multiple failed authentication attempts from IP 192.168.1.105!",
            "FiscalSentinel", "security", "critical", "",
            ANALYTICAL_VOICE, "System Alerts / Security Warnings"
        ),
        (
            "Great progress on your physics flashcards! Let's do one more review session.",
            "ScholarCore", "onboarding", "normal", "coaching",
            COACHING_VOICE, "Coaching / Encouragement / Onboarding"
        )
    ]
    
    all_passed = True
    for idx, (txt, role, mtype, urg, pers, exp_voice, exp_cat) in enumerate(test_cases, 1):
        decision = VoiceRouter.get_voice_profile(text=txt, agent_role=role, message_type=mtype, urgency=urg, persona_mode=pers)
        
        match_voice = (decision.assigned_voice == exp_voice)
        match_cat = (decision.category == exp_cat)
        
        if match_voice and match_cat:
            logger.info(f"✅ Route Test {idx} PASSED | Assigned: '{decision.assigned_voice}' ({decision.profile_name}) | Latency: {decision.latency_ms:.3f}ms")
        else:
            logger.error(f"❌ Route Test {idx} FAILED | Expected '{exp_voice}' ({exp_cat}), got '{decision.assigned_voice}' ({decision.category})")
            all_passed = False
            
    logger.info(f"✅ TEST 2 COMPLETED | Result: {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}\n")
    return all_passed


async def test_3_tts_synthesis_and_wav_export():
    logger.info("====================================================================")
    logger.info("TEST 3: ACOUSTIC TTS SYNTHESIS & WAV HEADER VALIDATION")
    logger.info("====================================================================")
    
    from voice_service import KokoroTTSService, VoiceRouter
    
    out_dir = Path("test_audio_output")
    out_dir.mkdir(exist_ok=True)
    
    scenarios = [
        ("default_blend.wav", "Welcome to Project Sahakar ATLAS. All core memory engines and autonomous containers are online.", "", "general", "normal"),
        ("analytical_sarah.wav", "Code review complete. The authentication middleware requires rate limiting to prevent brute force attacks.", "CareerArchitect", "code_review", "normal"),
        ("security_alert.wav", "CRITICAL WARNING: Unauthorized container breakout attempt intercepted. E2B microVM terminated.", "FiscalSentinel", "alert", "critical"),
        ("coaching_jessica.wav", "Congratulations on completing your study milestone! You are mastering this material faster than average.", "ScholarCore", "coaching", "normal")
    ]
    
    all_passed = True
    for filename, text, role, mtype, urg in scenarios:
        route = VoiceRouter.get_voice_profile(text=text, agent_role=role, message_type=mtype, urgency=urg)
        audio_bytes, is_gpu, latency = await KokoroTTSService.synthesize_audio(text=text, voice=route.assigned_voice)
        
        out_path = out_dir / filename
        out_path.write_bytes(audio_bytes)
        
        # Validate WAV Header Integrity
        try:
            with wave.open(str(out_path), "rb") as wf:
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                nframes = wf.getnframes()
                duration = nframes / float(framerate)
                
            assert channels == 1, f"Expected mono audio (1 channel), got {channels}"
            assert sampwidth == 2, f"Expected 16-bit audio (2 bytes), got {sampwidth}"
            assert framerate == 24000, f"Expected 24000 Hz sample rate, got {framerate}"
            assert duration > 0.5, f"Audio duration too short: {duration:.2f}s"
            
            source_tag = "Kokoro-GPU-FastAPI" if is_gpu else "Local-Acoustic-Fallback"
            logger.info(f"✅ Audio Exported: '{out_path}' | Size: {len(audio_bytes):,} bytes | Duration: {duration:.2f}s | Source: {source_tag} | Latency: {latency:.1f}ms")
            logger.info(f"   WAV Header Verified: {framerate}Hz, 16-bit Mono ({nframes:,} samples)")
        except Exception as e:
            logger.error(f"❌ WAV Header Validation Failed for '{filename}': {e}")
            all_passed = False
            
    logger.info(f"✅ TEST 3 COMPLETED | Audio files saved to '{out_dir.resolve()}'\n")
    return all_passed


async def test_4_eight_second_handoff_loop():
    logger.info("====================================================================")
    logger.info("TEST 4: 8-SECOND CONVERSATIONAL HANDOFF LOOP BEHAVIOR")
    logger.info("====================================================================")
    
    from voice_integration_example import SimulatedAudioPlayer
    
    logger.info("--- Sub-test A: Speech Detected within Window (at 2.0s) ---")
    start_t = time.perf_counter()
    speech_detected = await SimulatedAudioPlayer.run_8sec_handoff_loop(simulate_user_speech=True, speech_delay_sec=2.0)
    elapsed_a = time.perf_counter() - start_t
    
    assert speech_detected is True, "Expected speech detection to return True"
    assert 1.8 <= elapsed_a <= 3.5, f"Expected loop to close around 2.0s upon speech, took {elapsed_a:.2f}s"
    logger.info(f"✅ Sub-test A PASSED | Speech detected and mic closed in {elapsed_a:.2f}s (No wake word needed!)\n")
    
    logger.info("--- Sub-test B: Silence Timeout (8.0s listening window) ---")
    start_t = time.perf_counter()
    speech_detected = await SimulatedAudioPlayer.run_8sec_handoff_loop(simulate_user_speech=False)
    elapsed_b = time.perf_counter() - start_t
    
    assert speech_detected is False, "Expected silence timeout to return False"
    assert 7.8 <= elapsed_b <= 9.0, f"Expected loop to time out at 8.0s, took {elapsed_b:.2f}s"
    logger.info(f"✅ Sub-test B PASSED | 8.0s silence elapsed -> played acoustic bloop -> mic closed gracefully in {elapsed_b:.2f}s\n")
    return True


async def main():
    logger.info("🚀 STARTING ATLAS VOICE & TTS ARCHITECTURE VERIFICATION SUITE\n")
    
    t1 = test_1_pytorch_voice_blending()
    t2 = test_2_dynamic_voice_routing()
    t3 = await test_3_tts_synthesis_and_wav_export()
    t4 = await test_4_eight_second_handoff_loop()
    
    logger.info("====================================================================")
    logger.info("FINAL TEST SUITE SUMMARY")
    logger.info("====================================================================")
    logger.info(f"  [1] PyTorch Custom 80/20 Voice Blending : {'✅ PASSED' if t1 else '❌ FAILED'}")
    logger.info(f"  [2] Dynamic Voice Router Accuracy       : {'✅ PASSED' if t2 else '❌ FAILED'}")
    logger.info(f"  [3] Acoustic TTS Synthesis & WAV Export : {'✅ PASSED' if t3 else '❌ FAILED'}")
    logger.info(f"  [4] 8-Second Conversational Handoff Loop: {'✅ PASSED' if t4 else '❌ FAILED'}")
    logger.info("====================================================================")
    
    if all([t1, t2, t3, t4]):
        logger.info("🎉 ALL TESTS PASSED 100%! The ATLAS Voice System is ready for live deployment.")
        sys.exit(0)
    else:
        logger.error("⚠️ SOME TESTS FAILED. Please review logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
