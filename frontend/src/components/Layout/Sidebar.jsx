import React from 'react';
import { X, MessageSquare, Clock, Settings, Plus, LogOut, User } from 'lucide-react';
import { supabase } from '../../lib/supabaseClient';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose, userEmail, onSignOut, activeAgent, onSelectAgent }) => {
  const handleSignOut = async () => {
    await supabase.auth.signOut();
    if (onSignOut) onSignOut();
    onClose();
  };
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <span className="sidebar-title">Menu</span>
          <button className="btn-silver btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
        
        <div className="sidebar-content">
          <button className="sidebar-btn new-chat-btn" onClick={() => { if (onSelectAgent) onSelectAgent(null, 'General ATLAS'); onClose(); }}>
            <Plus size={16} />
            <span>New Chat</span>
          </button>
          
          <div className="sidebar-section" style={{ marginTop: '16px' }}>
            <h3 className="section-title" style={{ color: 'var(--primary)', fontWeight: '600', letterSpacing: '0.5px' }}>Intelligent Agents</h3>
            <button className={`sidebar-btn history-btn ${activeAgent?.id === 'scholar_core' ? 'active' : ''}`} onClick={() => { if (onSelectAgent) onSelectAgent('scholar_core', 'ScholarCore'); onClose(); }} style={activeAgent?.id === 'scholar_core' ? { background: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: '600' }}>ScholarCore</span>
                <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Academic Intelligence</span>
              </div>
            </button>
            <button className={`sidebar-btn history-btn ${activeAgent?.id === 'nexus_strategist' ? 'active' : ''}`} onClick={() => { if (onSelectAgent) onSelectAgent('nexus_strategist', 'NexusStrategist'); onClose(); }} style={activeAgent?.id === 'nexus_strategist' ? { background: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: '600' }}>NexusStrategist</span>
                <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Logistics & Scheduling</span>
              </div>
            </button>
            <button className={`sidebar-btn history-btn ${activeAgent?.id === 'zenith_counsel' ? 'active' : ''}`} onClick={() => { if (onSelectAgent) onSelectAgent('zenith_counsel', 'ZenithCounsel'); onClose(); }} style={activeAgent?.id === 'zenith_counsel' ? { background: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: '600' }}>ZenithCounsel</span>
                <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Cognitive Health</span>
              </div>
            </button>
            <button className={`sidebar-btn history-btn ${activeAgent?.id === 'career_architect' ? 'active' : ''}`} onClick={() => { if (onSelectAgent) onSelectAgent('career_architect', 'CareerArchitect'); onClose(); }} style={activeAgent?.id === 'career_architect' ? { background: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: '600' }}>CareerArchitect</span>
                <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Career Optimization</span>
              </div>
            </button>
            <button className={`sidebar-btn history-btn ${!activeAgent?.id ? 'active' : ''}`} onClick={() => { if (onSelectAgent) onSelectAgent(null, 'General ATLAS'); onClose(); }} style={!activeAgent?.id ? { background: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: '600' }}>General ATLAS</span>
                <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Auto-Routing Engine</span>
              </div>
            </button>
          </div>
          
          <div className="sidebar-section" style={{ marginTop: '16px' }}>
            <h3 className="section-title">Recent</h3>
            <button className="sidebar-btn history-btn">
              <MessageSquare size={16} />
              <span>Project Sahakar Setup</span>
            </button>
            <button className="sidebar-btn history-btn">
              <Clock size={16} />
              <span>View All History</span>
            </button>
          </div>
        </div>
        
        <div className="sidebar-footer">
          {userEmail && (
            <div className="sidebar-btn" style={{ cursor: 'default', color: 'var(--text-muted)' }}>
              <User size={16} />
              <span style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>{userEmail}</span>
            </div>
          )}
          <button className="sidebar-btn settings-btn" onClick={handleSignOut} style={{ marginTop: '8px', color: 'var(--destructive)' }}>
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
