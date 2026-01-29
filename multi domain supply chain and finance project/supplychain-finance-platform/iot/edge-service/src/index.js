const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mqtt = require('mqtt');
const winston = require('winston');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const path = require('path');

// Import edge computing modules
const { EdgeDataProcessor } = require('./edge-processor');
const { PredictiveMaintenanceEngine } = require('./maintenance-engine');
const { DigitalTwinManager } = require('./digital-twin');
const { RealTimeAnalytics } = require('./analytics');

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'edge-service.log' })
  ]
});

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Initialize edge computing components
const edgeProcessor = new EdgeDataProcessor();
const maintenanceEngine = new PredictiveMaintenanceEngine();
const digitalTwinManager = new DigitalTwinManager();
const analytics = new RealTimeAnalytics();

// MQTT Configuration
const MQTT_BROKER_URL = process.env.MQTT_BROKER_URL || 'mqtt://localhost:1883';
const mqttClient = mqtt.connect(MQTT_BROKER_URL);

// MQTT Connection Events
mqttClient.on('connect', () => {
  logger.info('Connected to MQTT broker');
  mqttClient.subscribe('supplychain/iot/sensors/#');
  mqttClient.subscribe('supplychain/iot/devices/#');
});

mqttClient.on('error', (error) => {
  logger.error('MQTT connection error:', error);
});

// Handle incoming MQTT messages
mqttClient.on('message', (topic, message) => {
  try {
    const data = JSON.parse(message.toString());
    handleSensorData(topic, data);
  } catch (error) {
    logger.error('Error parsing MQTT message:', error);
  }
});

// Handle sensor data
async function handleSensorData(topic, data) {
  try {
    // Process data at the edge
    const processedData = await edgeProcessor.process(data);
    
    // Update digital twin
    const twinState = await digitalTwinManager.updateState(data.deviceId, processedData);
    
    // Perform predictive maintenance analysis
    const maintenanceResult = await maintenanceEngine.analyze(data.deviceId, processedData);
    
    // Perform real-time analytics
    const analyticsResult = await analytics.process(processedData);
    
    // Emit results via WebSocket
    io.emit('sensorData', {
      deviceId: data.deviceId,
      timestamp: new Date(),
      rawData: data,
      processedData,
      twinState,
      maintenanceResult,
      analyticsResult
    });
    
    // Forward processed data to cloud if needed
    if (processedData.forwardToCloud) {
      mqttClient.publish('supplychain/iot/processed', JSON.stringify(processedData));
    }
    
    logger.info(`Processed data from device ${data.deviceId}`);
  } catch (error) {
    logger.error('Error processing sensor data:', error);
  }
}

// REST API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date() });
});

app.get('/api/devices/:deviceId/state', async (req, res) => {
  try {
    const { deviceId } = req.params;
    const state = await digitalTwinManager.getState(deviceId);
    res.json(state);
  } catch (error) {
    logger.error('Error getting device state:', error);
    res.status(500).json({ error: 'Failed to get device state' });
  }
});

app.get('/api/devices/:deviceId/maintenance', async (req, res) => {
  try {
    const { deviceId } = req.params;
    const maintenance = await maintenanceEngine.getRecommendations(deviceId);
    res.json(maintenance);
  } catch (error) {
    logger.error('Error getting maintenance recommendations:', error);
    res.status(500).json({ error: 'Failed to get maintenance recommendations' });
  }
});

app.get('/api/analytics', async (req, res) => {
  try {
    const stats = await analytics.getStats();
    res.json(stats);
  } catch (error) {
    logger.error('Error getting analytics:', error);
    res.status(500).json({ error: 'Failed to get analytics' });
  }
});

// WebSocket connection handling
io.on('connection', (socket) => {
  logger.info('New WebSocket connection');
  
  socket.on('disconnect', () => {
    logger.info('WebSocket disconnected');
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 3005;
server.listen(PORT, () => {
  logger.info(`Edge Computing Service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

module.exports = app;