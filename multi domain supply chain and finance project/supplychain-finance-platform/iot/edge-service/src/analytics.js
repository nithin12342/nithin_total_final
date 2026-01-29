class RealTimeAnalytics {
  constructor() {
    this.metrics = {
      totalDataPoints: 0,
      processedDataPoints: 0,
      anomaliesDetected: 0,
      devicesActive: new Set(),
      sensorReadings: {},
      processingLatency: [],
      dataThroughput: []
    };
    
    this.alerts = [];
    this.maxAlerts = 100;
    this.alertThresholds = {
      anomalyRate: 0.05, // 5% anomaly rate
      latencyThreshold: 1000, // 1 second
      throughputThreshold: 100 // 100 data points per second
    };
    
    this.timeWindows = {
      '1min': 60 * 1000,
      '5min': 5 * 60 * 1000,
      '15min': 15 * 60 * 1000,
      '1hour': 60 * 60 * 1000
    };
    
    this.windowedMetrics = {};
    this.initializeWindowedMetrics();
  }

  initializeWindowedMetrics() {
    // Initialize metrics for each time window
    Object.keys(this.timeWindows).forEach(window => {
      this.windowedMetrics[window] = {
        dataPoints: 0,
        anomalies: 0,
        latencySum: 0,
        latencyCount: 0,
        devices: new Set()
      };
    });
  }

  async process(data) {
    const startTime = Date.now();
    
    try {
      // Update basic metrics
      this.metrics.totalDataPoints++;
      this.metrics.devicesActive.add(data.deviceId);
      
      // Update sensor readings count
      const sensorType = data.sensorType || 'unknown';
      this.metrics.sensorReadings[sensorType] = 
        (this.metrics.sensorReadings[sensorType] || 0) + 1;
      
      // Check for anomalies
      if (data.anomaly) {
        this.metrics.anomaliesDetected++;
        this.generateAlert('anomaly_detected', {
          deviceId: data.deviceId,
          sensorType,
          value: data.value,
          processedValue: data.processedValue
        });
      }
      
      // Update windowed metrics
      this.updateWindowedMetrics(data);
      
      // Calculate processing time
      const processingTime = Date.now() - startTime;
      this.metrics.processingLatency.push(processingTime);
      
      // Keep only last 1000 latency measurements
      if (this.metrics.processingLatency.length > 1000) {
        this.metrics.processingLatency.shift();
      }
      
      // Update throughput metrics
      this.updateThroughput(processingTime);
      
      // Check for alerts
      this.checkAlerts();
      
      this.metrics.processedDataPoints++;
      
      return {
        success: true,
        processingTime,
        metricsUpdated: true
      };
    } catch (error) {
      console.error('Error in real-time analytics:', error);
      return {
        success: false,
        error: error.message,
        processingTime: Date.now() - startTime
      };
    }
  }

  updateWindowedMetrics(data) {
    const now = Date.now();
    
    Object.keys(this.timeWindows).forEach(window => {
      const windowMetrics = this.windowedMetrics[window];
      const windowSize = this.timeWindows[window];
      
      // Update metrics
      windowMetrics.dataPoints++;
      if (data.anomaly) {
        windowMetrics.anomalies++;
      }
      windowMetrics.devices.add(data.deviceId);
      
      // Clean up old data (simplified approach)
      // In a production system, you'd use a proper time-series database
    });
  }

  updateThroughput(processingTime) {
    const now = Date.now();
    this.metrics.dataThroughput.push({
      timestamp: now,
      processingTime
    });
    
    // Keep only last 1000 throughput measurements
    if (this.metrics.dataThroughput.length > 1000) {
      this.metrics.dataThroughput.shift();
    }
  }

  checkAlerts() {
    const now = Date.now();
    
    // Check anomaly rate
    if (this.metrics.totalDataPoints > 0) {
      const anomalyRate = this.metrics.anomaliesDetected / this.metrics.totalDataPoints;
      if (anomalyRate > this.alertThresholds.anomalyRate) {
        this.generateAlert('high_anomaly_rate', {
          rate: anomalyRate,
          threshold: this.alertThresholds.anomalyRate
        });
      }
    }
    
    // Check processing latency
    if (this.metrics.processingLatency.length > 0) {
      const avgLatency = this.metrics.processingLatency.reduce((a, b) => a + b, 0) / 
                         this.metrics.processingLatency.length;
      if (avgLatency > this.alertThresholds.latencyThreshold) {
        this.generateAlert('high_latency', {
          latency: avgLatency,
          threshold: this.alertThresholds.latencyThreshold
        });
      }
    }
    
    // Check throughput
    const recentThroughput = this.calculateRecentThroughput();
    if (recentThroughput > this.alertThresholds.throughputThreshold) {
      this.generateAlert('high_throughput', {
        throughput: recentThroughput,
        threshold: this.alertThresholds.throughputThreshold
      });
    }
  }

  calculateRecentThroughput() {
    const now = Date.now();
    const oneSecondAgo = now - 1000;
    
    const recentDataPoints = this.metrics.dataThroughput.filter(
      entry => entry.timestamp > oneSecondAgo
    ).length;
    
    return recentDataPoints;
  }

  generateAlert(type, details) {
    const alert = {
      id: `${type}_${Date.now()}`,
      type,
      timestamp: new Date(),
      details,
      severity: this.determineAlertSeverity(type)
    };
    
    this.alerts.push(alert);
    
    // Keep only recent alerts
    if (this.alerts.length > this.maxAlerts) {
      this.alerts.shift();
    }
    
    // Log alert
    console.warn(`ALERT: ${type}`, details);
  }

  determineAlertSeverity(type) {
    const severityMap = {
      'anomaly_detected': 'medium',
      'high_anomaly_rate': 'high',
      'high_latency': 'high',
      'high_throughput': 'medium',
      'device_offline': 'high'
    };
    
    return severityMap[type] || 'low';
  }

  async getStats() {
    const now = Date.now();
    
    return {
      overview: {
        totalDataPoints: this.metrics.totalDataPoints,
        processedDataPoints: this.metrics.processedDataPoints,
        anomaliesDetected: this.metrics.anomaliesDetected,
        activeDevices: this.metrics.devicesActive.size,
        uptime: process.uptime()
      },
      performance: {
        avgProcessingLatency: this.calculateAverageLatency(),
        recentThroughput: this.calculateRecentThroughput(),
        processingRate: this.metrics.totalDataPoints / process.uptime()
      },
      sensorDistribution: { ...this.metrics.sensorReadings },
      alerts: {
        total: this.alerts.length,
        recent: this.alerts.slice(-10),
        bySeverity: this.aggregateAlertsBySeverity()
      },
      windowed: this.getWindowedMetrics()
    };
  }

  calculateAverageLatency() {
    if (this.metrics.processingLatency.length === 0) {
      return 0;
    }
    
    const sum = this.metrics.processingLatency.reduce((a, b) => a + b, 0);
    return sum / this.metrics.processingLatency.length;
  }

  getWindowedMetrics() {
    const result = {};
    
    Object.keys(this.windowedMetrics).forEach(window => {
      const metrics = this.windowedMetrics[window];
      result[window] = {
        dataPoints: metrics.dataPoints,
        anomalies: metrics.anomalies,
        anomalyRate: metrics.dataPoints > 0 ? metrics.anomalies / metrics.dataPoints : 0,
        activeDevices: metrics.devices.size
      };
    });
    
    return result;
  }

  aggregateAlertsBySeverity() {
    const severityCounts = {
      low: 0,
      medium: 0,
      high: 0
    };
    
    this.alerts.forEach(alert => {
      severityCounts[alert.severity]++;
    });
    
    return severityCounts;
  }

  async getAlerts(limit = 50) {
    return this.alerts.slice(-limit);
  }

  async clearAlerts() {
    this.alerts = [];
  }

  async getDeviceMetrics(deviceId) {
    // This would typically query a time-series database
    // For this example, we'll return a simplified view
    return {
      deviceId,
      totalReadings: this.metrics.sensorReadings[deviceId] || 0,
      anomalies: 'N/A', // Would require more detailed tracking
      lastSeen: 'N/A'   // Would require device-specific tracking
    };
  }

  resetMetrics() {
    this.metrics = {
      totalDataPoints: 0,
      processedDataPoints: 0,
      anomaliesDetected: 0,
      devicesActive: new Set(),
      sensorReadings: {},
      processingLatency: [],
      dataThroughput: []
    };
    
    this.initializeWindowedMetrics();
  }
}

module.exports = { RealTimeAnalytics };