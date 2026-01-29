class PredictiveMaintenanceEngine {
  constructor() {
    this.deviceModels = new Map();
    this.maintenanceHistory = new Map();
    this.failurePredictions = new Map();
    this.initializeModels();
  }

  initializeModels() {
    // In a real implementation, these would be loaded ML models
    // For this example, we'll use rule-based approaches
    
    this.deviceModels.set('temperature_sensor', {
      type: 'sensor',
      criticalThreshold: 75,
      warningThreshold: 65,
      failureProbability: this.calculateFailureProbability
    });
    
    this.deviceModels.set('humidity_sensor', {
      type: 'sensor',
      criticalThreshold: 85,
      warningThreshold: 75,
      failureProbability: this.calculateFailureProbability
    });
    
    this.deviceModels.set('pressure_sensor', {
      type: 'sensor',
      criticalThreshold: 1050,
      warningThreshold: 1000,
      failureProbability: this.calculateFailureProbability
    });
    
    this.deviceModels.set('gps_tracker', {
      type: 'tracker',
      criticalThreshold: 100, // km/h
      warningThreshold: 80,   // km/h
      failureProbability: this.calculateGPSTrackerFailure
    });
  }

  async analyze(deviceId, processedData) {
    try {
      const deviceType = this.getDeviceType(deviceId);
      const model = this.deviceModels.get(deviceType);
      
      if (!model) {
        return {
          deviceId,
          status: 'unknown',
          recommendations: ['Device type not recognized'],
          failureRisk: 0.0,
          nextMaintenance: null
        };
      }
      
      // Calculate failure probability
      const failureProb = model.failureProbability(processedData, model);
      
      // Determine status
      const status = this.determineStatus(failureProb, processedData, model);
      
      // Generate recommendations
      const recommendations = this.generateRecommendations(status, processedData, model);
      
      // Predict next maintenance
      const nextMaintenance = this.predictNextMaintenance(deviceId, status, failureProb);
      
      // Store results
      const result = {
        deviceId,
        status,
        recommendations,
        failureRisk: failureProb,
        nextMaintenance,
        timestamp: new Date()
      };
      
      this.failurePredictions.set(deviceId, result);
      
      return result;
    } catch (error) {
      console.error('Error in predictive maintenance analysis:', error);
      return {
        deviceId,
        status: 'error',
        recommendations: ['Analysis failed'],
        failureRisk: 0.0,
        nextMaintenance: null,
        error: error.message
      };
    }
  }

  getDeviceType(deviceId) {
    // Simple device type inference based on ID
    if (deviceId.includes('temp')) return 'temperature_sensor';
    if (deviceId.includes('hum')) return 'humidity_sensor';
    if (deviceId.includes('pres')) return 'pressure_sensor';
    if (deviceId.includes('gps')) return 'gps_tracker';
    return 'generic_device';
  }

  calculateFailureProbability(data, model) {
    // Calculate failure probability based on sensor readings
    const value = data.processedValue || data.value;
    
    if (value >= model.criticalThreshold) {
      return 0.9; // 90% chance of failure
    } else if (value >= model.warningThreshold) {
      return 0.5; // 50% chance of failure
    } else {
      // Exponential decay based on distance from warning threshold
      const ratio = value / model.warningThreshold;
      return Math.max(0, Math.min(0.4, ratio * 0.4));
    }
  }

  calculateGPSTrackerFailure(data, model) {
    // Special handling for GPS trackers
    const speed = data.speed || 0;
    
    if (speed >= model.criticalThreshold) {
      return 0.8; // 80% chance of failure
    } else if (speed >= model.warningThreshold) {
      return 0.3; // 30% chance of failure
    } else {
      return 0.1; // 10% chance of failure
    }
  }

  determineStatus(failureProb, data, model) {
    if (failureProb >= 0.8) {
      return 'critical';
    } else if (failureProb >= 0.5 || data.anomaly) {
      return 'warning';
    } else {
      return 'normal';
    }
  }

  generateRecommendations(status, data, model) {
    const recommendations = [];
    
    switch (status) {
      case 'critical':
        recommendations.push('IMMEDIATE ACTION REQUIRED');
        recommendations.push('Shut down device to prevent damage');
        recommendations.push('Schedule emergency maintenance');
        break;
        
      case 'warning':
        recommendations.push('Monitor device closely');
        recommendations.push('Schedule maintenance within 48 hours');
        if (data.anomaly) {
          recommendations.push('Investigate anomalous readings');
        }
        break;
        
      case 'normal':
        recommendations.push('Device operating normally');
        recommendations.push('Continue regular monitoring');
        break;
    }
    
    // Add generic recommendations based on data quality
    if (data.quality < 0.7) {
      recommendations.push('Check sensor calibration');
      recommendations.push('Verify data transmission');
    }
    
    // Add trend-based recommendations
    if (data.trend === 'increasing' && data.processedValue > model.warningThreshold * 0.8) {
      recommendations.push('Monitor increasing trend');
    } else if (data.trend === 'decreasing' && data.processedValue < model.warningThreshold * 0.5) {
      recommendations.push('Monitor decreasing trend');
    }
    
    return recommendations;
  }

  predictNextMaintenance(deviceId, status, failureProb) {
    const now = new Date();
    
    // Get maintenance history for this device
    const history = this.maintenanceHistory.get(deviceId) || [];
    
    if (status === 'critical') {
      // Critical - immediate maintenance needed
      return new Date(now.getTime() + 1000 * 60 * 60); // 1 hour
    } else if (status === 'warning') {
      // Warning - maintenance within 48 hours
      return new Date(now.getTime() + 1000 * 60 * 60 * 48); // 48 hours
    } else {
      // Normal - schedule based on failure probability
      const days = Math.max(7, 30 * (1 - failureProb)); // 7-30 days
      return new Date(now.getTime() + 1000 * 60 * 60 * 24 * days);
    }
  }

  async getRecommendations(deviceId) {
    const prediction = this.failurePredictions.get(deviceId);
    if (prediction) {
      return {
        deviceId,
        ...prediction
      };
    }
    
    return {
      deviceId,
      status: 'unknown',
      recommendations: ['No recent analysis available'],
      failureRisk: 0.0,
      nextMaintenance: null
    };
  }

  recordMaintenance(deviceId, maintenanceType, notes = '') {
    if (!this.maintenanceHistory.has(deviceId)) {
      this.maintenanceHistory.set(deviceId, []);
    }
    
    const maintenanceRecord = {
      timestamp: new Date(),
      type: maintenanceType,
      notes,
      performedBy: 'edge_system'
    };
    
    this.maintenanceHistory.get(deviceId).push(maintenanceRecord);
    
    // Clear failure prediction after maintenance
    this.failurePredictions.delete(deviceId);
  }

  getSystemStats() {
    const totalDevices = this.failurePredictions.size;
    const criticalDevices = Array.from(this.failurePredictions.values())
      .filter(pred => pred.status === 'critical').length;
    const warningDevices = Array.from(this.failurePredictions.values())
      .filter(pred => pred.status === 'warning').length;
    
    return {
      totalDevices,
      criticalDevices,
      warningDevices,
      normalDevices: totalDevices - criticalDevices - warningDevices
    };
  }
}

module.exports = { PredictiveMaintenanceEngine };