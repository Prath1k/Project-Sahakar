import React, { useState, useEffect } from 'react';
import ChatInterface from './components/Chat/ChatInterface';
import ArtifactPanel from './components/Artifacts/ArtifactPanel';
import Navbar from './components/Layout/Navbar';
import './index.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  // Mock function to simulate opening an artifact
  const handleOpenArtifact = (artifact) => {
    setActiveArtifact(artifact);
    setIsArtifactOpen(true);
  };

  const handleCloseArtifact = () => {
    setIsArtifactOpen(false);
    setTimeout(() => setActiveArtifact(null), 500); // wait for animation
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <Navbar 
          isDarkMode={isDarkMode} 
          toggleTheme={toggleTheme} 
        />
        <ChatInterface onOpenArtifact={handleOpenArtifact} />
      </div>
      
      <div className={`artifact-container ${isArtifactOpen ? 'open' : ''}`}>
        <ArtifactPanel 
          artifact={activeArtifact} 
          onClose={handleCloseArtifact} 
        />
      </div>
    </div>
  );
}

export default App;
