import React, { useState, useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress, Alert, Snackbar } from '@mui/material';
import { registerMicroApps, start, initGlobalState } from 'qiankun';
import { MicroFrontendLoader } from './components/MicroFrontendLoader';
import { Navigation } from './components/Navigation';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ErrorFallback } from './components/ErrorFallback';
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';
import { useNotifications } from './hooks/useNotifications';
import { GlobalStateProvider } from './contexts/GlobalStateContext';
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import './App.css';

/**
 * Advanced Micro-Frontends Shell Application
 * 
 * This shell demonstrates:
 * - Module Federation with Webpack 5
 * - Single-SPA integration
 * - Advanced routing and state management
 * - Error boundaries and fallbacks
 * - Performance optimization
 * - Security and authentication
 * - Real-time communication between micro-frontends
 * - Advanced UI/UX patterns
 */

// Lazy load micro-frontend components
const AuthMicroFrontend = React.lazy(() => import('./micro-frontends/AuthMicroFrontend'));
const SupplyChainMicroFrontend = React.lazy(() => import('./micro-frontends/SupplyChainMicroFrontend'));
const FinanceMicroFrontend = React.lazy(() => import('./micro-frontends/FinanceMicroFrontend'));
const AnalyticsMicroFrontend = React.lazy(() => import('./micro-frontends/AnalyticsMicroFrontend'));

// Create Material-UI theme
const createAppTheme = (mode) => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#90caf9' : '#1976d2',
    },
    secondary: {
      main: mode === 'dark' ? '#f48fb1' : '#dc004e',
    },
    background: {
      default: mode === 'dark' ? '#121212' : '#f5f5f5',
      paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: mode === 'dark' 
            ? '0 4px 6px rgba(0, 0, 0, 0.3)' 
            : '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
});

// Global state management
const globalState = initGlobalState({
  user: null,
  theme: 'light',
  notifications: [],
  cart: [],
  preferences: {},
});

// Micro-frontend configuration
const microApps = [
  {
    name: 'auth',
    entry: process.env.REACT_APP_AUTH_URL || '//localhost:3001',
    container: '#auth-container',
    activeRule: '/auth',
    props: {
      globalState,
      theme: 'light',
    },
  },
  {
    name: 'supply-chain',
    entry: process.env.REACT_APP_SUPPLY_CHAIN_URL || '//localhost:3002',
    container: '#supply-chain-container',
    activeRule: '/supply-chain',
    props: {
      globalState,
      theme: 'light',
    },
  },
  {
    name: 'finance',
    entry: process.env.REACT_APP_FINANCE_URL || '//localhost:3003',
    container: '#finance-container',
    activeRule: '/finance',
    props: {
      globalState,
      theme: 'light',
    },
  },
  {
    name: 'analytics',
    entry: process.env.REACT_APP_ANALYTICS_URL || '//localhost:3004',
    container: '#analytics-container',
    activeRule: '/analytics',
    props: {
      globalState,
      theme: 'light',
    },
  },
];

// Error boundary for micro-frontends
const MicroFrontendErrorBoundary = ({ children, fallback }) => (
  <ErrorBoundary
    FallbackComponent={fallback || ErrorFallback}
    onError={(error, errorInfo) => {
      console.error('Micro-frontend error:', error, errorInfo);
      // Send error to monitoring service
      if (window.gtag) {
        window.gtag('event', 'exception', {
          description: error.toString(),
          fatal: false,
        });
      }
    }}
  >
    {children}
  </ErrorBoundary>
);

// Main App component
const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { notifications, addNotification, removeNotification } = useNotifications();

  // Initialize micro-frontends
  useEffect(() => {
    const initializeMicroFrontends = async () => {
      try {
        // Register micro-apps
        registerMicroApps(microApps, {
          beforeLoad: (app) => {
            console.log(`Loading micro-frontend: ${app.name}`);
            return Promise.resolve();
          },
          beforeMount: (app) => {
            console.log(`Mounting micro-frontend: ${app.name}`);
            return Promise.resolve();
          },
          afterMount: (app) => {
            console.log(`Mounted micro-frontend: ${app.name}`);
            return Promise.resolve();
          },
          beforeUnmount: (app) => {
            console.log(`Unmounting micro-frontend: ${app.name}`);
            return Promise.resolve();
          },
          afterUnmount: (app) => {
            console.log(`Unmounted micro-frontend: ${app.name}`);
            return Promise.resolve();
          },
        });

        // Start qiankun
        await start({
          sandbox: {
            strictStyleIsolation: true,
            experimentalStyleIsolation: true,
          },
          prefetch: 'all',
          singular: false,
        });

        setIsLoading(false);
      } catch (err) {
        console.error('Failed to initialize micro-frontends:', err);
        setError('Failed to initialize application');
        setIsLoading(false);
      }
    };

    initializeMicroFrontends();
  }, []);

  // Update global state when theme changes
  useEffect(() => {
    globalState.setGlobalState({ theme });
  }, [theme]);

  // Update global state when user changes
  useEffect(() => {
    globalState.setGlobalState({ user });
  }, [user]);

  // Handle global state changes
  useEffect(() => {
    const handleGlobalStateChange = (state, prev) => {
      console.log('Global state changed:', state, prev);
      
      // Handle notifications from micro-frontends
      if (state.notifications && state.notifications !== prev.notifications) {
        state.notifications.forEach(notification => {
          addNotification(notification);
        });
      }
    };

    globalState.onGlobalStateChange(handleGlobalStateChange, true);
    
    return () => {
      globalState.offGlobalStateChange(handleGlobalStateChange);
    };
  }, [addNotification]);

  // Performance monitoring
  useEffect(() => {
    if ('performance' in window) {
      const perfData = performance.getEntriesByType('navigation')[0];
      console.log('App load time:', perfData.loadEventEnd - perfData.loadEventStart);
    }
  }, []);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        flexDirection="column"
      >
        <CircularProgress size={60} />
        <Box mt={2}>Loading Supply Chain Platform...</Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        flexDirection="column"
      >
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <button onClick={() => window.location.reload()}>
          Reload Application
        </button>
      </Box>
    );
  }

  const appTheme = createAppTheme(theme);

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline />
      <GlobalStateProvider value={globalState}>
        <AuthProvider>
          <NotificationProvider>
            <Router>
              <Box className="app">
                <Header 
                  user={user}
                  isAuthenticated={isAuthenticated}
                  theme={theme}
                  onThemeToggle={toggleTheme}
                />
                
                <Box className="app-body">
                  <Sidebar isAuthenticated={isAuthenticated} />
                  
                  <Box className="app-content">
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      
                      <Route 
                        path="/auth/*" 
                        element={
                          <MicroFrontendErrorBoundary>
                            <Suspense fallback={<MicroFrontendLoader />}>
                              <div id="auth-container" />
                            </Suspense>
                          </MicroFrontendErrorBoundary>
                        } 
                      />
                      
                      <Route 
                        path="/supply-chain/*" 
                        element={
                          isAuthenticated ? (
                            <MicroFrontendErrorBoundary>
                              <Suspense fallback={<MicroFrontendLoader />}>
                                <div id="supply-chain-container" />
                              </Suspense>
                            </MicroFrontendErrorBoundary>
                          ) : (
                            <Navigate to="/auth/login" replace />
                          )
                        } 
                      />
                      
                      <Route 
                        path="/finance/*" 
                        element={
                          isAuthenticated ? (
                            <MicroFrontendErrorBoundary>
                              <Suspense fallback={<MicroFrontendLoader />}>
                                <div id="finance-container" />
                              </Suspense>
                            </MicroFrontendErrorBoundary>
                          ) : (
                            <Navigate to="/auth/login" replace />
                          )
                        } 
                      />
                      
                      <Route 
                        path="/analytics/*" 
                        element={
                          isAuthenticated ? (
                            <MicroFrontendErrorBoundary>
                              <Suspense fallback={<MicroFrontendLoader />}>
                                <div id="analytics-container" />
                              </Suspense>
                            </MicroFrontendErrorBoundary>
                          ) : (
                            <Navigate to="/auth/login" replace />
                          )
                        } 
                      />
                      
                      <Route 
                        path="/dashboard" 
                        element={
                          isAuthenticated ? (
                            <Dashboard />
                          ) : (
                            <Navigate to="/auth/login" replace />
                          )
                        } 
                      />
                      
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </Box>
                </Box>
                
                {/* Global notifications */}
                <Snackbar
                  open={notifications.length > 0}
                  autoHideDuration={6000}
                  onClose={() => removeNotification(notifications[0]?.id)}
                >
                  {notifications.length > 0 && (
                    <Alert 
                      severity={notifications[0].type}
                      onClose={() => removeNotification(notifications[0].id)}
                    >
                      {notifications[0].message}
                    </Alert>
                  )}
                </Snackbar>
              </Box>
            </Router>
          </NotificationProvider>
        </AuthProvider>
      </GlobalStateProvider>
    </ThemeProvider>
  );
};

// Dashboard component
const Dashboard = () => {
  const [stats, setStats] = useState({
    totalOrders: 0,
    pendingShipments: 0,
    revenue: 0,
    activeUsers: 0,
  });

  useEffect(() => {
    // Fetch dashboard statistics
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <Box p={3}>
      <h1>Supply Chain Dashboard</h1>
      <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={2}>
        <Box p={2} border="1px solid #ccc" borderRadius={2}>
          <h3>Total Orders</h3>
          <p>{stats.totalOrders}</p>
        </Box>
        <Box p={2} border="1px solid #ccc" borderRadius={2}>
          <h3>Pending Shipments</h3>
          <p>{stats.pendingShipments}</p>
        </Box>
        <Box p={2} border="1px solid #ccc" borderRadius={2}>
          <h3>Revenue</h3>
          <p>${stats.revenue.toLocaleString()}</p>
        </Box>
        <Box p={2} border="1px solid #ccc" borderRadius={2}>
          <h3>Active Users</h3>
          <p>{stats.activeUsers}</p>
        </Box>
      </Box>
    </Box>
  );
};

// 404 Not Found component
const NotFound = () => (
  <Box p={3} textAlign="center">
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
  </Box>
);

export default App;

