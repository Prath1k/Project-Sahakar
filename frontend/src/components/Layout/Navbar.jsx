import React from 'react';
import { Sun, Moon, Menu } from 'lucide-react';
import './Navbar.css';

const Navbar = ({ isDarkMode, toggleTheme, toggleSidebar, activeAgent }) => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <button className="btn-silver btn-icon" onClick={toggleSidebar} title="Menu">
          <Menu size={18} />
        </button>
      </div>
      
      <div className="navbar-center" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <img src="/logo.png" alt="Logo" className="navbar-logo" />
        <span className="navbar-title">Project Sahakar</span>
        {activeAgent && activeAgent.name !== '⚡ General ATLAS' && (
          <span style={{
            background: 'var(--primary)',
            color: '#fff',
            padding: '2px 10px',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: '600',
            letterSpacing: '0.3px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
          }}>
            {activeAgent.name}
          </span>
        )}
      </div>
      
      <div className="navbar-right">
        <button className="btn-silver btn-icon" onClick={toggleTheme} title="Toggle Theme">
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
