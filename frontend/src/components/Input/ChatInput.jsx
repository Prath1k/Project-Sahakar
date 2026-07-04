import React, { useState } from 'react';
import { Send, Mic, Paperclip, ChevronDown } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, disabled, isListening, onMicClick }) => {
  const [text, setText] = useState('');
  const [model, setModel] = useState('Auto');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const models = [
    { id: 'Auto', name: '🌟 Auto (Intelligent Routing)' },
    { id: 'Groq', name: '⚡ Groq (Llama 3.3)' },
    { id: 'SambaNova', name: '🧠 SambaNova (DeepSeek)' },
    { id: 'Nvidia', name: '👁️ NVIDIA NIM (Vision)' },
    { id: 'Cerebras', name: '🚀 Cerebras (Qwen 3)' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSendMessage(text, model);
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">
      <div className="input-box">
        
        {/* Model Selector Dropdown inside input area */}
        <div className="model-selector-wrapper">
          <button 
            type="button"
            className="model-selector-btn"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            disabled={disabled}
          >
            {models.find(m => m.id === model)?.name || 'Auto'}
            <ChevronDown size={14} />
          </button>
          
          {isDropdownOpen && (
            <div className="model-dropdown animate-slide-up">
              {models.map(m => (
                <div 
                  key={m.id} 
                  className="dropdown-item"
                  onClick={() => {
                    setModel(m.id);
                    setIsDropdownOpen(false);
                  }}
                >
                  {m.name}
                </div>
              ))}
            </div>
          )}
        </div>

        <textarea
          className="chat-textarea"
          placeholder="Ask me anything..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        
        <div className="input-actions">
          <button type="button" className="btn-silver btn-icon action-btn">
            <Paperclip size={18} />
          </button>
          
          <button 
            type="button" 
            className={`btn-silver btn-icon action-btn ${isListening ? 'listening-active' : ''}`}
            onClick={onMicClick}
          >
            <Mic size={18} color={isListening ? 'red' : 'currentColor'} />
          </button>

          <button 
            type="button" 
            className="btn-silver btn-icon submit-btn"
            onClick={handleSubmit}
            disabled={!text.trim() || disabled}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
      <div className="input-disclaimer">
        AI can make mistakes. Verify critical facts and generated outputs.
      </div>
    </div>
  );
};

export default ChatInput;
