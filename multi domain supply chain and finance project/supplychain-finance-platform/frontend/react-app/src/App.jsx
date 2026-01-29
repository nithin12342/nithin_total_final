import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/index.jsx';
import DashboardPage from './pages/dashboard.jsx';
import AIAnalyticsPage from './pages/AIAnalytics.jsx';
import ModelMonitoringPage from './pages/ModelMonitoring.jsx';
import PrivateRoute from './components/PrivateRoute.jsx';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route 
        path="/dashboard"
        element={
          <PrivateRoute>
            <DashboardPage />
          </PrivateRoute>
        }
      />
      <Route 
        path="/ai-analytics"
        element={
          <PrivateRoute>
            <AIAnalyticsPage />
          </PrivateRoute>
        }
      />
      <Route 
        path="/model-monitoring"
        element={
          <PrivateRoute>
            <ModelMonitoringPage />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<LoginPage />} />
    </Routes>
  );
}

export default App;