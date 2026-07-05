import React, { useEffect, useState } from 'react';
import { Zap, GraduationCap, Briefcase, BarChart3, Activity, Brain, Compass } from 'lucide-react';

const AGENT_CONFIGS = {
  scholar_core:      { icon: GraduationCap, desc: 'Feynman method · RAG study · Flashcards' },
  career_architect:  { icon: Briefcase, desc: 'ATS optimizer · Mock interviews · Roadmaps' },
  fiscal_sentinel:   { icon: BarChart3, desc: 'Budget · Burn-rate · Financial intelligence' },
  velocity_form:     { icon: Activity, desc: 'Adaptive training · Autoregulation · Macros' },
  zenith_counsel:    { icon: Brain, desc: 'CBT · Emotional support · Crisis detection' },
  nexus_strategist:  { icon: Compass, desc: 'Itineraries · Scheduling · Logistics' },
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

  const cfg = AGENT_CONFIGS[activeAgent.id] || { icon: Zap, desc: 'Specialized agent mode' };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '8px 16px',
        background: 'var(--bg-surface)',
        borderBottom: `1px solid var(--border-color)`,
        animation: 'slideUp 0.25s ease-out forwards',
      }}
    >
      <div style={{ color: 'var(--text-main)', display: 'flex', alignItems: 'center' }}>
        <cfg.icon size={20} />
      </div>
      <div style={{ flex: 1 }}>
        <span style={{
          fontSize: '0.8rem',
          fontWeight: 700,
          color: 'var(--text-main)',
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
        width: 7, height: 7,
        background: 'var(--text-main)',
      }} />
    </div>
  );
};

export default AgentBanner;
