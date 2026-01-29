"""
Demo script for AI-Driven Security Monitoring System
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the security modules
from security.ai_driven.ai_security_monitor import (
    AISecurityMonitor,
    SecurityEvent,
    ThreatLevel
)

def main():
    """Main demo function"""
    print("=== AI-Driven Security Monitoring Demo ===\n")
    
    # Initialize AI Security Monitor
    print("1. Initializing AI Security Monitor...")
    ai_monitor = AISecurityMonitor()
    
    # Train on sample historical data
    print("2. Training on historical security data...")
    historical_events = _generate_sample_historical_events()
    ai_monitor.train_on_historical_data(historical_events)
    
    # Add sample threat indicators
    print("3. Adding threat intelligence indicators...")
    _add_sample_threat_indicators(ai_monitor)
    
    # Update behavioral profiles
    print("4. Updating user behavioral profiles...")
    _update_user_behavioral_profiles(ai_monitor)
    
    # Process sample security events
    print("5. Processing security events...")
    sample_events = _generate_sample_security_events()
    
    results = []
    for i, event in enumerate(sample_events):
        print(f"   Processing event {i+1}/{len(sample_events)}...")
        result = ai_monitor.process_security_event(event)
        results.append(result)
        time.sleep(0.5)  # Small delay for demo effect
    
    # Display results
    print("\n=== Security Analysis Results ===")
    for i, result in enumerate(results):
        print(f"\nEvent {i+1}:")
        print(f"  Risk Score: {result['risk_score']:.2f}")
        print(f"  Threat Level: {result['threat_level'].value}")
        print(f"  Anomalies Detected: {result['anomalies_detected']}")
        print(f"  Alert Generated: {result['alert_generated']}")
        
        if result['anomalies']:
            print("  Anomalies:")
            for anomaly in result['anomalies']:
                print(f"    - Type: {anomaly.get('detection_method', 'unknown')}")
                print(f"      Score: {anomaly.get('anomaly_score', 0):.2f}")
        
        if result['behavioral_anomalies'].get('anomaly_detected'):
            print("  Behavioral Anomalies:")
            for anomaly_type, detected in result['behavioral_anomalies']['details'].items():
                if detected:
                    print(f"    - {anomaly_type}")
        
        if result['threat_intel_matches']:
            print("  Threat Intelligence Matches:")
            for match in result['threat_intel_matches']:
                print(f"    - {match['type']}: {match['threat_type']} (confidence: {match['confidence']:.2f})")
    
    # Show system statistics
    print(f"\n=== System Statistics ===")
    print(f"  Total Events Processed: {len(results)}")
    print(f"  High-Risk Events: {len([r for r in results if r['risk_score'] > 0.7])}")
    print(f"  Alerts Generated: {len([r for r in results if r['alert_generated']])}")
    print(f"  Threat Indicators Processed: {len(ai_monitor.threat_intel_processor.threat_indicators)}")

def _generate_sample_historical_events() -> list:
    """Generate sample historical security events for training"""
    events = []
    
    # Generate normal events
    for i in range(50):
        event = SecurityEvent(
            event_id=f"hist_norm_{i}",
            timestamp=datetime.now() - timedelta(days=i % 30),
            event_type="successful_login",
            severity=ThreatLevel.LOW,
            source_ip=f"192.168.1.{100 + (i % 50)}",
            user_id=f"user_{(i % 10) + 1}",
            resource="dashboard",
            action="read",
            result="success",
            metadata={
                "location": (40.7128, -74.0060),
                "user_agent": "Mozilla/5.0...",
                "session_duration": 1800
            },
            risk_score=0.1
        )
        events.append(event)
    
    # Generate some medium-risk events
    for i in range(20):
        event = SecurityEvent(
            event_id=f"hist_med_{i}",
            timestamp=datetime.now() - timedelta(days=i % 15),
            event_type="failed_login",
            severity=ThreatLevel.MEDIUM,
            source_ip=f"192.168.2.{100 + (i % 20)}",
            user_id=f"user_{(i % 5) + 1}",
            resource="admin_panel",
            action="login",
            result="failed",
            metadata={
                "attempt_count": 3,
                "location": (40.7128, -74.0060),
                "user_agent": "Mozilla/5.0..."
            },
            risk_score=0.5
        )
        events.append(event)
    
    # Generate some high-risk events
    for i in range(10):
        event = SecurityEvent(
            event_id=f"hist_high_{i}",
            timestamp=datetime.now() - timedelta(days=i % 7),
            event_type="data_exfiltration",
            severity=ThreatLevel.HIGH,
            source_ip=f"10.0.0.{100 + (i % 10)}",
            user_id=f"user_{(i % 3) + 1}",
            resource="financial_data",
            action="download",
            result="success",
            metadata={
                "data_size": 1000000,
                "location": (34.0522, -118.2437),  # Los Angeles
                "user_agent": "curl/7.0"
            },
            risk_score=0.8
        )
        events.append(event)
    
    return events

def _add_sample_threat_indicators(ai_monitor):
    """Add sample threat indicators to the system"""
    indicators = [
        {
            "id": "ioc_1",
            "timestamp": datetime.now().isoformat(),
            "type": "ip",
            "value": "10.0.0.100",
            "confidence": 0.9,
            "threat_type": "data_exfiltration",
            "source": "internal_threat_intel",
            "metadata": {"description": "Known malicious IP address"}
        },
        {
            "id": "ioc_2",
            "timestamp": datetime.now().isoformat(),
            "type": "user_agent",
            "value": "curl/7.0",
            "confidence": 0.8,
            "threat_type": "automated_attack",
            "source": "external_feed",
            "metadata": {"description": "Associated with automated scanning tools"}
        }
    ]
    
    ai_monitor.threat_intel_processor.update_threat_intelligence(indicators)

def _update_user_behavioral_profiles(ai_monitor):
    """Update user behavioral profiles with sample data"""
    # Update profiles for several users
    for user_id in ["user_1", "user_2", "user_3"]:
        # Normal behavior
        for i in range(10):
            ai_monitor.behavioral_analyzer.update_user_profile(user_id, {
                "login_time": datetime.now() - timedelta(hours=i*2),
                "accessed_resources": ["dashboard", "reports", "analytics"],
                "data_volume": 1000 + (i * 100),
                "location": (40.7128, -74.0060),  # New York
                "device_id": f"device_{user_id[-1]}",
                "session_duration": 1800 + (i * 300)
            })

def _generate_sample_security_events() -> list:
    """Generate sample security events for processing"""
    events = [
        # Normal event
        SecurityEvent(
            event_id="evt_1",
            timestamp=datetime.now(),
            event_type="successful_login",
            severity=ThreatLevel.LOW,
            source_ip="192.168.1.101",
            user_id="user_1",
            resource="dashboard",
            action="read",
            result="success",
            metadata={
                "location": (40.7128, -74.0060),
                "user_agent": "Mozilla/5.0...",
                "session_duration": 1800
            },
            risk_score=0.1
        ),
        
        # Behavioral anomaly - unusual login time
        SecurityEvent(
            event_id="evt_2",
            timestamp=datetime.now().replace(hour=3),  # Unusual hour
            event_type="successful_login",
            severity=ThreatLevel.MEDIUM,
            source_ip="192.168.1.102",
            user_id="user_2",
            resource="dashboard",
            action="read",
            result="success",
            metadata={
                "location": (40.7128, -74.0060),
                "user_agent": "Mozilla/5.0...",
                "session_duration": 1800
            },
            risk_score=0.4
        ),
        
        # Threat intelligence match
        SecurityEvent(
            event_id="evt_3",
            timestamp=datetime.now(),
            event_type="suspicious_request",
            severity=ThreatLevel.HIGH,
            source_ip="10.0.0.100",  # Known malicious IP
            user_id="user_3",
            resource="admin_panel",
            action="access",
            result="attempted",
            metadata={
                "location": (34.0522, -118.2437),  # Los Angeles
                "user_agent": "curl/7.0",  # Known malicious user agent
                "data_size": 0
            },
            risk_score=0.7
        ),
        
        # High-risk data access
        SecurityEvent(
            event_id="evt_4",
            timestamp=datetime.now(),
            event_type="data_access",
            severity=ThreatLevel.HIGH,
            source_ip="192.168.1.104",
            user_id="user_1",
            resource="financial_data",
            action="download",
            result="success",
            metadata={
                "location": (34.0522, -118.2437),  # Different location
                "user_agent": "Mozilla/5.0...",
                "data_size": 5000000,  # Large data volume
                "device_id": "device_unknown"  # Unknown device
            },
            risk_score=0.6
        )
    ]
    
    return events

if __name__ == "__main__":
    main()