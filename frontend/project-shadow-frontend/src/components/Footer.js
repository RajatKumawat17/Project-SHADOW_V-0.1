import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>RAW Intelligence Retrieval System (RIRS)</p>
        <p className="security-notice">Unauthorized access is prohibited and punishable under national security laws.</p>
      </div>
      <div className="footer-classification">
        <span>CLASSIFIED // LEVEL 7 // DCO</span>
      </div>
    </footer>
  );
};

export default Footer;