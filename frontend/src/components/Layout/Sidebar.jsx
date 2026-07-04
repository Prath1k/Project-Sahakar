import React from 'react';
import { X, MessageSquare, Clock, Settings, Plus, LogOut, User } from 'lucide-react';
import { supabase } from '../../lib/supabaseClient';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose, userEmail, onSignOut }) => {
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
          <button className="sidebar-btn new-chat-btn">
            <Plus size={16} />
            <span>New Chat</span>
          </button>
          
          <div className="sidebar-section">
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
