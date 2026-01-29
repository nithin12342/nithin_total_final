class DigitalTwinManager {
  constructor() {
    this.twins = new Map();
    this.stateHistory = new Map();
    this.maxHistoryLength = 100;
  }

  async updateState(deviceId, processedData) {
    try {
      // Get or create digital twin
      let twin = this.twins.get(deviceId);
      if (!twin) {
        twin = this.createDigitalTwin(deviceId, processedData);
        this.twins.set(deviceId, twin);
      }

      // Update twin state
      const updatedTwin = this.applyStateUpdate(twin, processedData);
      
      // Store in history
      this.storeStateHistory(deviceId, updatedTwin);
      
      // Save updated twin
      this.twins.set(deviceId, updatedTwin);
      
      return updatedTwin;
    } catch (error) {
      console.error('Error updating digital twin state:', error);
      return null;
    }
  }

  createDigitalTwin(deviceId, initialData) {
    return {
      deviceId,
      createdAt: new Date(),
      lastUpdated: new Date(),
      state: {
        status: 'online',
        batteryLevel: initialData.batteryLevel || 100,
        signalStrength: initialData.signalStrength || 100,
        location: initialData.location || [0, 0],
        temperature: initialData.sensorType === 'temperature' ? initialData.processedValue : null,
        humidity: initialData.sensorType === 'humidity' ? initialData.processedValue : null,
        pressure: initialData.sensorType === 'pressure' ? initialData.processedValue : null,
        lastSensorReading: initialData.timestamp || new Date()
      },
      metadata: {
        deviceType: this.inferDeviceType(deviceId, initialData),
        firmwareVersion: initialData.firmwareVersion || '1.0.0',
        manufacturer: initialData.manufacturer || 'Unknown',
        model: initialData.model || 'Generic'
      },
      metrics: {
        uptime: 0,
        dataPointsProcessed: 1,
        anomaliesDetected: initialData.anomaly ? 1 : 0,
        lastMaintenance: null
      }
    };
  }

  inferDeviceType(deviceId, data) {
    if (data.sensorType) {
      return `${data.sensorType}_sensor`;
    }
    
    if (deviceId.includes('temp')) return 'temperature_sensor';
    if (deviceId.includes('hum')) return 'humidity_sensor';
    if (deviceId.includes('pres')) return 'pressure_sensor';
    if (deviceId.includes('gps')) return 'gps_tracker';
    
    return 'generic_device';
  }

  applyStateUpdate(twin, data) {
    const now = new Date();
    const timeDiff = (now - twin.lastUpdated) / 1000; // seconds
    
    // Update basic properties
    const updatedTwin = {
      ...twin,
      lastUpdated: now,
      state: {
        ...twin.state,
        status: data.anomaly ? 'anomaly' : 'online',
        batteryLevel: data.batteryLevel !== undefined ? data.batteryLevel : twin.state.batteryLevel,
        signalStrength: data.signalStrength !== undefined ? data.signalStrength : twin.state.signalStrength,
        location: data.location || twin.state.location,
        lastSensorReading: data.timestamp || twin.state.lastSensorReading
      },
      metrics: {
        ...twin.metrics,
        uptime: twin.metrics.uptime + timeDiff,
        dataPointsProcessed: twin.metrics.dataPointsProcessed + 1,
        anomaliesDetected: twin.metrics.anomaliesDetected + (data.anomaly ? 1 : 0)
      }
    };

    // Update sensor-specific values
    switch (data.sensorType) {
      case 'temperature':
        updatedTwin.state.temperature = data.processedValue;
        break;
      case 'humidity':
        updatedTwin.state.humidity = data.processedValue;
        break;
      case 'pressure':
        updatedTwin.state.pressure = data.processedValue;
        break;
      case 'gps':
        updatedTwin.state.location = data.processedValue;
        updatedTwin.state.speed = data.speed;
        break;
    }

    // Update device status based on metrics
    updatedTwin.state.status = this.determineDeviceStatus(updatedTwin);

    return updatedTwin;
  }

  determineDeviceStatus(twin) {
    // Determine overall device status based on various factors
    if (twin.state.batteryLevel < 10) {
      return 'critical_battery';
    }
    
    if (twin.state.signalStrength < 20) {
      return 'poor_connectivity';
    }
    
    const recentAnomalies = twin.metrics.anomaliesDetected;
    if (recentAnomalies > 5) {
      return 'frequent_anomalies';
    }
    
    const uptimeHours = twin.metrics.uptime / 3600;
    if (uptimeHours > 720) { // 30 days
      return 'long_uptime';
    }
    
    return twin.state.status === 'anomaly' ? 'anomaly' : 'online';
  }

  storeStateHistory(deviceId, twinState) {
    if (!this.stateHistory.has(deviceId)) {
      this.stateHistory.set(deviceId, []);
    }
    
    const history = this.stateHistory.get(deviceId);
    history.push({
      timestamp: new Date(),
      state: { ...twinState.state }
    });
    
    // Trim history to max length
    if (history.length > this.maxHistoryLength) {
      history.shift();
    }
  }

  async getState(deviceId) {
    const twin = this.twins.get(deviceId);
    if (!twin) {
      return {
        deviceId,
        error: 'Digital twin not found'
      };
    }
    
    return twin;
  }

  async getHistory(deviceId, limit = 10) {
    const history = this.stateHistory.get(deviceId);
    if (!history) {
      return [];
    }
    
    // Return last N entries
    return history.slice(-limit);
  }

  async getDeviceStats() {
    const stats = {
      totalDevices: this.twins.size,
      onlineDevices: 0,
      offlineDevices: 0,
      anomalyDevices: 0,
      criticalDevices: 0,
      deviceTypes: {}
    };

    for (const [deviceId, twin] of this.twins) {
      const deviceType = twin.metadata.deviceType;
      stats.deviceTypes[deviceType] = (stats.deviceTypes[deviceType] || 0) + 1;

      switch (twin.state.status) {
        case 'online':
          stats.onlineDevices++;
          break;
        case 'anomaly':
          stats.anomalyDevices++;
          break;
        case 'critical_battery':
        case 'poor_connectivity':
        case 'frequent_anomalies':
          stats.criticalDevices++;
          break;
        default:
          stats.offlineDevices++;
      }
    }

    return stats;
  }

  async exportTwin(deviceId) {
    const twin = this.twins.get(deviceId);
    if (!twin) {
      throw new Error(`Digital twin for device ${deviceId} not found`);
    }
    
    return JSON.stringify(twin, null, 2);
  }

  async importTwin(deviceId, twinData) {
    try {
      const twin = typeof twinData === 'string' ? JSON.parse(twinData) : twinData;
      this.twins.set(deviceId, twin);
      return true;
    } catch (error) {
      console.error('Error importing digital twin:', error);
      return false;
    }
  }

  async deleteTwin(deviceId) {
    const existed = this.twins.delete(deviceId);
    this.stateHistory.delete(deviceId);
    return existed;
  }
}

module.exports = { DigitalTwinManager };