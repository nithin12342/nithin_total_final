"""
Advanced Zero Trust Security Architecture Enhancements
Implementation of zero-trust architecture, advanced threat detection, and security automation
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import jwt
import requests
import redis
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ZeroTrustPolicy:
    """Zero Trust Policy Definition"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict]
    enforcement_level: str  # "strict", "permissive", "audit"
    target_resources: List[str]
    target_users: List[str]
    created_at: datetime
    updated_at: datetime

class ZeroTrustOrchestrator:
    """Orchestrates zero-trust security policies and enforcement"""
    
    def __init__(self, config_path: str = "security/configs/zero_trust_config.yaml"):
        self.policies: Dict[str, ZeroTrustPolicy] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.threat_intel_feeds: List[str] = []
        self.security_controls: Dict[str, Dict] = {}
        self._load_config(config_path)
        self._initialize_security_controls()
    
    def _load_config(self, config_path: str):
        """Load zero trust configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.threat_intel_feeds = config.get('threat_intel_feeds', [])
                self.security_controls = config.get('security_controls', {})
                logger.info("Zero trust configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load zero trust configuration: {e}")
    
    def _initialize_security_controls(self):
        """Initialize security controls from configuration"""
        for control_name, control_config in self.security_controls.items():
            logger.info(f"Initializing security control: {control_name}")
            # In a real implementation, this would initialize actual security controls
    
    def create_policy(self, policy: ZeroTrustPolicy) -> bool:
        """Create a new zero trust policy"""
        try:
            self.policies[policy.policy_id] = policy
            logger.info(f"Created zero trust policy: {policy.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create policy {policy.name}: {e}")
            return False
    
    def evaluate_access_request(self, user_context: Dict, resource: str, action: str) -> Dict:
        """Evaluate an access request against zero trust policies"""
        decision = {
            "access_granted": False,
            "policy_matched": None,
            "reason": "",
            "additional_auth_required": False,
            "risk_score": 0.0
        }
        
        # Calculate risk score based on user context
        risk_score = self._calculate_risk_score(user_context)
        decision["risk_score"] = risk_score
        
        # Evaluate against all policies
        for policy_id, policy in self.policies.items():
            if self._matches_policy_targets(policy, user_context, resource):
                # Evaluate policy rules
                if self._evaluate_policy_rules(policy, user_context, resource, action, risk_score):
                    decision["access_granted"] = True
                    decision["policy_matched"] = policy_id
                    decision["reason"] = f"Access granted by policy: {policy.name}"
                    break
                else:
                    decision["access_granted"] = False
                    decision["policy_matched"] = policy_id
                    decision["reason"] = f"Access denied by policy: {policy.name}"
                    break
        
        # If no specific policy matches, apply default deny
        if decision["policy_matched"] is None:
            decision["access_granted"] = False
            decision["reason"] = "No matching policy found - default deny"
        
        # Log the access decision
        self._log_access_decision(user_context, resource, action, decision)
        
        return decision
    
    def _calculate_risk_score(self, user_context: Dict) -> float:
        """Calculate risk score based on user context"""
        risk_score = 0.0
        
        # Check for anomalous behavior
        if user_context.get("behavior_anomaly", False):
            risk_score += 0.3
        
        # Check location risk
        if user_context.get("location_risk", 0) > 0.5:
            risk_score += user_context["location_risk"] * 0.2
        
        # Check device trust
        if user_context.get("device_trust_score", 1.0) < 0.7:
            risk_score += (1.0 - user_context["device_trust_score"]) * 0.25
        
        # Check time-based risk
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 6:  # Night hours
            risk_score += 0.1
        
        # Check for multiple failed attempts
        if user_context.get("failed_attempts", 0) > 3:
            risk_score += min(0.3, user_context["failed_attempts"] * 0.1)
        
        return min(1.0, risk_score)  # Cap at 1.0
    
    def _matches_policy_targets(self, policy: ZeroTrustPolicy, user_context: Dict, resource: str) -> bool:
        """Check if policy targets match the request"""
        # Check resource match
        resource_match = any(target in resource for target in policy.target_resources)
        
        # Check user match (simplified)
        user_match = True  # In real implementation, check user groups/roles
        
        return resource_match and user_match
    
    def _evaluate_policy_rules(self, policy: ZeroTrustPolicy, user_context: Dict, resource: str, action: str, risk_score: float) -> bool:
        """Evaluate policy rules against the request"""
        for rule in policy.rules:
            # Check risk threshold
            if "max_risk_score" in rule and risk_score > rule["max_risk_score"]:
                return False
            
            # Check required authentication factors
            if "required_auth_factors" in rule:
                provided_factors = user_context.get("auth_factors", [])
                required_factors = rule["required_auth_factors"]
                if not all(factor in provided_factors for factor in required_factors):
                    return False
            
            # Check time-based access
            if "allowed_time_ranges" in rule:
                current_time = datetime.now().time()
                allowed = False
                for time_range in rule["allowed_time_ranges"]:
                    start_time = datetime.strptime(time_range["start"], "%H:%M").time()
                    end_time = datetime.strptime(time_range["end"], "%H:%M").time()
                    if start_time <= current_time <= end_time:
                        allowed = True
                        break
                if not allowed:
                    return False
        
        # If all rules pass, grant access
        return True
    
    def _log_access_decision(self, user_context: Dict, resource: str, action: str, decision: Dict):
        """Log access decision for audit and analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_context.get("user_id", "unknown"),
            "resource": resource,
            "action": action,
            "decision": decision,
            "user_context": user_context
        }
        
        logger.info(f"Access decision: {json.dumps(log_entry)}")
    
    def update_threat_intel(self):
        """Update threat intelligence feeds"""
        for feed_url in self.threat_intel_feeds:
            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    threat_data = response.json()
                    # Process threat intelligence data
                    self._process_threat_intel(threat_data)
                    logger.info(f"Updated threat intelligence from {feed_url}")
            except Exception as e:
                logger.error(f"Failed to update threat intel from {feed_url}: {e}")
    
    def _process_threat_intel(self, threat_data: Dict):
        """Process threat intelligence data"""
        # In a real implementation, this would update blocklists, reputation scores, etc.
        pass

class AdvancedThreatDetector:
    """Advanced threat detection using behavioral analytics and machine learning"""
    
    def __init__(self):
        self.baseline_profiles = {}
        self.anomaly_detectors = {}
        self.threat_indicators = set()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def analyze_user_behavior(self, user_id: str, activity_log: Dict) -> Dict:
        """Analyze user behavior for anomalies"""
        analysis_result = {
            "user_id": user_id,
            "anomaly_detected": False,
            "anomaly_score": 0.0,
            "threat_level": "low",
            "indicators": []
        }
        
        # Get user's baseline profile
        baseline = self._get_user_baseline(user_id)
        
        # Calculate deviation from baseline
        deviation_score = self._calculate_behavioral_deviation(activity_log, baseline)
        analysis_result["anomaly_score"] = deviation_score
        
        # Determine threat level
        if deviation_score > 0.8:
            analysis_result["threat_level"] = "critical"
            analysis_result["anomaly_detected"] = True
        elif deviation_score > 0.5:
            analysis_result["threat_level"] = "high"
            analysis_result["anomaly_detected"] = True
        elif deviation_score > 0.3:
            analysis_result["threat_level"] = "medium"
            analysis_result["anomaly_detected"] = True
        
        # Add specific indicators
        indicators = self._identify_threat_indicators(activity_log)
        analysis_result["indicators"] = indicators
        
        # Store analysis result
        self._store_analysis_result(analysis_result)
        
        return analysis_result
    
    def _get_user_baseline(self, user_id: str) -> Dict:
        """Get user's baseline behavioral profile"""
        baseline_key = f"baseline:{user_id}"
        baseline_data = self.redis_client.get(baseline_key)
        
        if baseline_data:
            return json.loads(baseline_data)
        else:
            # Create initial baseline
            baseline = {
                "avg_login_time": "09:00",
                "common_locations": ["192.168.1.0/24"],
                "typical_actions": ["view_orders", "update_inventory"],
                "usual_devices": ["device_123"],
                "session_duration_avg": 1800  # 30 minutes
            }
            self.redis_client.setex(baseline_key, 86400, json.dumps(baseline))  # 24 hours
            return baseline
    
    def _calculate_behavioral_deviation(self, activity_log: Dict, baseline: Dict) -> float:
        """Calculate deviation from baseline behavior"""
        deviation_score = 0.0
        
        # Check login time deviation
        login_time = activity_log.get("login_time", "")
        if login_time and baseline.get("avg_login_time"):
            # Simplified time deviation calculation
            deviation_score += 0.1
        
        # Check location deviation
        current_location = activity_log.get("source_ip", "")
        if current_location and baseline.get("common_locations"):
            if not any(loc in current_location for loc in baseline["common_locations"]):
                deviation_score += 0.3
        
        # Check action deviation
        current_actions = activity_log.get("actions", [])
        if current_actions and baseline.get("typical_actions"):
            typical_actions = set(baseline["typical_actions"])
            current_action_set = set(current_actions)
            unusual_actions = current_action_set - typical_actions
            if unusual_actions:
                deviation_score += len(unusual_actions) * 0.1
        
        return min(1.0, deviation_score)
    
    def _identify_threat_indicators(self, activity_log: Dict) -> List[str]:
        """Identify specific threat indicators"""
        indicators = []
        
        # Rapid succession of actions
        if activity_log.get("action_rate", 0) > 10:  # More than 10 actions per minute
            indicators.append("rapid_actions")
        
        # Access to sensitive resources
        sensitive_resources = ["/admin", "/finance", "/blockchain"]
        accessed_resources = activity_log.get("accessed_resources", [])
        for resource in accessed_resources:
            if any(sensitive in resource for sensitive in sensitive_resources):
                indicators.append("sensitive_resource_access")
                break
        
        # Failed authentication attempts
        failed_attempts = activity_log.get("failed_auth_attempts", 0)
        if failed_attempts > 3:
            indicators.append("multiple_failed_auth")
        
        # Unusual data access patterns
        data_accessed = activity_log.get("data_accessed", {})
        if data_accessed.get("large_volume", False):
            indicators.append("unusual_data_volume")
        
        return indicators
    
    def _store_analysis_result(self, analysis_result: Dict):
        """Store analysis result for future reference"""
        result_key = f"analysis:{analysis_result['user_id']}:{int(time.time())}"
        self.redis_client.setex(result_key, 3600, json.dumps(analysis_result))  # 1 hour

class SecurityOrchestration:
    """Security orchestration and automation"""
    
    def __init__(self):
        self.orchestrator = ZeroTrustOrchestrator()
        self.threat_detector = AdvancedThreatDetector()
        self.incident_response_playbooks = {}
        self._load_playbooks()
    
    def _load_playbooks(self):
        """Load incident response playbooks"""
        # In a real implementation, this would load playbooks from files
        self.incident_response_playbooks = {
            "high_risk_access": {
                "steps": [
                    "Block user access temporarily",
                    "Notify security team",
                    "Require additional authentication",
                    "Log incident for investigation"
                ]
            },
            "anomalous_behavior": {
                "steps": [
                    "Increase monitoring frequency",
                    "Review recent user activities",
                    "Update user risk profile",
                    "Notify user of suspicious activity"
                ]
            }
        }
    
    async def handle_security_event(self, event: Dict):
        """Handle a security event through orchestration"""
        event_type = event.get("type", "unknown")
        
        if event_type == "access_request":
            await self._handle_access_request(event)
        elif event_type == "anomalous_behavior":
            await self._handle_anomalous_behavior(event)
        elif event_type == "threat_detected":
            await self._handle_threat_detection(event)
    
    async def _handle_access_request(self, event: Dict):
        """Handle access request event"""
        user_context = event.get("user_context", {})
        resource = event.get("resource", "")
        action = event.get("action", "")
        
        # Evaluate access request
        decision = self.orchestrator.evaluate_access_request(user_context, resource, action)
        
        # If high risk, trigger additional controls
        if decision["risk_score"] > 0.7:
            await self._trigger_high_risk_response(user_context, resource, decision)
    
    async def _handle_anomalous_behavior(self, event: Dict):
        """Handle anomalous behavior detection"""
        user_id = event.get("user_id", "")
        activity_log = event.get("activity_log", {})
        
        # Analyze behavior
        analysis = self.threat_detector.analyze_user_behavior(user_id, activity_log)
        
        # If anomaly detected, take action
        if analysis["anomaly_detected"]:
            await self._trigger_anomaly_response(user_id, analysis)
    
    async def _handle_threat_detection(self, event: Dict):
        """Handle threat detection event"""
        threat_info = event.get("threat_info", {})
        # In a real implementation, this would trigger threat response procedures
        logger.warning(f"Threat detected: {threat_info}")
    
    async def _trigger_high_risk_response(self, user_context: Dict, resource: str, decision: Dict):
        """Trigger response for high-risk access request"""
        user_id = user_context.get("user_id", "unknown")
        logger.warning(f"High-risk access detected for user {user_id} to resource {resource}")
        
        # Execute incident response playbook
        playbook = self.incident_response_playbooks.get("high_risk_access")
        if playbook:
            for step in playbook["steps"]:
                logger.info(f"Executing response step: {step}")
                # In a real implementation, this would execute actual response actions
    
    async def _trigger_anomaly_response(self, user_id: str, analysis: Dict):
        """Trigger response for behavioral anomaly"""
        logger.warning(f"Behavioral anomaly detected for user {user_id}: {analysis}")
        
        # Execute incident response playbook
        playbook = self.incident_response_playbooks.get("anomalous_behavior")
        if playbook:
            for step in playbook["steps"]:
                logger.info(f"Executing response step: {step}")
                # In a real implementation, this would execute actual response actions

# Example usage
async def main():
    """Example usage of the zero trust security enhancements"""
    # Initialize security orchestration
    security_orchestrator = SecurityOrchestration()
    
    # Create a sample zero trust policy
    policy = ZeroTrustPolicy(
        policy_id="policy_001",
        name="High-Security Resource Access",
        description="Strict access control for sensitive resources",
        rules=[
            {
                "max_risk_score": 0.5,
                "required_auth_factors": ["password", "totp"],
                "allowed_time_ranges": [
                    {"start": "08:00", "end": "18:00"}
                ]
            }
        ],
        enforcement_level="strict",
        target_resources=["/admin", "/finance", "/blockchain"],
        target_users=["*"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Add policy to orchestrator
    security_orchestrator.orchestrator.create_policy(policy)
    
    # Simulate an access request
    user_context = {
        "user_id": "user_123",
        "source_ip": "192.168.1.100",
        "auth_factors": ["password", "totp"],
        "device_trust_score": 0.9,
        "location_risk": 0.1,
        "behavior_anomaly": False
    }
    
    access_event = {
        "type": "access_request",
        "user_context": user_context,
        "resource": "/admin/dashboard",
        "action": "read"
    }
    
    # Handle the security event
    await security_orchestrator.handle_security_event(access_event)
    
    # Simulate anomalous behavior detection
    activity_log = {
        "user_id": "user_123",
        "login_time": "03:00",
        "source_ip": "10.0.0.1",
        "actions": ["view_orders", "export_data", "delete_records"],
        "action_rate": 15,
        "accessed_resources": ["/admin/users", "/finance/transactions"],
        "data_accessed": {"large_volume": True}
    }
    
    anomaly_event = {
        "type": "anomalous_behavior",
        "user_id": "user_123",
        "activity_log": activity_log
    }
    
    # Handle the anomaly detection event
    await security_orchestrator.handle_security_event(anomaly_event)

if __name__ == "__main__":
    asyncio.run(main())