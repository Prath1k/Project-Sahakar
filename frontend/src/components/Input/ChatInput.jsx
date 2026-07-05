import React, { useState, useRef } from 'react';
import { Send, Mic, Paperclip, X, FileText } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, disabled, isListening, onMicClick, isAutoSpeak, onToggleAutoSpeak }) => {
  const [text, setText] = useState('');
  const [attachedImage, setAttachedImage] = useState(null);
  const [attachedFile, setAttachedFile] = useState(null);
  
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if ((text.trim() || attachedImage || attachedFile) && !disabled) {
      onSendMessage(text, attachedImage?.base64, attachedFile);
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
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  return (
    <div className="chat-input-container">
      <div className="input-box">
        {/* Attachment Previews */}
        {attachedImage && (
          <div className="attachment-preview">
            <div className="preview-img-wrap">
              <img src={attachedImage.base64} alt="Attached" />
            </div>
            <div className="preview-meta">
              <span className="preview-name">{attachedImage.name}</span>
              <span className="preview-type">Image</span>
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
          <div className="attachment-preview">
            <div className="preview-icon-wrap">
              <FileText size={20} />
            </div>
            <div className="preview-meta">
              <span className="preview-name">{attachedFile.name}</span>
              <span className="preview-type">{attachedFile.size}</span>
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
          placeholder="Ask me anything..."
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
              title="Attach file"
              disabled={disabled}
            >
              <Paperclip size={16} />
            </button>
            
            <button 
              type="button" 
              className={`btn-silver btn-icon action-btn ${isListening ? 'listening-active' : ''}`}
              onClick={onMicClick}
              title="Voice input"
              disabled={disabled}
            >
              <Mic size={16} />
            </button>

            <button 
              type="button" 
              className={`btn-silver action-btn ${isAutoSpeak ? 'listening-active' : ''}`}
              onClick={onToggleAutoSpeak}
              title={isAutoSpeak ? "Auto-Speak: ON (Click to turn off)" : "Auto-Speak: OFF (Click to turn on)"}
              style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '0 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold' }}
            >
              🔊 {isAutoSpeak ? 'ON' : 'OFF'}
            </button>
          </div>

          <div className="actions-right">
            <button 
              type="button" 
              className="submit-btn"
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
        <span>AI can make mistakes. Verify critical facts and generated outputs.</span>
      </div>
    </div>
  );
};

export default ChatInput;
