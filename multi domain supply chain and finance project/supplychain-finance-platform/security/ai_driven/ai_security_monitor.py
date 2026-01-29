"""
AI-Driven Security Monitoring and Threat Detection System

This module implements advanced AI/ML techniques for real-time security monitoring,
threat detection, and automated response in the supply chain finance platform.
"""

import numpy as np
import pandas as pd
import json
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets

# ML Libraries
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam

# Security Libraries
import cryptography
from cryptography.fernet import Fernet

# Internal imports
from security.advanced.zero_trust_architecture import SecurityEvent, ThreatLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Types of security threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDoS = "ddos"
    INSIDER_THREAT = "insider_threat"
    DATA_EXFILTRATION = "data_exfiltration"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    RANSOMWARE = "ransomware"
    ZERO_DAY = "zero_day"

@dataclass
class SecurityMetric:
    """Security metric data structure"""
    metric_id: str
    timestamp: datetime
    metric_type: str
    value: float
    source: str
    metadata: Dict[str, Any]

@dataclass
class ThreatIndicator:
    """Threat indicator data structure"""
    indicator_id: str
    timestamp: datetime
    indicator_type: str
    value: str
    confidence: float
    threat_type: ThreatType
    source: str
    metadata: Dict[str, Any]

class AIThreatDetector:
    """AI-powered threat detection system"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.lstm_model = None
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.is_trained = False
        self.feature_names = []
        self.threat_patterns = {}
        self.baseline_metrics = {}
        
    def train_models(self, training_data: pd.DataFrame, labels: Optional[pd.Series] = None):
        """Train AI models on security data"""
        logger.info("Training AI threat detection models...")
        
        # Prepare features
        feature_columns = [col for col in training_data.columns if col != 'label']
        X = training_data[feature_columns]
        self.feature_names = feature_columns
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest for anomaly detection
        self.isolation_forest.fit(X_scaled)
        
        # Train Random Forest for classification (if labels provided)
        if labels is not None:
            self.random_forest.fit(X_scaled, labels)
            self.is_trained = True
        
        # Train LSTM for temporal pattern detection
        self._train_lstm_model(X_scaled)
        
        logger.info("AI threat detection models trained successfully")
    
    def _train_lstm_model(self, X_scaled: np.ndarray):
        """Train LSTM model for temporal pattern detection"""
        try:
            # Reshape data for LSTM (samples, timesteps, features)
            timesteps = 10
            n_features = X_scaled.shape[1]
            
            # Create sequences
            X_seq, y_seq = [], []
            for i in range(len(X_scaled) - timesteps):
                X_seq.append(X_scaled[i:(i + timesteps)])
                # For anomaly detection, we predict the next value
                y_seq.append(X_scaled[i + timesteps] if i + timesteps < len(X_scaled) else X_scaled[i])
            
            if len(X_seq) > 0:
                X_seq = np.array(X_seq)
                y_seq = np.array(y_seq)
                
                # Build LSTM model
                self.lstm_model = Sequential([
                    LSTM(50, return_sequences=True, input_shape=(timesteps, n_features)),
                    Dropout(0.2),
                    LSTM(50, return_sequences=False),
                    Dropout(0.2),
                    Dense(25),
                    Dense(n_features)
                ])
                
                self.lstm_model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
                
                # Train model
                self.lstm_model.fit(X_seq, y_seq, epochs=50, batch_size=32, verbose=0)
                
        except Exception as e:
            logger.error(f"Failed to train LSTM model: {e}")
    
    def detect_anomalies(self, security_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in security data"""
        if not self.is_trained and len(security_data) == 0:
            return []
        
        anomalies = []
        
        # Anomaly detection with Isolation Forest
        feature_columns = [col for col in security_data.columns if col in self.feature_names]
        if feature_columns:
            X = security_data[feature_columns]
            X_scaled = self.scaler.transform(X)
            
            # Isolation Forest predictions
            iso_predictions = self.isolation_forest.predict(X_scaled)
            iso_scores = self.isolation_forest.decision_function(X_scaled)
            
            # LSTM predictions for temporal anomalies
            lstm_anomalies = self._detect_lstm_anomalies(X_scaled)
            
            # Combine results
            for i, (iso_pred, iso_score, lstm_anom) in enumerate(zip(iso_predictions, iso_scores, lstm_anomalies)):
                if iso_pred == -1 or lstm_anom:  # Anomaly detected
                    anomaly_score = max(abs(iso_score), 0.5 if lstm_anom else 0)
                    threat_level = self._score_to_threat_level(anomaly_score)
                    
                    anomalies.append({
                        'index': i,
                        'anomaly_score': anomaly_score,
                        'threat_level': threat_level,
                        'detection_method': 'isolation_forest' if iso_pred == -1 else 'lstm',
                        'features': dict(zip(feature_columns, X.iloc[i].values))
                    })
        
        return anomalies
    
    def _detect_lstm_anomalies(self, X_scaled: np.ndarray) -> List[bool]:
        """Detect anomalies using LSTM model"""
        if self.lstm_model is None or len(X_scaled) < 10:
            return [False] * len(X_scaled)
        
        try:
            # Prepare sequences
            timesteps = 10
            sequences = []
            for i in range(len(X_scaled) - timesteps + 1):
                sequences.append(X_scaled[i:(i + timesteps)])
            
            if len(sequences) == 0:
                return [False] * len(X_scaled)
            
            sequences = np.array(sequences)
            predictions = self.lstm_model.predict(sequences, verbose=0)
            
            # Calculate reconstruction errors
            actual_values = X_scaled[timesteps-1:]
            errors = np.mean(np.abs(predictions - actual_values), axis=1)
            
            # Determine threshold (95th percentile of errors during training)
            threshold = np.percentile(errors, 95) if len(errors) > 0 else 0.1
            anomalies = errors > threshold
            
            # Pad with False for initial values
            result = [False] * (timesteps - 1) + anomalies.tolist()
            return result
            
        except Exception as e:
            logger.error(f"LSTM anomaly detection failed: {e}")
            return [False] * len(X_scaled)
    
    def classify_threat(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify threat type using trained model"""
        if not self.is_trained:
            return {'threat_type': 'unknown', 'confidence': 0.0}
        
        try:
            # Prepare feature vector
            feature_vector = np.array([[features.get(name, 0) for name in self.feature_names]])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict threat type
            prediction = self.random_forest.predict(feature_vector_scaled)[0]
            probabilities = self.random_forest.predict_proba(feature_vector_scaled)[0]
            confidence = max(probabilities)
            
            return {
                'threat_type': prediction,
                'confidence': confidence,
                'probabilities': dict(zip(self.random_forest.classes_, probabilities))
            }
        except Exception as e:
            logger.error(f"Threat classification failed: {e}")
            return {'threat_type': 'unknown', 'confidence': 0.0}
    
    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """Convert anomaly score to threat level"""
        if score > 0.8:
            return ThreatLevel.CRITICAL
        elif score > 0.6:
            return ThreatLevel.HIGH
        elif score > 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

class BehavioralAnalyzer:
    """User and entity behavior analytics"""
    
    def __init__(self):
        self.user_profiles = {}
        self.entity_profiles = {}
        self.baseline_period = timedelta(days=30)
    
    def update_user_profile(self, user_id: str, behavior_data: Dict[str, Any]):
        """Update user behavior profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'login_times': [],
                'access_patterns': [],
                'data_access_volume': [],
                'geographical_patterns': [],
                'device_usage': [],
                'session_durations': [],
                'last_updated': datetime.now()
            }
        
        profile = self.user_profiles[user_id]
        
        # Update behavior metrics
        if 'login_time' in behavior_data:
            profile['login_times'].append(behavior_data['login_time'])
        
        if 'accessed_resources' in behavior_data:
            profile['access_patterns'].extend(behavior_data['accessed_resources'])
        
        if 'data_volume' in behavior_data:
            profile['data_access_volume'].append(behavior_data['data_volume'])
        
        if 'location' in behavior_data:
            profile['geographical_patterns'].append(behavior_data['location'])
        
        if 'device_id' in behavior_data:
            profile['device_usage'].append(behavior_data['device_id'])
        
        if 'session_duration' in behavior_data:
            profile['session_durations'].append(behavior_data['session_duration'])
        
        profile['last_updated'] = datetime.now()
        
        # Keep only recent data
        self._prune_old_data(profile)
    
    def _prune_old_data(self, profile: Dict[str, Any]):
        """Remove old data beyond baseline period"""
        cutoff_time = datetime.now() - self.baseline_period
        
        for key in ['login_times', 'access_patterns', 'data_access_volume', 
                   'geographical_patterns', 'device_usage', 'session_durations']:
            if key in profile and isinstance(profile[key], list):
                # Keep only recent entries
                if key == 'login_times' and profile[key]:
                    profile[key] = [t for t in profile[key] if t > cutoff_time]
    
    def detect_behavioral_anomalies(self, user_id: str, current_behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in user behavior"""
        if user_id not in self.user_profiles:
            return {'anomaly_detected': False, 'risk_score': 0.0}
        
        profile = self.user_profiles[user_id]
        risk_score = 0.0
        anomalies = []
        
        # Check login time anomalies
        if 'login_time' in current_behavior and profile['login_times']:
            login_hour = current_behavior['login_time'].hour
            avg_login_hour = np.mean([t.hour for t in profile['login_times']])
            hour_diff = abs(login_hour - avg_login_hour)
            if hour_diff > 4:  # More than 4 hours difference
                risk_score += 0.3
                anomalies.append('unusual_login_time')
        
        # Check geographical anomalies
        if 'location' in current_behavior and profile['geographical_patterns']:
            current_loc = current_behavior['location']
            distances = []
            for loc in profile['geographical_patterns']:
                # Calculate distance (simplified)
                distance = np.sqrt((current_loc[0] - loc[0])**2 + (current_loc[1] - loc[1])**2)
                distances.append(distance)
            
            avg_distance = np.mean(distances) if distances else 0
            if avg_distance > 2.0:  # Significant geographical difference
                risk_score += 0.4
                anomalies.append('unusual_location')
        
        # Check data access volume anomalies
        if 'data_volume' in current_behavior and profile['data_access_volume']:
            current_volume = current_behavior['data_volume']
            avg_volume = np.mean(profile['data_access_volume'])
            if current_volume > avg_volume * 3:  # 3x normal volume
                risk_score += 0.3
                anomalies.append('unusual_data_access')
        
        # Check device usage anomalies
        if 'device_id' in current_behavior and profile['device_usage']:
            device_id = current_behavior['device_id']
            if device_id not in profile['device_usage']:
                risk_score += 0.2
                anomalies.append('unusual_device')
        
        return {
            'anomaly_detected': len(anomalies) > 0,
            'risk_score': min(1.0, risk_score),
            'anomalies': anomalies,
            'details': {
                'login_time_anomaly': 'unusual_login_time' in anomalies,
                'location_anomaly': 'unusual_location' in anomalies,
                'data_access_anomaly': 'unusual_data_access' in anomalies,
                'device_anomaly': 'unusual_device' in anomalies
            }
        }

class ThreatIntelligenceProcessor:
    """Process and analyze threat intelligence data"""
    
    def __init__(self):
        self.threat_indicators = {}
        self.ioc_database = {}
        self.threat_actors = {}
    
    def add_threat_indicator(self, indicator: ThreatIndicator):
        """Add a threat indicator to the database"""
        self.threat_indicators[indicator.indicator_id] = indicator
        self.ioc_database[indicator.value] = indicator
    
    def correlate_indicators(self, security_event: SecurityEvent) -> List[Dict[str, Any]]:
        """Correlate security events with threat indicators"""
        matches = []
        
        # Check IP address correlation
        if hasattr(security_event, 'source_ip') and security_event.source_ip in self.ioc_database:
            indicator = self.ioc_database[security_event.source_ip]
            matches.append({
                'type': 'ip_match',
                'indicator': indicator.indicator_id,
                'confidence': indicator.confidence,
                'threat_type': indicator.threat_type.value
            })
        
        # Check other metadata for matches
        for key, value in security_event.metadata.items():
            if isinstance(value, str) and value in self.ioc_database:
                indicator = self.ioc_database[value]
                matches.append({
                    'type': f'{key}_match',
                    'indicator': indicator.indicator_id,
                    'confidence': indicator.confidence,
                    'threat_type': indicator.threat_type.value
                })
        
        return matches
    
    def update_threat_intelligence(self, feed_data: List[Dict[str, Any]]):
        """Update threat intelligence from external feeds"""
        for item in feed_data:
            indicator = ThreatIndicator(
                indicator_id=item.get('id', secrets.token_hex(8)),
                timestamp=datetime.fromisoformat(item['timestamp']) if 'timestamp' in item else datetime.now(),
                indicator_type=item.get('type', 'unknown'),
                value=item.get('value', ''),
                confidence=item.get('confidence', 0.5),
                threat_type=ThreatType(item.get('threat_type', 'malware')),
                source=item.get('source', 'unknown'),
                metadata=item.get('metadata', {})
            )
            self.add_threat_indicator(indicator)

class AISecurityMonitor:
    """Main AI-driven security monitoring system"""
    
    def __init__(self):
        self.threat_detector = AIThreatDetector()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.threat_intel_processor = ThreatIntelligenceProcessor()
        self.security_metrics = []
        self.threat_events = []
        self.alert_threshold = 0.7
        
    def process_security_event(self, event: SecurityEvent) -> Dict[str, Any]:
        """Process a security event with AI-driven analysis"""
        logger.info(f"Processing security event: {event.event_id}")
        
        # Convert event to feature vector for AI analysis
        features = self._event_to_features(event)
        
        # Create DataFrame for analysis
        event_df = pd.DataFrame([features])
        
        # Detect anomalies
        anomalies = self.threat_detector.detect_anomalies(event_df)
        
        # Behavioral analysis
        behavioral_analysis = {}
        if event.user_id:
            behavioral_analysis = self.behavioral_analyzer.detect_behavioral_anomalies(
                event.user_id, 
                self._event_to_behavior_data(event)
            )
        
        # Threat intelligence correlation
        threat_intel_matches = self.threat_intel_processor.correlate_indicators(event)
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(
            anomalies, 
            behavioral_analysis, 
            threat_intel_matches,
            event.risk_score
        )
        
        # Determine threat level
        threat_level = self._risk_to_threat_level(risk_score)
        
        # Generate alert if necessary
        alert_generated = False
        if risk_score > self.alert_threshold:
            alert_generated = self._generate_alert(event, risk_score, threat_level)
        
        # Create analysis result
        result = {
            'event_id': event.event_id,
            'risk_score': risk_score,
            'threat_level': threat_level,
            'anomalies_detected': len(anomalies) > 0,
            'anomalies': anomalies,
            'behavioral_anomalies': behavioral_analysis,
            'threat_intel_matches': threat_intel_matches,
            'alert_generated': alert_generated,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store threat event if high risk
        if risk_score > 0.5:
            self.threat_events.append(result)
        
        return result
    
    def _event_to_features(self, event: SecurityEvent) -> Dict[str, Any]:
        """Convert security event to feature vector"""
        features = {
            'event_type_encoded': hash(event.event_type) % 1000,
            'severity_encoded': hash(event.severity.value) % 10,
            'risk_score': event.risk_score,
            'hour_of_day': event.timestamp.hour,
            'day_of_week': event.timestamp.weekday(),
            'metadata_count': len(event.metadata),
            'has_user_id': 1 if event.user_id else 0,
            'has_source_ip': 1 if event.source_ip else 0
        }
        
        # Add metadata features
        for key, value in event.metadata.items():
            if isinstance(value, (int, float)):
                features[f'meta_{key}'] = value
            elif isinstance(value, str):
                features[f'meta_{key}_encoded'] = hash(value) % 1000
        
        return features
    
    def _event_to_behavior_data(self, event: SecurityEvent) -> Dict[str, Any]:
        """Convert security event to behavioral data"""
        behavior_data = {
            'login_time': event.timestamp,
            'location': (0.0, 0.0),  # Default location
            'data_volume': 0,
            'device_id': 'unknown'
        }
        
        # Extract behavioral data from metadata
        if 'location' in event.metadata:
            behavior_data['location'] = event.metadata['location']
        
        if 'data_size' in event.metadata:
            behavior_data['data_volume'] = event.metadata['data_size']
        
        if 'device_id' in event.metadata:
            behavior_data['device_id'] = event.metadata['device_id']
        
        return behavior_data
    
    def _calculate_risk_score(self, anomalies: List[Dict[str, Any]], 
                            behavioral_analysis: Dict[str, Any],
                            threat_intel_matches: List[Dict[str, Any]],
                            base_risk_score: float) -> float:
        """Calculate overall risk score"""
        risk_factors = []
        
        # Anomaly-based risk
        if anomalies:
            max_anomaly_score = max([a.get('anomaly_score', 0) for a in anomalies])
            risk_factors.append(max_anomaly_score)
        
        # Behavioral risk
        if behavioral_analysis.get('anomaly_detected'):
            risk_factors.append(behavioral_analysis.get('risk_score', 0))
        
        # Threat intelligence risk
        if threat_intel_matches:
            max_confidence = max([m.get('confidence', 0) for m in threat_intel_matches])
            risk_factors.append(max_confidence)
        
        # Base risk score
        risk_factors.append(base_risk_score)
        
        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.2]  # Anomaly, behavioral, threat intel, base
        risk_score = sum(w * r for w, r in zip(weights[:len(risk_factors)], risk_factors))
        
        return min(1.0, max(0.0, risk_score))
    
    def _risk_to_threat_level(self, risk_score: float) -> ThreatLevel:
        """Convert risk score to threat level"""
        if risk_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif risk_score >= 0.6:
            return ThreatLevel.HIGH
        elif risk_score >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _generate_alert(self, event: SecurityEvent, risk_score: float, threat_level: ThreatLevel) -> bool:
        """Generate security alert"""
        alert_message = f"High-risk security event detected: {event.event_type} with risk score {risk_score:.2f}"
        logger.warning(f"ALERT: {alert_message}")
        
        # In a real implementation, this would send notifications via email, SMS, Slack, etc.
        # For now, we'll just log it
        return True
    
    def train_on_historical_data(self, historical_events: List[SecurityEvent]):
        """Train AI models on historical security data"""
        logger.info("Training AI models on historical security data...")
        
        # Convert events to features
        features_list = []
        labels_list = []
        
        for event in historical_events:
            features = self._event_to_features(event)
            features_list.append(features)
            
            # Create labels based on severity (simplified)
            if event.severity == ThreatLevel.CRITICAL:
                labels_list.append('critical')
            elif event.severity == ThreatLevel.HIGH:
                labels_list.append('high')
            elif event.severity == ThreatLevel.MEDIUM:
                labels_list.append('medium')
            else:
                labels_list.append('low')
        
        if features_list:
            # Create DataFrame
            df = pd.DataFrame(features_list)
            labels = pd.Series(labels_list)
            
            # Train models
            self.threat_detector.train_models(df, labels)
            
            logger.info("AI models trained successfully on historical data")
        else:
            logger.warning("No historical data available for training")

# Example usage
if __name__ == "__main__":
    # Create AI security monitor
    ai_monitor = AISecurityMonitor()
    
    # Create sample security event
    sample_event = SecurityEvent(
        event_id="evt_12345",
        timestamp=datetime.now(),
        event_type="failed_login",
        severity=ThreatLevel.MEDIUM,
        source_ip="192.168.1.100",
        user_id="user_abc",
        resource="admin_panel",
        action="login",
        result="failed",
        metadata={
            "attempt_count": 3,
            "location": (40.7128, -74.0060),
            "user_agent": "Mozilla/5.0...",
            "data_size": 0
        },
        risk_score=0.6
    )
    
    # Process the event
    result = ai_monitor.process_security_event(sample_event)
    
    print("AI Security Analysis Result:")
    print(json.dumps(result, indent=2, default=str))