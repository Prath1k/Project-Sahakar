import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from '../Input/ChatInput';
import { useVoiceHandoff } from '../../hooks/useVoiceHandoff';
import { GlyphMatrix } from "@/components/ui/glyph-matrix";
import './ChatInterface.css';

const ChatInterface = ({ onOpenArtifact, activeAgent }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I am your autonomous task and learning assistant. How can I help you today?', sender: 'ai' }
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isAutoSpeak, setIsAutoSpeak] = useState(true);
  const messagesEndRef = useRef(null);
  
  const { isListening, startEightSecondListeningLoop, stopListening, speakAtlasResponse } = useVoiceHandoff();

  const handleToggleVoiceMode = () => {
    setIsVoiceMode(prev => {
      const newState = !prev;
      if (newState) {
        // Pass a callback to automatically send the transcribed text
        startEightSecondListeningLoop((transcribedText) => {
          handleSendMessage(transcribedText);
          setIsVoiceMode(false); // turn off voice mode after one successful recognition
        });
      } else {
        stopListening();
      }
      return newState;
    });
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleRetry = async (messageId) => {
    const index = messages.findIndex(m => m.id === messageId);
    if (index > 0) {
      const prevMsg = messages[index - 1];
      if (prevMsg.sender === 'user') {
        const availableModels = ['Groq', 'SambaNova', 'Cerebras'];
        const randomModel = availableModels[Math.floor(Math.random() * availableModels.length)];
        
        // Remove the current AI message and the preceding User message from the UI
        setMessages(prev => prev.slice(0, index - 1));
        
        // Resend the message with the randomly selected alternative model
        handleSendMessage(prevMsg.text, randomModel, prevMsg.imageBase64);
      }
    }
  };

  const handleSendMessage = async (text, model, imageBase64 = null) => {
    if (!text.trim() && !imageBase64) return;

    const newUserMsg = { 
      id: Date.now(), 
      text: text || "Attached an image.", 
      sender: 'user',
      hasImage: !!imageBase64,
      imageBase64
    };
    setMessages(prev => [...prev, newUserMsg]);
    setIsGenerating(true);

    try {
      const endpoint = activeAgent && activeAgent.id ? '/agent/chat' : '/chat';
      const bodyPayload = activeAgent && activeAgent.id ? {
        agent_id: activeAgent.id,
        prompt: text || "Please describe this image.",
        has_image: !!imageBase64,
        image_base64: imageBase64
      } : {
        prompt: text || "Please describe this image.",
        has_image: !!imageBase64,
        image_base64: imageBase64,
        override_model: model !== 'Auto' ? model : null
      };

      // Send request to actual backend
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload)
      });
      
      const data = await res.json();
      
      // Delay the response by 0.5 seconds to show the animation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      let responseText = data.response || "No response received.";
      
      // Parse artifact if present
      const artifactMatch = responseText.match(/<atlas_artifact[^>]*>([\s\S]*?)<\/atlas_artifact>/i);
      let artifactContent = null;
      if (artifactMatch) {
        artifactContent = artifactMatch[1].trim();
        // Remove artifact from main chat text
        responseText = responseText.replace(artifactMatch[0], '').trim();
      }

      const newAiMsg = { 
        id: Date.now() + 1, 
        text: responseText, 
        sender: 'ai',
        modelInfo: data.model_used || model,
        hasArtifact: !!artifactContent
      };
      
      setMessages(prev => [...prev, newAiMsg]);
      setIsGenerating(false);

      if (artifactContent) {
        onOpenArtifact({ title: 'Generated Artifact', content: artifactContent });
      }

      // Play TTS response if Auto-Speak OR Voice Mode is toggled ON
      if (isVoiceMode || isAutoSpeak) {
        speakAtlasResponse(responseText);
      }

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { 
        id: Date.now() + 1, 
        text: 'Error connecting to the backend API.', 
        sender: 'ai' 
      }]);
      setIsGenerating(false);
    }
  };

  return (
    <div className="chat-interface">
      <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--bg-main)' }}>
        <button 
          onClick={() => setIsAutoSpeak(!isAutoSpeak)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: '600',
            border: '1px solid var(--border)',
            background: isAutoSpeak ? 'var(--primary)' : 'transparent',
            color: isAutoSpeak ? '#fff' : 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          title="Toggle automatic speech synthesis for AI responses"
        >
          <span>{isAutoSpeak ? '🔊' : '🔇'}</span>
          <span>Auto-Speak: {isAutoSpeak ? 'ON' : 'OFF'}</span>
        </button>
      </div>
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onOpenArtifact={() => msg.hasArtifact && onOpenArtifact({ title: 'Generated Plan', content: '# Sample Plan' })}
            onRetry={handleRetry}
            onSpeak={(text) => speakAtlasResponse(text)}
          />
        ))}
        {isGenerating && (
          <div className="message-row ai-row animate-bounce-in mt-2 mb-2">
            <div className="message-container">
              <div className="message-avatar">
                <img src="/logo.png" alt="AI" className="ai-avatar-img" />
              </div>
              <div className="message-content" style={{ display: 'flex', alignItems: 'center' }}>
                <div className="border-border h-[60px] w-[200px] overflow-hidden rounded-2xl border relative flex items-center justify-center opacity-80 shadow-lg" style={{ backgroundColor: 'var(--bubble-ai)' }}>
                  <GlyphMatrix color="rgba(150, 150, 150, 0.4)" />
                  <div className="absolute z-10 text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--text-main)', textShadow: '0 1px 2px rgba(0,0,0,0.8)' }}>
                    <div className="skeleton-pulse"></div> Generating...
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-wrapper">
        <ChatInput 
          onSendMessage={handleSendMessage} 
          disabled={isGenerating} 
          isListening={isVoiceMode}
          onMicClick={handleToggleVoiceMode}
        />
      </div>
    </div>
  );
};

export default ChatInterface;
