import React, { useState, useEffect } from 'react';
import ChatInterface from './components/Chat/ChatInterface';
import ArtifactPanel from './components/Artifacts/ArtifactPanel';
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import AuthPage from './components/Auth/AuthPage';
import { supabase } from './lib/supabaseClient';
import './index.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [session, setSession] = useState(null);
  const [isGuest, setIsGuest] = useState(false);
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeAgent, setActiveAgent] = useState({ id: null, name: '⚡ General ATLAS' });

  const handleSelectAgent = (agentId, agentName) => {
    setActiveAgent({ id: agentId, name: agentName });
    setIsSidebarOpen(false);
  };

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  // Mock function to simulate opening an artifact
  const handleOpenArtifact = (artifact) => {
    setActiveArtifact(artifact);
    setIsArtifactOpen(true);
  };

  const handleCloseArtifact = () => {
    setIsArtifactOpen(false);
    setTimeout(() => setActiveArtifact(null), 500); // wait for animation
  };

  if (!session && !isGuest) {
    return (
      <div className="app-container" style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 100 }}>
           <button className="btn-silver btn-icon" onClick={toggleTheme} title="Toggle Theme">
             {isDarkMode ? '☀️' : '🌙'}
           </button>
        </div>
        <AuthPage onGuestLogin={() => setIsGuest(true)} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} userEmail={session?.user?.email || (isGuest ? 'Guest User' : null)} onSignOut={() => setIsGuest(false)} activeAgent={activeAgent} onSelectAgent={handleSelectAgent} />
      <div className="chat-container">
        <Navbar 
          isDarkMode={isDarkMode} 
          toggleTheme={toggleTheme} 
          toggleSidebar={toggleSidebar}
          activeAgent={activeAgent}
        />
        <ChatInterface onOpenArtifact={handleOpenArtifact} activeAgent={activeAgent} />
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
