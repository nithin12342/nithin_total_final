import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import { useAuth } from '../hooks/useAuth';

const IndexPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="index-page">
      <div className="hero-section">
        <h1>Supply Chain Finance Platform</h1>
        <p>Revolutionizing supply chain management with blockchain and AI</p>
      </div>
      <div className="login-section">
        <LoginForm />
      </div>
      <div className="features-section">
        <h2>Key Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Supply Chain Management</h3>
            <p>End-to-end visibility and tracking</p>
          </div>
          <div className="feature-card">
            <h3>Financial Services</h3>
            <p>Invoice financing and payments</p>
          </div>
          <div className="feature-card">
            <h3>Blockchain Integration</h3>
            <p>Secure and transparent transactions</p>
          </div>
          <div className="feature-card">
            <h3>AI Analytics</h3>
            <p>Predictive insights and fraud detection</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndexPage;
