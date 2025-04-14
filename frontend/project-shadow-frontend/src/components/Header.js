import React from 'react';
import '../styles/Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="logo">
        <div className="logo-symbol">◈</div>
        <div className="logo-text">
          <h1>PROJECT SHADOW</h1>
          <p>Directorate of Covert Operations</p>
        </div>
      </div>
      <div className="security-badge">
        <span className="classification">LEVEL 7 CLASSIFIED</span>
        <span className="secure-tag">SECURE TERMINAL</span>
      </div>
    </header>
  );
};

export default Header;