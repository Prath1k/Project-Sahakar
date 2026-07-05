import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from '../Input/ChatInput';
import AgentBanner from './AgentBanner';
import { useVoiceHandoff } from '../../hooks/useVoiceHandoff';
import { API_BASE_URL } from '../../lib/config';
import { Volume2, VolumeX, RotateCcw } from 'lucide-react';
import './ChatInterface.css';

const DEFAULT_WELCOME = {
  id: 1,
  text: "Hello! I am your autonomous task and learning assistant. How can I help you today?",
  sender: 'ai',
  modelInfo: 'ATLAS'
};

const ChatInterface = ({ onOpenArtifact, activeAgent, loadedMessages, selectedModel }) => {
  const [messages, setMessages] = useState(() => loadedMessages || [DEFAULT_WELCOME]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isAutoSpeak, setIsAutoSpeak] = useState(false);
  const [currentSessionTitle, setCurrentSessionTitle] = useState('New Conversation');
  const messagesEndRef = useRef(null);
  
  const { isListening, stopListening, stopCurrentSpeech, speakAtlasResponse, startEightSecondListeningLoop } = useVoiceHandoff();

  useEffect(() => {
    if (loadedMessages && loadedMessages.length > 0) {
      setMessages(loadedMessages);
    }
  }, [loadedMessages]);

  useEffect(() => {
    if (messages.length > 1) {
      saveToHistory(messages);
    }
  }, [messages, activeAgent]);

  const saveToHistory = (msgs) => {
    try {
      const raw = localStorage.getItem('atlas_chat_history');
      let history = raw ? JSON.parse(raw) : [];
      
      const firstUserMsg = msgs.find(m => m.sender === 'user');
      const title = firstUserMsg ? firstUserMsg.text.slice(0, 42) + (firstUserMsg.text.length > 42 ? '...' : '') : 'Conversation';
      setCurrentSessionTitle(title);

      const sessionObj = {
        id: msgs[0]?.sessionId || Date.now(),
        title,
        timestamp: Date.now(),
        agentId: activeAgent?.id || null,
        messages: msgs
      };

      const index = history.findIndex(h => h.id === sessionObj.id);
      if (index >= 0) {
        history[index] = sessionObj;
      } else {
        history.unshift(sessionObj);
      }

      localStorage.setItem('atlas_chat_history', JSON.stringify(history.slice(0, 20)));
    } catch (e) {
      console.error('Failed to save chat history:', e);
    }
  };

  const handleToggleVoiceMode = () => {
    if (isListening) {
      stopListening();
    } else {
      startEightSecondListeningLoop((transcribedText) => {
        handleSendMessage(transcribedText, selectedModel || 'Auto');
      });
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleClearChat = () => {
    stopCurrentSpeech();
    setMessages([{ ...DEFAULT_WELCOME, id: Date.now() }]);
    setCurrentSessionTitle('New Conversation');
  };

  const handleRetry = async (messageId) => {
    const index = messages.findIndex(m => m.id === messageId);
    if (index > 0) {
      const prevMsg = messages[index - 1];
      if (prevMsg.sender === 'user') {
        const availableModels = ['Groq', 'SambaNova', 'Cerebras', 'OpenRouter'];
        const randomModel = availableModels[Math.floor(Math.random() * availableModels.length)];
        
        setMessages(prev => prev.slice(0, index - 1));
        handleSendMessage(prevMsg.text, randomModel, prevMsg.imageBase64, prevMsg.attachedFile);
      }
    }
  };

  const handleSendMessage = async (text, model = null, imageBase64 = null, attachedFile = null, selectedParams = {}) => {
    const effectiveModel = model || selectedModel || 'Auto';
    if (!text.trim() && !imageBase64 && !attachedFile) return;
    stopCurrentSpeech();

    let formattedPrompt = text || (attachedFile ? `Uploaded document: **${attachedFile.name}**` : "Attached an image for analysis.");
    if (selectedParams && Object.keys(selectedParams).length > 0) {
      const paramsList = Object.entries(selectedParams)
        .map(([key, val]) => `• **${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}**: \`${val}\``)
        .join('\n');
      formattedPrompt = `**[Selected Agent Parameters]**:\n${paramsList}\n\n**User Question**:\n${text || "Please analyze."}`;
    }

    const newUserMsg = { 
      id: Date.now(), 
      text: formattedPrompt, 
      sender: 'user',
      hasImage: !!imageBase64,
      imageBase64,
      attachedFile
    };
    
    setMessages(prev => [...prev, newUserMsg]);
    setIsGenerating(true);

    try {
      if (attachedFile) {
        if (attachedFile.type === 'application/pdf' || attachedFile.name.endsWith('.pdf')) {
          const formData = new FormData();
          formData.append('file', attachedFile.file);
          formData.append('user_id', 'user_sricharan_default');
          formData.append('title', attachedFile.name);

          const ingestRes = await fetch(`${API_BASE_URL}/api/memory/ingest-pdf`, {
            method: 'POST',
            body: formData
          });

          if (ingestRes.ok) {
            const ingestData = await ingestRes.json();
            const ragSuccessMsg = {
              id: Date.now() + 1,
              text: `### Document Ingested\n* **File**: \`${ingestData.document}\`\n* **Pages**: ${ingestData.total_pages}\n* **Chunks Indexed**: ${ingestData.total_chunks_indexed}\n\n${ingestData.message}\n\n*You can now ask questions about this document.*`,
              sender: 'ai',
              modelInfo: 'RAG'
            };
            setMessages(prev => [...prev, ragSuccessMsg]);
            setIsGenerating(false);
            return;
          }
        }
      }

      if (effectiveModel === 'ImageGen') {
        const res = await fetch(`${API_BASE_URL}/api/image-gen/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text || "A beautiful landscape", style: "vivid", model: "flux" })
        });

        const data = await res.json();
        if (data.success || data.image_url) {
          const newAiMsg = {
            id: Date.now() + 1,
            text: `### Image Generated\n**Prompt**: *${data.enriched_prompt || text}*`,
            sender: 'ai',
            imageUrl: data.image_url,
            isGeneratedImage: true,
            modelInfo: 'FLUX AI'
          };
          setMessages(prev => [...prev, newAiMsg]);
          setIsGenerating(false);
          return;
        } else {
          throw new Error("Image generation failed");
        }
      }

      const endpoint = activeAgent && activeAgent.id ? '/agent/chat' : '/chat';
      const bodyPayload = activeAgent && activeAgent.id ? {
        agent_id: activeAgent.id,
        prompt: formattedPrompt,
        parameters: selectedParams,
        has_image: !!imageBase64,
        image_base64: imageBase64
      } : {
        prompt: formattedPrompt,
        has_image: !!imageBase64,
        image_base64: imageBase64,
        override_model: effectiveModel !== 'Auto' ? effectiveModel : null
      };

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload)
      });
      
      const data = await res.json();
      await new Promise(resolve => setTimeout(resolve, 400));
      
      let responseText = data.response || "No response received from model.";
      
      const artifactMatch = responseText.match(/<atlas_artifact[^>]*>([\s\S]*?)<\/atlas_artifact>/i);
      let artifactContent = null;
      if (artifactMatch) {
        artifactContent = artifactMatch[1].trim();
        responseText = responseText.replace(artifactMatch[0], '').trim();
      }

      const newAiMsg = { 
        id: Date.now() + 1, 
        text: responseText, 
        sender: 'ai',
        modelInfo: data.model_used || data.provider || effectiveModel,
        hasArtifact: !!artifactContent
      };
      
      setMessages(prev => [...prev, newAiMsg]);
      setIsGenerating(false);

      if (artifactContent && onOpenArtifact) {
        onOpenArtifact({ title: `${activeAgent?.name || 'General'} Plan`, content: artifactContent });
      }

      if (isAutoSpeak) {
        speakAtlasResponse(responseText);
      }

    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { 
        id: Date.now() + 1, 
        text: 'Connection Error: Could not reach the backend. Please check if the server is running.', 
        sender: 'ai',
        modelInfo: 'System'
      }]);
      setIsGenerating(false);
    }
  };

  return (
    <div className="chat-interface">
      <AgentBanner activeAgent={activeAgent} />

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onOpenArtifact={() => msg.hasArtifact && onOpenArtifact({ title: 'Generated Plan', content: '# Plan' })}
            onRetry={handleRetry}
            onSpeak={(text) => speakAtlasResponse(text)}
          />
        ))}

        {isGenerating && (
          <div className="message-row ai-row">
            <div className="message-container">
              <div className="message-avatar">
                <div className="ai-avatar-circle">
                  <img src="/logo.png" alt="AI" className="ai-avatar-img" />
                </div>
              </div>
              <div className="message-content" style={{ display: 'flex', alignItems: 'center' }}>
                <div className="generating-card">
                  <div className="generating-text">
                    <span>Generating...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-wrapper">
        <ChatInput 
          onSendMessage={(text, imageBase64, attachedFile, selectedParams) => handleSendMessage(text, null, imageBase64, attachedFile, selectedParams)} 
          disabled={isGenerating} 
          isListening={isListening}
          onMicClick={handleToggleVoiceMode}
          isAutoSpeak={isAutoSpeak}
          onToggleAutoSpeak={() => setIsAutoSpeak(prev => !prev)}
          activeAgent={activeAgent}
        />
      </div>
    </div>
  );
};

export default ChatInterface;
