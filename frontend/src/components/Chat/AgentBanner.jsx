import React, { useEffect, useState } from 'react';

const AGENT_CONFIGS = {
  scholar_core:      { color: '#3ecfcf', glow: 'rgba(62,207,207,0.12)',  emoji: '🎓', desc: 'Feynman method · RAG study · Flashcards' },
  career_architect:  { color: '#ff7a45', glow: 'rgba(255,122,69,0.12)',  emoji: '💼', desc: 'ATS optimizer · Mock interviews · Roadmaps' },
  fiscal_sentinel:   { color: '#34d399', glow: 'rgba(52,211,153,0.12)',  emoji: '📊', desc: 'Budget · Burn-rate · Financial intelligence' },
  velocity_form:     { color: '#f472b6', glow: 'rgba(244,114,182,0.12)', emoji: '⚡', desc: 'Adaptive training · Autoregulation · Macros' },
  zenith_counsel:    { color: '#a78bfa', glow: 'rgba(167,139,250,0.12)', emoji: '🧘', desc: 'CBT · Emotional support · Crisis detection' },
  nexus_strategist:  { color: '#60a5fa', glow: 'rgba(96,165,250,0.12)',  emoji: '🧭', desc: 'Itineraries · Scheduling · Logistics' },
};

const AgentBanner = ({ activeAgent }) => {
  const [visible, setVisible] = useState(false);
  const [displayed, setDisplayed] = useState(activeAgent);

  useEffect(() => {
    if (activeAgent?.id) {
      setDisplayed(activeAgent);
      setVisible(false);
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
    }
  }, [activeAgent?.id]);

  if (!activeAgent?.id || !visible) return null;

  const cfg = AGENT_CONFIGS[activeAgent.id] || { color: '#7c6bff', glow: 'rgba(124,107,255,0.12)', emoji: '⚡', desc: 'Specialized agent mode' };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '8px 16px',
        background: cfg.glow,
        borderBottom: `1px solid ${cfg.color}33`,
        animation: 'slideUp 0.25s ease-out forwards',
      }}
    >
      <span style={{ fontSize: '1.1rem' }}>{cfg.emoji}</span>
      <div style={{ flex: 1 }}>
        <span style={{
          fontSize: '0.8rem',
          fontWeight: 700,
          color: cfg.color,
          letterSpacing: '0.02em',
        }}>
          {displayed?.name?.replace(/^[^\w]*/, '').trim()}
        </span>
        <span style={{
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
          marginLeft: '8px',
        }}>
          {cfg.desc}
        </span>
      </div>
      <div style={{
        width: 7, height: 7, borderRadius: '50%',
        background: cfg.color,
        boxShadow: `0 0 6px ${cfg.color}`,
        animation: 'pulse-skeleton 2s ease-in-out infinite',
      }} />
    </div>
  );
};

export default AgentBanner;
