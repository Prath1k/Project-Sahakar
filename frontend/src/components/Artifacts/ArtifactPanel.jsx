import React from 'react';
import { X, Copy, Download, Maximize2 } from 'lucide-react';
import './ArtifactPanel.css';

const ArtifactPanel = ({ artifact, onClose }) => {
  if (!artifact) return null;

  return (
    <div className="artifact-panel">
      <div className="artifact-header">
        <h3 className="artifact-title">{artifact.title}</h3>
        <div className="artifact-actions">
          <button className="btn-silver btn-icon">
            <Copy size={16} />
          </button>
          <button className="btn-silver btn-icon">
            <Download size={16} />
          </button>
          <button className="btn-silver btn-icon">
            <Maximize2 size={16} />
          </button>
          <button className="btn-silver btn-icon" onClick={onClose}>
            <X size={16} />
          </button>
        </div>
      </div>
      
      <div className="artifact-content">
        <pre>{artifact.content}</pre>
      </div>
    </div>
  );
};

export default ArtifactPanel;
