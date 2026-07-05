import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from '../Input/ChatInput';
import AgentBanner from './AgentBanner';
import { useVoiceHandoff } from '../../hooks/useVoiceHandoff';
import { GlyphMatrix } from "@/components/ui/glyph-matrix";
import { API_BASE_URL } from "@/lib/config";
import { Volume2, VolumeX, Trash2, RotateCcw } from 'lucide-react';
import './ChatInterface.css';

const DEFAULT_WELCOME = {
  id: 1,
  text: "# Welcome to ATLAS & Project Sahakar 🌟\n\nI am your autonomous **multi-agent task and learning assistant**. How can I help you today?\n\n### What I can do:\n* **🎓 ScholarCore**: Study with Feynman technique & RAG textbook memory\n* **💼 CareerArchitect**: Optimize ATS resumes & generate career roadmaps\n* **📊 FiscalSentinel**: Analyze budgets, burn rates & financial intelligence\n* **⚡ VelocityForm**: Adaptive training & macronutrient autoregulation\n* **🧘 ZenithCounsel**: CBT cognitive health & emotional support\n* **🧭 NexusStrategist**: Complex logistics, itineraries & scheduling\n* **🎨 ImageGen**: Create stunning AI images using FLUX\n* **📄 RAG Memory**: Upload PDFs to pinpoint answers down to the exact page & chunk!",
  sender: 'ai',
  modelInfo: 'ATLAS Multi-Agent Framework'
};

const ChatInterface = ({ onOpenArtifact, activeAgent, loadedMessages }) => {
  const [messages, setMessages] = useState(() => loadedMessages || [DEFAULT_WELCOME]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isAutoSpeak, setIsAutoSpeak] = useState(false);
  const [currentSessionTitle, setCurrentSessionTitle] = useState('New Conversation');
  const messagesEndRef = useRef(null);
  
  const { isListening, stopListening, stopCurrentSpeech, speakAtlasResponse, startEightSecondListeningLoop } = useVoiceHandoff();

  // Load messages from sidebar history click
  useEffect(() => {
    if (loadedMessages && loadedMessages.length > 0) {
      setMessages(loadedMessages);
    }
  }, [loadedMessages]);

  // Save session to localStorage when messages change
  useEffect(() => {
    if (messages.length > 1) {
      saveToHistory(messages);
    }
  }, [messages, activeAgent]);

  const saveToHistory = (msgs) => {
    try {
      const raw = localStorage.getItem('atlas_chat_history');
      let history = raw ? JSON.parse(raw) : [];
      
      // Derive a title from the first user message
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

      // Update existing or prepend new
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
    setIsVoiceMode(prev => {
      const newState = !prev;
      if (newState) {
        startEightSecondListeningLoop((transcribedText) => {
          handleSendMessage(transcribedText, 'Auto');
          setIsVoiceMode(false);
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

  const handleSendMessage = async (text, model = 'Auto', imageBase64 = null, attachedFile = null) => {
    if (!text.trim() && !imageBase64 && !attachedFile) return;
    stopCurrentSpeech();

    const newUserMsg = { 
      id: Date.now(), 
      text: text || (attachedFile ? `Uploaded document: **${attachedFile.name}**` : "Attached an image for analysis."), 
      sender: 'user',
      hasImage: !!imageBase64,
      imageBase64,
      attachedFile
    };
    
    setMessages(prev => [...prev, newUserMsg]);
    setIsGenerating(true);

    try {
      // 1. Handle PDF / Document Ingestion to RAG
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
              text: `### 📄 Document Successfully Ingested into RAG!\n* **File**: \`${ingestData.document}\`\n* **Pages Parsed**: ${ingestData.total_pages}\n* **Semantic Chunks Indexed**: ${ingestData.total_chunks_indexed}\n\n${ingestData.message}\n\n*You can now ask me any question about this document and I will pinpoint the exact page and section!*`,
              sender: 'ai',
              modelInfo: 'SCAAR RAG Document Ocean'
            };
            setMessages(prev => [...prev, ragSuccessMsg]);
            setIsGenerating(false);
            return;
          }
        }
      }

      // 2. Handle Image Generation (FLUX AI via Pollinations)
      if (model === 'ImageGen') {
        const res = await fetch(`${API_BASE_URL}/api/image-gen/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text || "A beautiful cyberpunk city at sunset, 8k resolution", style: "vivid", model: "flux" })
        });

        const data = await res.json();
        if (data.success || data.image_url) {
          const newAiMsg = {
            id: Date.now() + 1,
            text: `### 🎨 Image Generated Successfully!\n**Prompt**: *${data.enriched_prompt || text}*\n\nHere is your custom masterpiece generated using **FLUX AI**:`,
            sender: 'ai',
            imageUrl: data.image_url,
            isGeneratedImage: true,
            modelInfo: 'FLUX AI (Pollinations.ai)'
          };
          setMessages(prev => [...prev, newAiMsg]);
          setIsGenerating(false);
          return;
        } else {
          throw new Error("Image generation failed");
        }
      }

      // 3. Normal Chat / Agent Routing
      const endpoint = activeAgent && activeAgent.id ? '/api/agent/chat' : '/api/chat';
      const bodyPayload = activeAgent && activeAgent.id ? {
        agent_id: activeAgent.id,
        prompt: text || "Please analyze this image.",
        has_image: !!imageBase64,
        image_base64: imageBase64
      } : {
        prompt: text || "Please analyze this image.",
        has_image: !!imageBase64,
        image_base64: imageBase64,
        override_model: model !== 'Auto' ? model : null
      };

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload)
      });
      
      const data = await res.json();
      await new Promise(resolve => setTimeout(resolve, 400));
      
      let responseText = data.response || "No response received from model.";
      
      // Extract XML Artifacts if present
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
        modelInfo: data.model_used || data.provider || model,
        hasArtifact: !!artifactContent
      };
      
      setMessages(prev => [...prev, newAiMsg]);
      setIsGenerating(false);

      if (artifactContent && onOpenArtifact) {
        onOpenArtifact({ title: `${activeAgent?.name || 'ATLAS'} Plan & Roadmap`, content: artifactContent });
      }

      if (isVoiceMode || isAutoSpeak) {
        speakAtlasResponse(responseText);
      }

    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { 
        id: Date.now() + 1, 
        text: '⚠️ **Connection Error**: Could not reach the ATLAS backend. Please check if the Hugging Face Space is active or running locally on port 7860.', 
        sender: 'ai',
        modelInfo: 'System Error'
      }]);
      setIsGenerating(false);
    }
  };

  return (
    <div className="chat-interface">
      {/* Active Agent Banner */}
      <AgentBanner activeAgent={activeAgent} />

      {/* Top Bar / Controls */}
      <div className="chat-topbar">
        <div className="session-info">
          <span className="session-label">{currentSessionTitle}</span>
          <span className="msg-count">{messages.length - 1} messages</span>
        </div>

        <div className="topbar-actions">
          <button 
            onClick={() => setIsAutoSpeak(!isAutoSpeak)}
            className={`topbar-btn ${isAutoSpeak ? 'auto-speak-active' : ''}`}
            title="Toggle automatic voice narration of AI replies"
          >
            {isAutoSpeak ? <Volume2 size={15} /> : <VolumeX size={15} />}
            <span>Auto-Speak: {isAutoSpeak ? 'ON' : 'OFF'}</span>
          </button>

          <button 
            onClick={handleClearChat}
            className="topbar-btn btn-clear"
            title="Clear chat and start fresh"
          >
            <RotateCcw size={14} />
            <span>Reset Chat</span>
          </button>
        </div>
      </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            onOpenArtifact={() => msg.hasArtifact && onOpenArtifact({ title: 'Generated Plan & Roadmap', content: '# Sample Plan' })}
            onRetry={handleRetry}
            onSpeak={(text) => speakAtlasResponse(text)}
          />
        ))}

        {isGenerating && (
          <div className="message-row ai-row animate-bounce-in mt-2 mb-2">
            <div className="message-container">
              <div className="message-avatar">
                <div className="ai-avatar-circle">
                  <img src="/logo.png" alt="AI" className="ai-avatar-img" />
                </div>
              </div>
              <div className="message-content" style={{ display: 'flex', alignItems: 'center' }}>
                <div className="generating-card">
                  <GlyphMatrix color="rgba(124, 107, 255, 0.5)" />
                  <div className="generating-text">
                    <div className="skeleton-pulse" />
                    <span>Synthesizing intelligent response...</span>
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
