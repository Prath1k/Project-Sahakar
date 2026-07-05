import React, { useState, useEffect } from 'react';
import { X, MessageSquare, Plus, LogOut, User, Trash2, ChevronDown, ChevronUp, Download } from 'lucide-react';
import { supabase } from '../../lib/supabaseClient';
import './Sidebar.css';

const AGENTS = [
  { id: null,               name: 'General',    subtitle: 'Auto-Routing' },
  { id: 'scholar_core',     name: 'Scholar',    subtitle: 'Academic Intelligence' },
  { id: 'career_architect', name: 'Career',     subtitle: 'Career Optimization' },
  { id: 'fiscal_sentinel',  name: 'Finance',    subtitle: 'Financial Intelligence' },
  { id: 'velocity_form',    name: 'Fitness',    subtitle: 'Fitness & Physiology' },
  { id: 'biometrics_pilot', name: 'Biometrics', subtitle: 'Preventative Health' },
  { id: 'zenith_counsel',   name: 'Wellness',   subtitle: 'Cognitive Health' },
  { id: 'nexus_strategist', name: 'Planner',    subtitle: 'Logistics & Planning' },
];

const MODELS = [
  { id: 'Auto',       name: 'Auto (Intelligent Routing)' },
  { id: 'Groq',       name: 'Groq (Llama 3.3 70B)' },
  { id: 'SambaNova',  name: 'DeepSeek-R1 (SambaNova)' },
  { id: 'Maverick',   name: 'Llama-4-Maverick (128K)' },
  { id: 'Cerebras',   name: 'Cerebras (Llama 3.3)' },
  { id: 'Gemini',     name: 'Gemini 1.5 Pro' },
  { id: 'Nvidia',     name: 'NVIDIA NIM Vision' },
  { id: 'OpenRouter', name: 'OpenRouter Free (Gemma)' },
  { id: 'ImageGen',   name: 'ImageGen (FLUX AI)' },
];

const Sidebar = ({ isOpen, onClose, userEmail, onSignOut, activeAgent, onSelectAgent, onNewChat, selectedModel, onSelectModel }) => {
  const [chatHistory, setChatHistory] = useState([]);
  const [isModelsOpen, setIsModelsOpen] = useState(false);

  // Reload history every time sidebar opens
  useEffect(() => {
    if (isOpen) loadHistory();
  }, [isOpen]);

  const loadHistory = () => {
    try {
      const raw = localStorage.getItem('atlas_chat_history');
      if (raw) setChatHistory(JSON.parse(raw).slice(0, 20));
      else setChatHistory([]);
    } catch (e) {
      setChatHistory([]);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    if (onSignOut) onSignOut();
    onClose();
  };

  const handleClearHistory = () => {
    localStorage.removeItem('atlas_chat_history');
    setChatHistory([]);
  };

  const handleSelectHistory = (session) => {
    if (onSelectAgent) {
      const agent = AGENTS.find(a => a.id === session.agentId);
      onSelectAgent(session.agentId, agent ? agent.name : 'General', session.messages);
    }
    onClose();
  };

  const handleDeleteSession = (e, sessionId) => {
    e.stopPropagation();
    try {
      const raw = localStorage.getItem('atlas_chat_history');
      if (raw) {
        const history = JSON.parse(raw).filter(h => h.id !== sessionId);
        localStorage.setItem('atlas_chat_history', JSON.stringify(history));
        setChatHistory(history.slice(0, 20));
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleExportTxt = () => {
    const raw = localStorage.getItem('atlas_chat_history');
    if (!raw) return;
    const history = JSON.parse(raw);
    let text = '';
    history.forEach(session => {
      text += `=== ${session.title} (${new Date(session.timestamp).toLocaleString()}) ===\n\n`;
      (session.messages || []).forEach(msg => {
        text += `[${msg.sender === 'user' ? 'You' : 'AI'}]: ${msg.text}\n\n`;
      });
      text += '\n---\n\n';
    });
    downloadFile(text, 'chat-history.txt', 'text/plain');
  };

  const handleExportJson = () => {
    const raw = localStorage.getItem('atlas_chat_history');
    if (!raw) return;
    downloadFile(raw, 'chat-history.json', 'application/json');
  };

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatTime = (ts) => {
    const d = new Date(ts);
    const now = new Date();
    const diffH = (now - d) / 3600000;
    if (diffH < 1) return 'Just now';
    if (diffH < 24) return `${Math.floor(diffH)}h ago`;
    return d.toLocaleDateString('en', { month: 'short', day: 'numeric' });
  };

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="sidebar-title">Menu</span>
          </div>
          <button className="sidebar-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sidebar-content">
          {/* New Chat */}
          <button
            className="new-chat-btn"
            onClick={() => {
              if (onNewChat) onNewChat();
              onClose();
            }}
          >
            <Plus size={15} />
            <span>New Chat</span>
          </button>

          {/* Agents */}
          <div className="sidebar-section">
            <div className="section-header">
              <span className="section-title">AGENTS</span>
            </div>
            <div className="agents-list">
              {AGENTS.map((agent) => {
                const isActive = activeAgent?.id === agent.id;
                return (
                  <button
                    key={agent.id ?? 'general'}
                    className={`agent-card ${isActive ? 'active' : ''}`}
                    onClick={() => {
                      if (onSelectAgent) onSelectAgent(agent.id, agent.name);
                      onClose();
                    }}
                  >
                    <div className="agent-info">
                      <span className="agent-name">{agent.name}</span>
                      <span className="agent-subtitle">{agent.subtitle}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Models Dropdown */}
          <div className="sidebar-section">
            <button className="section-header section-toggle" onClick={() => setIsModelsOpen(!isModelsOpen)}>
              <span className="section-title">MODELS</span>
              {isModelsOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {isModelsOpen && (
              <div className="agents-list">
                {MODELS.map((m) => (
                  <button
                    key={m.id}
                    className={`agent-card ${selectedModel === m.id ? 'active' : ''}`}
                    onClick={() => onSelectModel && onSelectModel(m.id)}
                  >
                    <div className="agent-info">
                      <span className="agent-name">{m.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Chat History */}
          <div className="sidebar-section">
            <div className="section-header">
              <span className="section-title">RECENT</span>
              {chatHistory.length > 0 && (
                <button className="clear-history-btn" onClick={handleClearHistory} title="Clear all">
                  <Trash2 size={11} />
                </button>
              )}
            </div>
            {chatHistory.length > 0 && (
              <div className="history-list">
                {chatHistory.map((session, i) => (
                  <button
                    key={session.id || i}
                    className="history-item"
                    onClick={() => handleSelectHistory(session)}
                    title={session.title}
                  >
                    <MessageSquare size={13} className="history-icon" />
                    <div className="history-info">
                      <span className="history-title">{session.title}</span>
                      <span className="history-time">{formatTime(session.timestamp)}</span>
                    </div>
                    <button
                      className="clear-history-btn"
                      onClick={(e) => handleDeleteSession(e, session.id)}
                      title="Delete this chat"
                    >
                      <X size={11} />
                    </button>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Export */}
          {chatHistory.length > 0 && (
            <div className="sidebar-section">
              <div className="section-header">
                <span className="section-title">EXPORT</span>
              </div>
              <div className="export-btns">
                <button className="export-btn" onClick={handleExportTxt}>
                  <Download size={13} />
                  <span>Export TXT</span>
                </button>
                <button className="export-btn" onClick={handleExportJson}>
                  <Download size={13} />
                  <span>Export JSON</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
          {userEmail && (
            <div className="user-info">
              <div className="user-avatar">
                <User size={14} />
              </div>
              <span className="user-email">{userEmail}</span>
            </div>
          )}
          <button className="sign-out-btn" onClick={handleSignOut}>
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
