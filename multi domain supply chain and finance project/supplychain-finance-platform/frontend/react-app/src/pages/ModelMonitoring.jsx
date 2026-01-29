import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './ModelMonitoring.css';

const ModelMonitoringPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRetraining, setIsRetraining] = useState(false);

  useEffect(() => {
    fetchModelMetrics();
  }, []);

  const fetchModelMetrics = async () => {
    try {
      setIsLoading(true);
      const response = await api.getModelPerformanceMetrics();
      setMetrics(response.data);
    } catch (err) {
      setError('Failed to fetch model metrics');
      console.error('Error fetching model metrics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetrainModels = async () => {
    try {
      setIsRetraining(true);
      await api.triggerModelRetraining();
      // Refresh metrics after retraining
      setTimeout(fetchModelMetrics, 2000);
    } catch (err) {
      setError('Failed to trigger model retraining');
      console.error('Error triggering model retraining:', err);
    } finally {
      setIsRetraining(false);
    }
  };

  if (isLoading) {
    return <div className="model-monitoring-page">Loading model metrics...</div>;
  }

  if (error) {
    return <div className="model-monitoring-page error">{error}</div>;
  }

  return (
    <div className="model-monitoring-page">
      <header className="page-header">
        <h1>AI Model Monitoring</h1>
        <p>Performance metrics and monitoring for AI/ML models</p>
      </header>

      <div className="metrics-dashboard">
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Demand Forecasting Accuracy</h3>
            <div className="metric-value">
              {(metrics.data.demandForecastAccuracy * 100).toFixed(1)}%
            </div>
            <div className="metric-status">
              {metrics.data.demandForecastAccuracy >= 0.8 ? (
                <span className="status-good">Good</span>
              ) : (
                <span className="status-poor">Needs Attention</span>
              )}
            </div>
          </div>

          <div className="metric-card">
            <h3>Fraud Detection Accuracy</h3>
            <div className="metric-value">
              {(metrics.data.fraudDetectionAccuracy * 100).toFixed(1)}%
            </div>
            <div className="metric-status">
              {metrics.data.fraudDetectionAccuracy >= 0.9 ? (
                <span className="status-good">Good</span>
              ) : (
                <span className="status-poor">Needs Attention</span>
              )}
            </div>
          </div>

          <div className="metric-card">
            <h3>Risk Assessment Accuracy</h3>
            <div className="metric-value">
              {(metrics.data.riskAssessmentAccuracy * 100).toFixed(1)}%
            </div>
            <div className="metric-status">
              {metrics.data.riskAssessmentAccuracy >= 0.85 ? (
                <span className="status-good">Good</span>
              ) : (
                <span className="status-poor">Needs Attention</span>
              )}
            </div>
          </div>
        </div>

        <div className="last-updated">
          Last updated: {new Date(metrics.data.lastUpdated).toLocaleString()}
        </div>

        <div className="actions">
          <button 
            className="retrain-button" 
            onClick={handleRetrainModels}
            disabled={isRetraining}
          >
            {isRetraining ? 'Retraining...' : 'Retrain All Models'}
          </button>
        </div>
      </div>

      <div className="thresholds-info">
        <h3>Performance Thresholds</h3>
        <ul>
          <li>Demand Forecasting: ≥ 80% accuracy</li>
          <li>Fraud Detection: ≥ 90% accuracy</li>
          <li>Risk Assessment: ≥ 85% accuracy</li>
        </ul>
      </div>
    </div>
  );
};

export default ModelMonitoringPage;