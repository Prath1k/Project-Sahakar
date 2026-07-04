import React, { useState } from 'react';
import { Send, Mic, Paperclip, ChevronDown, X } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, disabled, isListening, onMicClick }) => {
  const [text, setText] = useState('');
  const [model, setModel] = useState('Auto');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null);
  const fileInputRef = React.useRef(null);

  const models = [
    { id: 'Auto', name: '🌟 Auto (Intelligent Routing)' },
    { id: 'Groq', name: '⚡ Groq (Llama 3.3)' },
    { id: 'SambaNova', name: '🧠 SambaNova (DeepSeek)' },
    { id: 'Nvidia', name: '👁️ NVIDIA NIM (Vision)' },
    { id: 'Cerebras', name: '🚀 Cerebras (Qwen 3)' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if ((text.trim() || attachedImage) && !disabled) {
      onSendMessage(text, model, attachedImage?.base64);
      setText('');
      setAttachedImage(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedImage({ file, base64: reader.result });
      };
      reader.readAsDataURL(file);
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

        {/* Attachment Preview */}
        {attachedImage && (
          <div className="attachment-preview">
            <img src={attachedImage.base64} alt="Attached preview" />
            <button className="clear-attachment-btn" onClick={() => {
              setAttachedImage(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}>
              <X size={14} />
            </button>
          </div>
        )}

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
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
            accept="image/*"
          />
          <button 
            type="button" 
            className="btn-silver btn-icon action-btn"
            onClick={() => fileInputRef.current?.click()}
          >
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
            disabled={(!text.trim() && !attachedImage) || disabled}
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
