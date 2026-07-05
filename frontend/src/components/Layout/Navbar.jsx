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
        <img src="/logo.jpeg" alt="Logo" className="navbar-logo" />
        <span className="navbar-title">Project Sahakar</span>
        {activeAgent && activeAgent.name !== 'General' && (
          <span style={{
            fontSize: '0.78rem',
            fontWeight: 500,
            color: 'var(--text-muted)',
            marginLeft: '4px',
          }}>
            / {activeAgent.name}
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
