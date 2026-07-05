import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import ChatInterface from './components/Chat/ChatInterface';
import ArtifactPanel from './components/Artifacts/ArtifactPanel';
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import AuthPage from './components/Auth/AuthPage';
import { supabase } from './lib/supabaseClient';
import './index.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [session, setSession] = useState(null);
  const [isGuest, setIsGuest] = useState(false);
  const [guestId] = useState(() => {
    let gid = sessionStorage.getItem('atlas_guest_id');
    if (!gid) {
      gid = 'guest_' + Math.random().toString(36).substring(2, 11);
      sessionStorage.setItem('atlas_guest_id', gid);
    }
    return gid;
  });
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeAgent, setActiveAgent] = useState({ id: null, name: 'General' });
  const [selectedModel, setSelectedModel] = useState('Auto');
  const [loadedMessages, setLoadedMessages] = useState(null);
  const [chatResetKey, setChatResetKey] = useState(0);

  const handleSelectAgent = (agentId, agentName, messages = null) => {
    setActiveAgent({ id: agentId, name: agentName });
    if (messages && messages.length > 0) {
      setLoadedMessages(messages);
    } else {
      setLoadedMessages(null);
    }
    setIsSidebarOpen(false);
  };

  const handleNewChat = () => {
    setLoadedMessages(null);
    setActiveAgent({ id: null, name: 'General' });
    setChatResetKey(prev => prev + 1);
  };

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode', 'dark');
      document.body.classList.remove('light-mode');
    } else {
      document.body.classList.remove('dark-mode', 'dark');
      document.body.classList.add('light-mode');
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

  const handleOpenArtifact = (artifact) => {
    setActiveArtifact(artifact);
    setIsArtifactOpen(true);
  };

  const handleCloseArtifact = () => {
    setIsArtifactOpen(false);
    setTimeout(() => setActiveArtifact(null), 400);
  };

  if (!session && !isGuest) {
    return (
      <div className="app-container" style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 100 }}>
          <button className="btn-silver btn-icon" onClick={toggleTheme} title="Toggle Theme" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
        <AuthPage onGuestLogin={() => setIsGuest(true)} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
        userEmail={session?.user?.email || (isGuest ? 'Guest User' : null)} 
        onSignOut={() => {
          sessionStorage.removeItem('atlas_guest_id');
          setIsGuest(false);
        }} 
        activeAgent={activeAgent} 
        onSelectAgent={handleSelectAgent}
        onNewChat={handleNewChat}
        selectedModel={selectedModel}
        onSelectModel={setSelectedModel}
      />
      <div className="chat-container">
        <Navbar 
          isDarkMode={isDarkMode} 
          toggleTheme={toggleTheme} 
          toggleSidebar={toggleSidebar}
          activeAgent={activeAgent} 
        />
        <ChatInterface 
          key={chatResetKey}
          onOpenArtifact={handleOpenArtifact} 
          activeAgent={activeAgent} 
          loadedMessages={loadedMessages}
          selectedModel={selectedModel}
          userId={session?.user?.email || session?.user?.id || (isGuest ? guestId : 'user_sricharan_default')}
        />
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
