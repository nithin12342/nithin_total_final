import React from 'react';
import { useAuth } from '../hooks/useAuth';
import Chart from '../components/Chart';
import { api } from '../services/api';

const DashboardPage = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = React.useState({
    totalTransactions: 0,
    activeShipments: 0,
    pendingInvoices: 0,
    monthlyVolume: 0
  });
  const [supplyChainMetrics, setSupplyChainMetrics] = React.useState({});
  const [demandForecasts, setDemandForecasts] = React.useState([]);
  const [riskAssessments, setRiskAssessments] = React.useState([]);
  const [recentTransactions, setRecentTransactions] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [
          metricsData, 
          transactionsData,
          supplyChainMetricsData,
          demandForecastData,
          riskAssessmentData
        ] = await Promise.all([
          api.get('/dashboard/metrics'),
          api.get('/dashboard/transactions'),
          api.get('/supply/analytics/metrics'),
          api.get('/supply/analytics/demand-forecast/PRODUCT_001'), // Example product ID
          api.get('/supply/analytics/risk-assessment/supplier/1') // Example supplier ID
        ]);
        
        setMetrics(metricsData.data);
        setRecentTransactions(transactionsData.data);
        setSupplyChainMetrics(supplyChainMetricsData.data);
        setDemandForecasts([demandForecastData.data]); // Assuming single forecast for now
        setRiskAssessments([riskAssessmentData.data]); // Assuming single assessment for now
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>Welcome, {user.name}</h1>
        <div className="date">{new Date().toLocaleDateString()}</div>
      </header>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Transactions</h3>
          <p>{metrics.totalTransactions}</p>
        </div>
        <div className="metric-card">
          <h3>Active Shipments</h3>
          <p>{metrics.activeShipments}</p>
        </div>
        <div className="metric-card">
          <h3>Pending Invoices</h3>
          <p>{metrics.pendingInvoices}</p>
        </div>
        <div className="metric-card">
          <h3>Monthly Volume</h3>
          <p>${metrics.monthlyVolume.toLocaleString()}</p>
        </div>
      </div>

      {/* AI/ML Enhanced Analytics Section */}
      <div className="ai-analytics-section">
        <h2>AI-Powered Insights</h2>
        
        {/* Demand Forecasting */}
        <div className="forecast-section">
          <h3>Demand Forecast</h3>
          {demandForecasts.map((forecast, index) => (
            <div key={index} className="forecast-card">
              <p>Product: {forecast.productId}</p>
              <p>Predicted Demand: {forecast.predictedDemand}</p>
              <p>Confidence: {(forecast.confidenceLevel * 100).toFixed(1)}%</p>
              <p>Period: {forecast.period}</p>
            </div>
          ))}
        </div>
        
        {/* Risk Assessment */}
        <div className="risk-section">
          <h3>Supplier Risk Assessment</h3>
          {riskAssessments.map((assessment, index) => (
            <div key={index} className="risk-card">
              <p>Supplier ID: {assessment.supplierId}</p>
              <p>Risk Score: {assessment.riskScore.toFixed(2)}</p>
              <p>Risk Level: 
                <span className={`risk-level risk-${assessment.riskLevel.toLowerCase()}`}>
                  {assessment.riskLevel}
                </span>
              </p>
              <p>Confidence: {(assessment.confidenceLevel * 100).toFixed(1)}%</p>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-container">
          <h2>Transaction Volume</h2>
          <Chart
            type="line"
            data={recentTransactions.map(t => ({
              date: t.date,
              value: t.amount
            }))}
          />
        </div>
      </div>

      <div className="recent-transactions">
        <h2>Recent Transactions</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentTransactions.map(transaction => (
              <tr key={transaction.id}>
                <td>{new Date(transaction.date).toLocaleDateString()}</td>
                <td>{transaction.type}</td>
                <td>${transaction.amount.toLocaleString()}</td>
                <td>
                  <span className={`status status-${transaction.status.toLowerCase()}`}>
                    {transaction.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DashboardPage;