class EdgeDataProcessor {
  constructor() {
    this.processingRules = new Map();
    this.dataCache = new Map();
    this.cacheExpiry = 60000; // 1 minute
    this.initializeProcessingRules();
  }

  initializeProcessingRules() {
    // Temperature sensor processing rules
    this.processingRules.set('temperature', (data) => {
      const processed = {
        ...data,
        processedValue: this.applyCalibration(data.value, 'temperature'),
        anomaly: this.detectAnomaly(data.value, 'temperature'),
        trend: this.calculateTrend(data.deviceId, data.value, 'temperature'),
        quality: this.assessQuality(data),
        forwardToCloud: this.shouldForwardToCloud(data, 'temperature')
      };
      return processed;
    });

    // Humidity sensor processing rules
    this.processingRules.set('humidity', (data) => {
      const processed = {
        ...data,
        processedValue: this.applyCalibration(data.value, 'humidity'),
        anomaly: this.detectAnomaly(data.value, 'humidity'),
        trend: this.calculateTrend(data.deviceId, data.value, 'humidity'),
        quality: this.assessQuality(data),
        forwardToCloud: this.shouldForwardToCloud(data, 'humidity')
      };
      return processed;
    });

    // Pressure sensor processing rules
    this.processingRules.set('pressure', (data) => {
      const processed = {
        ...data,
        processedValue: this.applyCalibration(data.value, 'pressure'),
        anomaly: this.detectAnomaly(data.value, 'pressure'),
        trend: this.calculateTrend(data.deviceId, data.value, 'pressure'),
        quality: this.assessQuality(data),
        forwardToCloud: this.shouldForwardToCloud(data, 'pressure')
      };
      return processed;
    });

    // GPS sensor processing rules
    this.processingRules.set('gps', (data) => {
      const processed = {
        ...data,
        processedValue: data.value,
        anomaly: this.detectLocationAnomaly(data.value),
        distance: this.calculateDistance(data.deviceId, data.value),
        speed: this.calculateSpeed(data.deviceId, data.value),
        quality: this.assessQuality(data),
        forwardToCloud: this.shouldForwardToCloud(data, 'gps')
      };
      return processed;
    });
  }

  async process(data) {
    try {
      const sensorType = data.sensorType || 'generic';
      const rule = this.processingRules.get(sensorType) || this.getDefaultProcessor();
      
      // Apply processing rule
      const processedData = rule(data);
      
      // Cache the processed data
      this.cacheData(data.deviceId, sensorType, processedData);
      
      return processedData;
    } catch (error) {
      console.error('Error processing data:', error);
      return { ...data, error: true, errorMessage: error.message };
    }
  }

  applyCalibration(value, sensorType) {
    // Apply sensor-specific calibration
    const calibrationFactors = {
      temperature: { offset: 0.5, scale: 1.0 },
      humidity: { offset: 2.0, scale: 0.98 },
      pressure: { offset: 0.0, scale: 1.02 }
    };

    const factors = calibrationFactors[sensorType] || { offset: 0, scale: 1 };
    return (value * factors.scale) + factors.offset;
  }

  detectAnomaly(value, sensorType) {
    // Simple statistical anomaly detection
    const thresholds = {
      temperature: { min: -40, max: 85 },
      humidity: { min: 0, max: 100 },
      pressure: { min: 900, max: 1100 }
    };

    const threshold = thresholds[sensorType];
    if (threshold) {
      return value < threshold.min || value > threshold.max;
    }

    return false;
  }

  detectLocationAnomaly(location) {
    // Basic location validation
    const [lat, lon] = location;
    return lat < -90 || lat > 90 || lon < -180 || lon > 180;
  }

  calculateTrend(deviceId, value, sensorType) {
    // Calculate trend based on historical data
    const key = `${deviceId}-${sensorType}`;
    if (!this.dataCache.has(key)) {
      this.dataCache.set(key, []);
    }

    const history = this.dataCache.get(key);
    history.push({ value, timestamp: Date.now() });

    // Keep only last 10 readings
    if (history.length > 10) {
      history.shift();
    }

    if (history.length < 2) {
      return 'stable';
    }

    const recent = history[history.length - 1].value;
    const previous = history[history.length - 2].value;
    const diff = recent - previous;

    if (Math.abs(diff) < 0.1) return 'stable';
    if (diff > 0) return 'increasing';
    return 'decreasing';
  }

  calculateDistance(deviceId, location) {
    // Calculate distance from last known location
    const key = `${deviceId}-location`;
    const lastLocation = this.dataCache.get(key);

    if (!lastLocation) {
      this.dataCache.set(key, location);
      return 0;
    }

    // Simple Euclidean distance (in practice, use Haversine formula)
    const [lat1, lon1] = lastLocation;
    const [lat2, lon2] = location;
    const distance = Math.sqrt(Math.pow(lat2 - lat1, 2) + Math.pow(lon2 - lon1, 2));
    
    this.dataCache.set(key, location);
    return distance;
  }

  calculateSpeed(deviceId, location) {
    // Calculate speed based on distance and time
    const key = `${deviceId}-location-timestamp`;
    const lastTimestamp = this.dataCache.get(key);
    const currentTimestamp = Date.now();

    if (!lastTimestamp) {
      this.dataCache.set(key, currentTimestamp);
      return 0;
    }

    const distance = this.calculateDistance(deviceId, location);
    const timeDiff = (currentTimestamp - lastTimestamp) / 1000; // seconds
    const speed = timeDiff > 0 ? distance / timeDiff : 0;

    this.dataCache.set(key, currentTimestamp);
    return speed;
  }

  assessQuality(data) {
    // Assess data quality based on various factors
    let qualityScore = 1.0;

    // Check for missing fields
    if (!data.deviceId || !data.timestamp || data.value === undefined) {
      qualityScore -= 0.3;
    }

    // Check for anomaly
    if (data.anomaly) {
      qualityScore -= 0.2;
    }

    // Check timestamp freshness
    const age = Date.now() - new Date(data.timestamp).getTime();
    if (age > 300000) { // 5 minutes
      qualityScore -= 0.1;
    }

    return Math.max(0, qualityScore);
  }

  shouldForwardToCloud(data, sensorType) {
    // Determine if data should be forwarded to cloud
    // Forward if: anomaly detected, quality is high, or periodic sync
    return data.anomaly || 
           data.quality > 0.8 || 
           Math.random() < 0.1; // 10% random sampling
  }

  cacheData(deviceId, sensorType, data) {
    const key = `${deviceId}-${sensorType}`;
    this.dataCache.set(key, {
      data,
      timestamp: Date.now()
    });

    // Set timeout to expire cache entry
    setTimeout(() => {
      if (this.dataCache.has(key)) {
        const cached = this.dataCache.get(key);
        if (cached.timestamp === this.dataCache.get(key).timestamp) {
          this.dataCache.delete(key);
        }
      }
    }, this.cacheExpiry);
  }

  getDefaultProcessor() {
    return (data) => ({
      ...data,
      processedValue: data.value,
      anomaly: false,
      trend: 'unknown',
      quality: 0.5,
      forwardToCloud: true
    });
  }

  getCacheStats() {
    return {
      size: this.dataCache.size,
      expiryTime: this.cacheExpiry
    };
  }
}

module.exports = { EdgeDataProcessor };