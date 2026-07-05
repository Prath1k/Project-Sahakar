import { useState, useRef, useCallback } from 'react';
const API_BASE_URL = 'http://localhost:5001';

/**
 * Strip markdown formatting symbols before passing to TTS.
 * Prevents voice from reading "hashtag hashtag" or "asterisk asterisk bold asterisk asterisk" etc.
 */
function cleanTextForSpeech(text) {
  return text
    // Remove [DOC: ...] RAG context prefixes
    .replace(/\[DOC:[^\]]*\]/gi, '')
    // Remove atlas_artifact XML tags
    .replace(/<\/?atlas_artifact[^>]*>/gi, '')
    // Remove markdown headings (#, ##, ###)
    .replace(/#{1,6}\s+/g, '')
    // Remove bold/italic (**text**, *text*, __text__, _text_)
    .replace(/(\*{1,3}|_{1,3})(.*?)\1/g, '$2')
    // Remove inline code (`code`)
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    // Remove markdown links [text](url)
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    // Remove blockquote markers
    .replace(/^>\s+/gm, '')
    // Remove horizontal rules
    .replace(/^---+$/gm, '')
    // Remove bullet/numbered list markers
    .replace(/^[\s]*[-*+]\s+/gm, '')
    .replace(/^[\s]*\d+\.\s+/gm, '')
    // Collapse multiple newlines
    .replace(/\n{3,}/g, '\n\n')
    // Trim result
    .trim();
}

export function useVoiceHandoff(onSpeechDetected) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef(null);
  const currentAudioRef = useRef(null); // Track active Audio object for interruption

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

  /**
   * Stop any currently playing audio immediately.
   * Called at the start of every new user message.
   */
  const stopCurrentSpeech = useCallback(() => {
    if (currentAudioRef.current) {
      try {
        currentAudioRef.current.pause();
        currentAudioRef.current.src = '';
        currentAudioRef.current = null;
      } catch (e) {
        // ignore
      }
      setIsSpeaking(false);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current) {
      try {
        mediaRecorderRef.current.abort();
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
      mediaRecorderRef.current = recognition;
      
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
    // Cancel any currently playing audio before starting new one
    stopCurrentSpeech();

    // Clean text: remove markdown, [DOC:...] prefixes, code blocks, etc.
    const cleanText = cleanTextForSpeech(text);
    if (!cleanText || cleanText.length < 3) return;

    try {
      setIsSpeaking(true);
      const response = await fetch(`${API_BASE_URL}/api/tts/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText, agent_role: agentRole, message_type: messageType, urgency })
      });

      if (!response.ok) throw new Error('TTS Failed');

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      currentAudioRef.current = audio; // Track this audio for future interruption

      audio.onended = () => {
        console.log('[ATLAS TTS] Playback finished.');
        currentAudioRef.current = null;
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl); // Clean up memory
      };

      audio.onerror = () => {
        currentAudioRef.current = null;
        setIsSpeaking(false);
      };

      await audio.play();
    } catch (error) {
      console.error('[ATLAS TTS] Error playing audio:', error);
      currentAudioRef.current = null;
      setIsSpeaking(false);
    }
  }, [stopCurrentSpeech]);

  return {
    isListening,
    isSpeaking,
    startEightSecondListeningLoop,
    stopListening,
    stopCurrentSpeech,
    speakAtlasResponse
  };
}
