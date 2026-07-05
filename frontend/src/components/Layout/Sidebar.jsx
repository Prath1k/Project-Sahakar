import React, { useState, useEffect } from 'react';
import { X, MessageSquare, Plus, LogOut, User, Trash2, ChevronRight, Zap, Clock } from 'lucide-react';
import { supabase } from '../../lib/supabaseClient';
import './Sidebar.css';

// All 7 ATLAS Intelligent Agents
const AGENTS = [
  {
    id: null,
    name: 'General ATLAS',
    subtitle: 'Auto-Routing Engine',
    emoji: '⚡',
    color: '#7c6bff',
    glow: 'rgba(124,107,255,0.2)',
    description: 'Intelligent multi-model routing'
  },
  {
    id: 'scholar_core',
    name: 'ScholarCore',
    subtitle: 'Academic Intelligence',
    emoji: '🎓',
    color: '#3ecfcf',
    glow: 'rgba(62,207,207,0.2)',
    description: 'Feynman technique, flashcards, RAG study'
  },
  {
    id: 'career_architect',
    name: 'CareerArchitect',
    subtitle: 'Career Optimization',
    emoji: '💼',
    color: '#ff7a45',
    glow: 'rgba(255,122,69,0.2)',
    description: 'ATS resumes, mock interviews, roadmaps'
  },
  {
    id: 'fiscal_sentinel',
    name: 'FiscalSentinel',
    subtitle: 'Financial Intelligence',
    emoji: '📊',
    color: '#34d399',
    glow: 'rgba(52,211,153,0.2)',
    description: 'Budget tracking, burn-rate analysis'
  },
  {
    id: 'velocity_form',
    name: 'VelocityForm',
    subtitle: 'Fitness & Physiology',
    emoji: '⚡',
    color: '#f472b6',
    glow: 'rgba(244,114,182,0.2)',
    description: 'Adaptive training, macro calculator'
  },
  {
    id: 'zenith_counsel',
    name: 'ZenithCounsel',
    subtitle: 'Cognitive Health',
    emoji: '🧘',
    color: '#a78bfa',
    glow: 'rgba(167,139,250,0.2)',
    description: 'CBT frameworks, emotional support'
  },
  {
    id: 'nexus_strategist',
    name: 'NexusStrategist',
    subtitle: 'Logistics & Planning',
    emoji: '🧭',
    color: '#60a5fa',
    glow: 'rgba(96,165,250,0.2)',
    description: 'Itineraries, schedules, constraint planning'
  },
];

const Sidebar = ({ isOpen, onClose, userEmail, onSignOut, activeAgent, onSelectAgent, onNewChat }) => {
  const [chatHistory, setChatHistory] = useState([]);
  const [hoveredAgent, setHoveredAgent] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      const raw = localStorage.getItem('atlas_chat_history');
      if (raw) setChatHistory(JSON.parse(raw).slice(0, 15));
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
      onSelectAgent(session.agentId, agent ? `${agent.emoji} ${agent.name}` : '⚡ General ATLAS', session.messages);
    }
    onClose();
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
            <div className="logo-orb" />
            <span className="sidebar-title">ATLAS</span>
          </div>
          <button className="sidebar-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sidebar-content">
          {/* New Chat Button */}
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

          {/* Agents Section */}
          <div className="sidebar-section">
            <div className="section-header">
              <Zap size={12} className="section-icon" />
              <span className="section-title">Intelligent Agents</span>
            </div>

            <div className="agents-list">
              {AGENTS.map((agent) => {
                const isActive = activeAgent?.id === agent.id;
                return (
                  <button
                    key={agent.id ?? 'general'}
                    className={`agent-card ${isActive ? 'active' : ''}`}
                    onClick={() => {
                      if (onSelectAgent) onSelectAgent(agent.id, `${agent.emoji} ${agent.name}`);
                      onClose();
                    }}
                    onMouseEnter={() => setHoveredAgent(agent.id ?? 'general')}
                    onMouseLeave={() => setHoveredAgent(null)}
                    style={isActive ? { '--agent-color': agent.color, '--agent-glow': agent.glow } : {}}
                  >
                    <div className="agent-emoji-wrap" style={{ background: isActive ? agent.glow : 'var(--bg-glass)' }}>
                      <span className="agent-emoji">{agent.emoji}</span>
                    </div>
                    <div className="agent-info">
                      <span className="agent-name">{agent.name}</span>
                      <span className="agent-subtitle">{agent.subtitle}</span>
                    </div>
                    <div className="agent-right">
                      {isActive && <div className="active-dot" style={{ background: agent.color }} />}
                      <ChevronRight size={13} className="agent-arrow" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Chat History Section */}
          <div className="sidebar-section" style={{ marginTop: '8px' }}>
            <div className="section-header">
              <Clock size={12} className="section-icon" />
              <span className="section-title">Recent Chats</span>
              {chatHistory.length > 0 && (
                <button className="clear-history-btn" onClick={handleClearHistory} title="Clear history">
                  <Trash2 size={11} />
                </button>
              )}
            </div>

            {chatHistory.length === 0 ? (
              <div className="empty-history">
                <MessageSquare size={18} style={{ opacity: 0.3 }} />
                <span>No chats yet</span>
              </div>
            ) : (
              <div className="history-list">
                {chatHistory.map((session, i) => (
                  <button
                    key={i}
                    className="history-item"
                    onClick={() => handleSelectHistory(session)}
                    title={session.title}
                  >
                    <MessageSquare size={13} className="history-icon" />
                    <div className="history-info">
                      <span className="history-title">{session.title}</span>
                      <span className="history-time">{formatTime(session.timestamp)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
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
