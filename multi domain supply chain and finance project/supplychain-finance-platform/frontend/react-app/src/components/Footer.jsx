import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>About Us</h4>
          <p>Supply Chain Finance Platform - Integrating blockchain and AI for modern supply chain management.</p>
        </div>
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href="/supply-chain">Supply Chain</a></li>
            <li><a href="/finance">Finance</a></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Contact</h4>
          <ul>
            <li>Email: support@supplychain-finance.com</li>
            <li>Phone: +1 (555) 123-4567</li>
          </ul>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; 2025 Supply Chain Finance Platform. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
