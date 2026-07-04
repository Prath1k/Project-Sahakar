import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from '../Input/ChatInput';
import { useVoiceHandoff } from '../../hooks/useVoiceHandoff';
import { GlyphMatrix } from "@/components/ui/glyph-matrix";
import './ChatInterface.css';

const ChatInterface = ({ onOpenArtifact }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I am your autonomous task and learning assistant. How can I help you today?', sender: 'ai' }
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
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
      // Send request to actual backend
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt: text || "Please describe this image.",
          has_image: !!imageBase64,
          image_base64: imageBase64,
          override_model: model !== 'Auto' ? model : null
        })
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

      // Only play TTS response if Voice Mode is explicitly toggled ON
      if (isVoiceMode) {
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
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onOpenArtifact={() => msg.hasArtifact && onOpenArtifact({ title: 'Generated Plan', content: '# Sample Plan' })}
            onRetry={handleRetry}
          />
        ))}
        {isGenerating && (
          <div className="border-border bg-background h-[400px] w-full overflow-hidden rounded-lg border mt-4 mb-4">
            <GlyphMatrix />
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
