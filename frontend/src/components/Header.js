import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-logo">
        <svg width="40" height="40" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="#006233" stroke="#C1272D" strokeWidth="4"/>
          <polygon points="50,20 55,40 75,40 60,52 65,72 50,60 35,72 40,52 25,40 45,40" fill="#FFD700"/>
        </svg>
        <h1>AFCON 2025 Morocco</h1>
        <span>Stadium Simulator</span>
      </div>
      <div className="header-badge">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        <span>AI-Powered Crowd Management</span>
      </div>
    </header>
  );
};

export default Header;
