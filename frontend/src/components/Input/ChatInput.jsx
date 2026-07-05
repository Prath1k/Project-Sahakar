import React, { useState, useRef } from 'react';
import { Send, Mic, Paperclip, ChevronDown, X, Sparkles, FileText, Image as ImageIcon } from 'lucide-react';
import './ChatInput.css';

const MODELS = [
  { id: 'Auto',       name: '🌟 Auto (Intelligent Routing)', desc: 'Best model for each task' },
  { id: 'Groq',       name: '⚡ Groq (Llama 3.3 70B)',         desc: 'Fast conversational chat' },
  { id: 'SambaNova',  name: '🧠 DeepSeek-R1 (SambaNova)',    desc: 'Complex code & reasoning' },
  { id: 'Maverick',   name: '📚 Llama-4-Maverick (128K)',    desc: 'Long documents & RAG' },
  { id: 'Cerebras',   name: '🚀 Cerebras (Llama 3.3)',        desc: 'Ultra high-speed batch' },
  { id: 'Gemini',     name: '✨ Gemini 1.5 Pro',              desc: 'Large context & artifacts' },
  { id: 'Nvidia',     name: '👁️ NVIDIA NIM Vision',           desc: 'Image & visual analysis' },
  { id: 'OpenRouter', name: '📡 OpenRouter Free (Gemma)',     desc: 'Multi-model fallback' },
  { id: 'ImageGen',   name: '🎨 ImageGen (FLUX AI)',          desc: 'Create images from text' },
];

const ChatInput = ({ onSendMessage, disabled, isListening, onMicClick }) => {
  const [text, setText] = useState('');
  const [model, setModel] = useState('Auto');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null);
  const [attachedFile, setAttachedFile] = useState(null);
  
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if ((text.trim() || attachedImage || attachedFile) && !disabled) {
      onSendMessage(text, model, attachedImage?.base64, attachedFile);
      setText('');
      setAttachedImage(null);
      setAttachedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedImage({ file, base64: reader.result, name: file.name });
        setAttachedFile(null);
      };
      reader.readAsDataURL(file);
    } else {
      // PDF, DOCX, TXT, MD
      setAttachedFile({ file, name: file.name, type: file.type, size: (file.size / 1024).toFixed(1) + ' KB' });
      setAttachedImage(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e) => {
    setText(e.target.value);
    // Auto-grow height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  const min = (a, b) => (a < b ? a : b);
  const selectedModelObj = MODELS.find(m => m.id === model) || MODELS[0];
  const isImageGen = model === 'ImageGen';

  return (
    <div className="chat-input-container">
      <div className={`input-box ${isImageGen ? 'image-gen-active' : ''}`}>
        
        {/* Model Selector Button & Dropdown */}
        <div className="model-selector-wrapper">
          <button 
            type="button"
            className={`model-selector-btn ${isImageGen ? 'btn-image-gen' : ''}`}
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            disabled={disabled}
          >
            {isImageGen ? <Sparkles size={14} className="animate-spin-slow text-pink-400" /> : null}
            <span>{selectedModelObj.name}</span>
            <ChevronDown size={13} style={{ opacity: 0.7 }} />
          </button>
          
          {isDropdownOpen && (
            <>
              <div className="dropdown-backdrop" onClick={() => setIsDropdownOpen(false)} />
              <div className="model-dropdown animate-slide-up">
                <div className="dropdown-header">Select Model Roster</div>
                {MODELS.map(m => (
                  <button 
                    key={m.id} 
                    type="button"
                    className={`dropdown-item ${m.id === model ? 'active' : ''}`}
                    onClick={() => {
                      setModel(m.id);
                      setIsDropdownOpen(false);
                    }}
                  >
                    <div className="dropdown-item-main">
                      <span className="dropdown-item-name">{m.name}</span>
                      <span className="dropdown-item-desc">{m.desc}</span>
                    </div>
                    {m.id === model && <div className="active-check">✓</div>}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Attachment Previews */}
        {attachedImage && (
          <div className="attachment-preview animate-fade-in">
            <div className="preview-img-wrap">
              <img src={attachedImage.base64} alt="Attached" />
            </div>
            <div className="preview-meta">
              <span className="preview-name">{attachedImage.name}</span>
              <span className="preview-type">Image Analysis Mode</span>
            </div>
            <button type="button" className="clear-attachment-btn" onClick={() => {
              setAttachedImage(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}>
              <X size={14} />
            </button>
          </div>
        )}

        {attachedFile && (
          <div className="attachment-preview animate-fade-in">
            <div className="preview-icon-wrap">
              <FileText size={20} className="text-cyan-400" />
            </div>
            <div className="preview-meta">
              <span className="preview-name">{attachedFile.name}</span>
              <span className="preview-type">{attachedFile.size} · Will ingest to RAG</span>
            </div>
            <button type="button" className="clear-attachment-btn" onClick={() => {
              setAttachedFile(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}>
              <X size={14} />
            </button>
          </div>
        )}

        {/* Main Textarea */}
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={
            isImageGen 
              ? "Describe the image you want to generate (e.g. 'Cyberpunk samurai in Tokyo rain, 8k')..." 
              : "Ask ATLAS anything, attach PDFs for RAG, or paste code..."
          }
          value={text}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        
        {/* Actions Bar */}
        <div className="input-actions">
          <div className="actions-left">
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
              accept="image/*,.pdf,.txt,.md,.docx,.doc"
            />
            <button 
              type="button" 
              className="btn-silver btn-icon action-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Attach image or PDF document"
              disabled={disabled}
            >
              <Paperclip size={16} />
            </button>
            
            <button 
              type="button" 
              className={`btn-silver btn-icon action-btn ${isListening ? 'listening-active' : ''}`}
              onClick={onMicClick}
              title="Voice input (speech-to-text)"
              disabled={disabled}
            >
              <Mic size={16} color={isListening ? '#ff5555' : 'currentColor'} />
            </button>
          </div>

          <div className="actions-right">
            <button 
              type="button" 
              className={`submit-btn ${isImageGen ? 'submit-image-gen' : ''}`}
              onClick={handleSubmit}
              disabled={(!text.trim() && !attachedImage && !attachedFile) || disabled}
              title="Send message"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>

      <div className="input-disclaimer">
        <span>ATLAS AI can make mistakes. Verify critical facts and outputs.</span>
        <span className="dot-sep">·</span>
        <span>SCAAR RAG Enabled</span>
      </div>
    </div>
  );
};

export default ChatInput;
