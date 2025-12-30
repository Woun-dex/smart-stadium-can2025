import React from 'react';

const LoadingOverlay = ({ message }) => {
  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p style={{ color: 'rgba(255,255,255,0.8)' }}>{message || 'Running simulation...'}</p>
      <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)' }}>
        Analyzing crowd patterns with AI
      </p>
    </div>
  );
};

export default LoadingOverlay;
