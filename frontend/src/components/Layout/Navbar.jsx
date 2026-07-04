import React from 'react';
import { Sun, Moon, Menu } from 'lucide-react';
import './Navbar.css';

const Navbar = ({ isDarkMode, toggleTheme, toggleSidebar }) => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <button className="btn-silver btn-icon" onClick={toggleSidebar} title="Menu">
          <Menu size={18} />
        </button>
      </div>
      
      <div className="navbar-center">
        <img src="/logo.png" alt="Logo" className="navbar-logo" />
        <span className="navbar-title">Project Sahakar</span>
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
