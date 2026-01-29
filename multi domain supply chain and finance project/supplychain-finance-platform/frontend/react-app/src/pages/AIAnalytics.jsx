import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './AIAnalytics.css';

const AIAnalyticsPage = () => {
  const [supplyChainMetrics, setSupplyChainMetrics] = useState({});
  const [financialMetrics, setFinancialMetrics] = useState({});
  const [demandForecasts, setDemandForecasts] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState('PRODUCT_001');
  const [selectedSupplier, setSelectedSupplier] = useState('1');
  const [forecastPeriod, setForecastPeriod] = useState('WEEKLY');

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setIsLoading(true);
        const [
          metricsData,
          financialData,
          forecastData,
          riskData
        ] = await Promise.all([
          api.get('/supply/analytics/metrics'),
          api.get('/supply/analytics/financial'),
          api.get(`/supply/analytics/demand-forecast/${selectedProduct}`, { params: { period: forecastPeriod } }),
          api.get(`/supply/analytics/risk-assessment/supplier/${selectedSupplier}`)
        ]);

        setSupplyChainMetrics(metricsData.data);
        setFinancialMetrics(financialData.data);
        setDemandForecasts([forecastData.data]);
        setRiskAssessments([riskData.data]);
      } catch (error) {
        console.error('Error fetching analytics data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [selectedProduct, selectedSupplier, forecastPeriod]);

  const handleForecastRequest = async () => {
    try {
      const response = await api.get(`/supply/analytics/demand-forecast/${selectedProduct}`, { 
        params: { period: forecastPeriod } 
      });
      setDemandForecasts([response.data]);
    } catch (error) {
      console.error('Error fetching demand forecast:', error);
    }
  };

  const handleRiskAssessmentRequest = async () => {
    try {
      const response = await api.get(`/supply/analytics/risk-assessment/supplier/${selectedSupplier}`);
      setRiskAssessments([response.data]);
    } catch (error) {
      console.error('Error fetching risk assessment:', error);
    }
  };

  if (isLoading) {
    return <div className="ai-analytics-page">Loading AI analytics...</div>;
  }

  return (
    <div className="ai-analytics-page">
      <header className="page-header">
        <h1>AI-Powered Analytics</h1>
        <p>Advanced insights powered by machine learning</p>
      </header>

      {/* Key Metrics Dashboard */}
      <section className="metrics-dashboard">
        <h2>Supply Chain Overview</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Total Inventory Items</h3>
            <p>{supplyChainMetrics.totalInventoryItems || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Active Shipments</h3>
            <p>{supplyChainMetrics.activeShipments || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Pending Orders</h3>
            <p>{supplyChainMetrics.pendingOrders || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Inventory Value</h3>
            <p>${(financialMetrics.totalInventoryValue || 0).toLocaleString()}</p>
          </div>
        </div>
      </section>

      {/* Demand Forecasting Section */}
      <section className="forecasting-section">
        <h2>Demand Forecasting</h2>
        <div className="forecast-controls">
          <div className="control-group">
            <label htmlFor="product-select">Product ID:</label>
            <input
              type="text"
              id="product-select"
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              placeholder="Enter product ID"
            />
          </div>
          <div className="control-group">
            <label htmlFor="period-select">Period:</label>
            <select
              id="period-select"
              value={forecastPeriod}
              onChange={(e) => setForecastPeriod(e.target.value)}
            >
              <option value="DAILY">Daily</option>
              <option value="WEEKLY">Weekly</option>
              <option value="MONTHLY">Monthly</option>
            </select>
          </div>
          <button onClick={handleForecastRequest}>Generate Forecast</button>
        </div>

        <div className="forecast-results">
          {demandForecasts.map((forecast, index) => (
            <div key={index} className="forecast-card">
              <h3>Demand Forecast for {forecast.productId}</h3>
              <div className="forecast-details">
                <p><strong>Predicted Demand:</strong> {forecast.predictedDemand} units</p>
                <p><strong>Confidence Level:</strong> {(forecast.confidenceLevel * 100).toFixed(1)}%</p>
                <p><strong>Forecast Period:</strong> {forecast.period}</p>
                <p><strong>Forecast Date:</strong> {new Date(forecast.forecastDate).toLocaleDateString()}</p>
              </div>
              <div className="confidence-meter">
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${forecast.confidenceLevel * 100}%` }}
                  ></div>
                </div>
                <span>Confidence</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Risk Assessment Section */}
      <section className="risk-assessment-section">
        <h2>Supplier Risk Assessment</h2>
        <div className="risk-controls">
          <div className="control-group">
            <label htmlFor="supplier-select">Supplier ID:</label>
            <input
              type="text"
              id="supplier-select"
              value={selectedSupplier}
              onChange={(e) => setSelectedSupplier(e.target.value)}
              placeholder="Enter supplier ID"
            />
          </div>
          <button onClick={handleRiskAssessmentRequest}>Assess Risk</button>
        </div>

        <div className="risk-results">
          {riskAssessments.map((assessment, index) => (
            <div key={index} className="risk-card">
              <h3>Risk Assessment for Supplier {assessment.supplierId}</h3>
              <div className="risk-details">
                <p><strong>Risk Score:</strong> {assessment.riskScore.toFixed(2)}</p>
                <p><strong>Risk Level:</strong> 
                  <span className={`risk-badge risk-${assessment.riskLevel.toLowerCase()}`}>
                    {assessment.riskLevel}
                  </span>
                </p>
                <p><strong>Confidence Level:</strong> {(assessment.confidenceLevel * 100).toFixed(1)}%</p>
                <p><strong>Assessment Date:</strong> {new Date(assessment.assessmentDate).toLocaleDateString()}</p>
              </div>
              <div className="risk-meter">
                <div className="risk-bar">
                  <div 
                    className={`risk-fill risk-${assessment.riskLevel.toLowerCase()}`}
                    style={{ width: `${assessment.riskScore * 100}%` }}
                  ></div>
                </div>
                <span>Risk Level</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Fraud Detection Section */}
      <section className="fraud-detection-section">
        <h2>Fraud Detection</h2>
        <div className="fraud-overview">
          <p>Fraud detection algorithms continuously monitor transactions for suspicious patterns.</p>
          <p>High-risk transactions are flagged for review with detailed risk scores and explanations.</p>
        </div>
      </section>
    </div>
  );
};

export default AIAnalyticsPage;