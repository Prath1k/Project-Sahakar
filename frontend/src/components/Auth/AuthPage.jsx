import React, { useState } from 'react';
import { supabase } from '../../lib/supabaseClient';
import './AuthPage.css';
import { Mail, Lock, Loader2 } from 'lucide-react';

const AuthPage = ({ onGuestLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setMessage('Check your email for the login link!');
      }
    } catch (err) {
      setError(err.message || 'An error occurred during authentication.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box input-box">
        <div className="auth-header">
          <img src="/logo.jpeg" alt="Logo" className="auth-logo" />
          <h2>{isLogin ? 'Welcome Back' : 'Create an Account'}</h2>
          <p>Project Sahakar - Intelligent Assistant</p>
        </div>

        {error && <div className="auth-alert auth-error">{error}</div>}
        {message && <div className="auth-alert auth-success">{message}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <Mail size={18} className="input-icon" />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="chat-textarea auth-input"
            />
          </div>

          <div className="input-group">
            <Lock size={18} className="input-icon" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="chat-textarea auth-input"
            />
          </div>

          <button type="submit" className="btn-silver submit-btn auth-submit" disabled={loading}>
            {loading ? <Loader2 size={18} className="spin-anim" /> : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="auth-footer">
          <button 
            type="button" 
            className="toggle-auth-mode"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
          </button>
          
          <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
            <button 
              type="button" 
              className="btn-silver"
              style={{ width: '100%' }}
              onClick={onGuestLogin}
            >
              Continue as Guest
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
