import { useState, useRef, useCallback } from 'react';
import { API_BASE_URL } from '@/lib/config';

export function useVoiceHandoff(onSpeechDetected) {
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);

  // Play a gentle "bloop" sound when mic closes due to silence
  const playGracefulCloseCue = useCallback(() => {
    try {
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
    } catch (e) {
      console.warn("AudioContext not supported for bloop cue");
    }
  }, []);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current) {
      try {
        mediaRecorderRef.current.abort(); // aborts the SpeechRecognition instance
      } catch (e) {
        console.error(e);
      }
    }
    setIsListening(false);
  }, []);

  const startEightSecondListeningLoop = useCallback(async (onSpeechRecognized) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error("[ATLAS Mic] Speech Recognition API is not supported in this browser.");
      alert("Voice mode requires a browser that supports the Web Speech API (like Chrome or Safari).");
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      mediaRecorderRef.current = recognition; // Reusing the ref to hold the recognition instance
      
      recognition.lang = 'en-US';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        console.log('[ATLAS Mic] Microphone OPEN. Listening for speech...');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('[ATLAS Mic] Speech detected:', transcript);
        if (onSpeechRecognized) {
          onSpeechRecognized(transcript);
        }
      };

      recognition.onspeechend = () => {
        recognition.stop();
      };

      recognition.onend = () => {
        setIsListening(false);
        playGracefulCloseCue();
      };

      recognition.onerror = (event) => {
        console.error('[ATLAS Mic] Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.start();

    } catch (err) {
      console.error('[ATLAS Mic] Error initializing Speech Recognition:', err);
      setIsListening(false);
    }
  }, [playGracefulCloseCue]);

  const speakAtlasResponse = useCallback(async (text, agentRole = '', messageType = 'general', urgency = 'normal') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tts/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, agent_role: agentRole, message_type: messageType, urgency })
      });

      if (!response.ok) throw new Error('TTS Failed');

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        console.log('[ATLAS TTS] Playback finished.');
      };

      await audio.play();
    } catch (error) {
      console.error('[ATLAS TTS] Error playing audio:', error);
    }
  }, [startEightSecondListeningLoop]);

  return {
    isListening,
    startEightSecondListeningLoop,
    stopListening,
    speakAtlasResponse
  };
}
