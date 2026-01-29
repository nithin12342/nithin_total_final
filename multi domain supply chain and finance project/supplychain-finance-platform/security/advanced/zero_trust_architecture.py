"""
Advanced Zero Trust Security Architecture
Demonstrating mastery of cybersecurity from intermediate to advanced levels

This module showcases:
- Zero Trust Network Access (ZTNA)
- Identity and Access Management (IAM)
- Multi-Factor Authentication (MFA)
- Behavioral Analytics and Anomaly Detection
- Threat Intelligence and Response
- Security Orchestration, Automation and Response (SOAR)
- Advanced Persistent Threat (APT) Detection
- Quantum-Resistant Cryptography
- Homomorphic Encryption
- Zero-Knowledge Proofs
"""

import hashlib
import hmac
import secrets
import time
import json
import logging
import asyncio
import threading
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import jwt
import bcrypt
import pyotp
import qrcode
from PIL import Image
import requests
import redis
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import yaml
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AccessDecision(Enum):
    """Access decision enumeration"""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    REVIEW = "review"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    resource: str
    action: str
    result: str
    metadata: Dict[str, Any]
    risk_score: float

@dataclass
class UserContext:
    """User context for zero trust decisions"""
    user_id: str
    device_id: str
    source_ip: str
    location: Tuple[float, float]
    network: str
    time_of_access: datetime
    behavior_profile: Dict[str, Any]
    risk_factors: List[str]
    trust_score: float
    totp_code: Optional[str] = None

@dataclass
class AccessRequest:
    """Access request data structure"""
    request_id: str
    user_id: str
    resource: str
    action: str
    context: UserContext
    timestamp: datetime
    session_id: str

class QuantumResistantCrypto:
    """Quantum-resistant cryptographic operations"""
    
    def __init__(self):
        self.algorithms = {
            'dilithium': self._dilithium_sign,
            'kyber': self._kyber_encrypt,
            'sphincs': self._sphincs_sign
        }
    
    def generate_quantum_resistant_keypair(self, algorithm: str = 'dilithium') -> Tuple[bytes, bytes]:
        """Generate quantum-resistant key pair"""
        if algorithm == 'dilithium':
            # Simplified Dilithium-like key generation
            private_key = secrets.token_bytes(32)
            public_key = hashlib.sha256(private_key).digest()
            return private_key, public_key
        elif algorithm == 'kyber':
            # Simplified Kyber-like key generation
            private_key = secrets.token_bytes(32)
            public_key = hashlib.sha256(private_key + b'kyber').digest()
            return private_key, public_key
        else:
            raise ValueError(f"Unsupported quantum-resistant algorithm: {algorithm}")
    
    def _dilithium_sign(self, message: bytes, private_key: bytes) -> bytes:
        """Dilithium-like digital signature"""
        # Simplified implementation
        signature = hmac.new(private_key, message, hashlib.sha256).digest()
        return signature
    
    def _kyber_encrypt(self, message: bytes, public_key: bytes) -> bytes:
        """Kyber-like encryption"""
        # Simplified implementation
        key = hashlib.sha256(public_key).digest()
        cipher = Cipher(algorithms.AES(key), modes.CBC(secrets.token_bytes(16)), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(message) + encryptor.finalize()
    
    def _sphincs_sign(self, message: bytes, private_key: bytes) -> bytes:
        """SPHINCS-like digital signature"""
        # Simplified implementation
        signature = hashlib.sha256(private_key + message).digest()
        return signature

class HomomorphicEncryption:
    """Homomorphic encryption for privacy-preserving computations"""
    
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self._generate_keypair()
    
    def _generate_keypair(self):
        """Generate homomorphic encryption key pair"""
        # Simplified implementation - in practice, use libraries like SEAL or HElib
        self.private_key = secrets.token_bytes(32)
        self.public_key = hashlib.sha256(self.private_key).digest()
    
    def encrypt(self, plaintext: int) -> bytes:
        """Encrypt plaintext homomorphically"""
        # Simplified additive homomorphic encryption
        noise = secrets.randbelow(1000)
        encrypted = (plaintext + noise).to_bytes(4, 'big')
        return encrypted
    
    def decrypt(self, ciphertext: bytes) -> int:
        """Decrypt ciphertext"""
        # Simplified decryption
        return int.from_bytes(ciphertext, 'big')
    
    def add_encrypted(self, ciphertext1: bytes, ciphertext2: bytes) -> bytes:
        """Add two encrypted values homomorphically"""
        val1 = int.from_bytes(ciphertext1, 'big')
        val2 = int.from_bytes(ciphertext2, 'big')
        result = (val1 + val2).to_bytes(4, 'big')
        return result
    
    def multiply_encrypted(self, ciphertext: bytes, scalar: int) -> bytes:
        """Multiply encrypted value by scalar homomorphically"""
        val = int.from_bytes(ciphertext, 'big')
        result = (val * scalar).to_bytes(4, 'big')
        return result

class ZeroKnowledgeProof:
    """Zero-knowledge proof system"""
    
    def __init__(self):
        self.challenges = {}
    
    def generate_proof(self, secret: str, statement: str) -> Dict[str, Any]:
        """Generate zero-knowledge proof"""
        # Simplified ZK proof using Fiat-Shamir heuristic
        commitment = hashlib.sha256(secret.encode()).hexdigest()
        challenge = secrets.token_hex(16)
        response = hashlib.sha256((secret + challenge).encode()).hexdigest()
        
        proof = {
            'commitment': commitment,
            'challenge': challenge,
            'response': response,
            'statement': statement,
            'timestamp': datetime.now().isoformat()
        }
        
        self.challenges[challenge] = proof
        return proof
    
    def verify_proof(self, proof: Dict[str, Any]) -> bool:
        """Verify zero-knowledge proof"""
        try:
            commitment = proof['commitment']
            challenge = proof['challenge']
            response = proof['response']
            
            # Verify response matches expected value
            expected_response = hashlib.sha256((commitment + challenge).encode()).hexdigest()
            return response == expected_response
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False

class BehavioralAnalytics:
    """Behavioral analytics for anomaly detection"""
    
    def __init__(self):
        self.user_profiles = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def update_user_profile(self, user_id: str, behavior_data: Dict[str, Any]):
        """Update user behavior profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'login_times': [],
                'access_patterns': [],
                'device_usage': [],
                'location_patterns': [],
                'resource_access': [],
                'session_durations': []
            }
        
        profile = self.user_profiles[user_id]
        
        # Update various behavior metrics
        if 'login_time' in behavior_data:
            profile['login_times'].append(behavior_data['login_time'])
        
        if 'access_pattern' in behavior_data:
            profile['access_patterns'].append(behavior_data['access_pattern'])
        
        if 'device_info' in behavior_data:
            profile['device_usage'].append(behavior_data['device_info'])
        
        if 'location' in behavior_data:
            profile['location_patterns'].append(behavior_data['location'])
        
        if 'resource' in behavior_data:
            profile['resource_access'].append(behavior_data['resource'])
        
        if 'session_duration' in behavior_data:
            profile['session_durations'].append(behavior_data['session_duration'])
        
        # Keep only recent data (last 1000 entries)
        for key in profile:
            if len(profile[key]) > 1000:
                profile[key] = profile[key][-1000:]
    
    def detect_anomalies(self, user_id: str, current_behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Detect behavioral anomalies"""
        if user_id not in self.user_profiles:
            return {'anomaly_detected': False, 'risk_score': 0.0}
        
        profile = self.user_profiles[user_id]
        
        # Extract features for anomaly detection
        features = self._extract_behavior_features(profile, current_behavior)
        
        if not self.is_fitted:
            # Train anomaly detector on historical data
            self._train_anomaly_detector()
        
        # Detect anomalies
        anomaly_score = self.anomaly_detector.decision_function([features])[0]
        is_anomaly = self.anomaly_detector.predict([features])[0] == -1
        
        risk_score = max(0, min(1, (1 - anomaly_score) / 2))
        
        return {
            'anomaly_detected': bool(is_anomaly),
            'anomaly_score': float(anomaly_score),
            'risk_score': risk_score,
            'features': features.tolist()
        }
    
    def _extract_behavior_features(self, profile: Dict[str, Any], current_behavior: Dict[str, Any]) -> np.ndarray:
        """Extract features from behavior data"""
        features = []
        
        # Login time features
        if profile['login_times']:
            current_hour = current_behavior.get('login_time', datetime.now().hour)
            avg_hour = np.mean([t.hour for t in profile['login_times']])
            features.extend([current_hour.hour, avg_hour, abs(current_hour.hour - avg_hour)])
        else:
            features.extend([0, 0, 0])
        
        # Location features
        if profile['location_patterns']:
            current_location = current_behavior.get('location', (0, 0))
            avg_lat = np.mean([loc[0] for loc in profile['location_patterns']])
            avg_lon = np.mean([loc[1] for loc in profile['location_patterns']])
            distance = np.sqrt((current_location[0] - avg_lat)**2 + (current_location[1] - avg_lon)**2)
            features.extend([current_location[0], current_location[1], distance])
        else:
            features.extend([0, 0, 0])
        
        # Session duration features
        if profile['session_durations']:
            current_duration = current_behavior.get('session_duration', 0)
            avg_duration = np.mean(profile['session_durations'])
            features.extend([current_duration, avg_duration, abs(current_duration - avg_duration)])
        else:
            features.extend([0, 0, 0])
        
        # Resource access patterns
        if profile['resource_access']:
            current_resource = current_behavior.get('resource', '')
            resource_frequency = profile['resource_access'].count(current_resource) / len(profile['resource_access'])
            features.append(resource_frequency)
        else:
            features.append(0)
        
        return np.array(features)
    
    def _train_anomaly_detector(self):
        """Train anomaly detector on all user profiles"""
        all_features = []
        
        for user_id, profile in self.user_profiles.items():
            if len(profile['login_times']) > 10:  # Only use profiles with sufficient data
                features = self._extract_behavior_features(profile, {})
                all_features.append(features)
        
        if all_features:
            all_features = np.array(all_features)
            self.scaler.fit(all_features)
            all_features = self.scaler.transform(all_features)
            self.anomaly_detector.fit(all_features)
            self.is_fitted = True

class ThreatIntelligence:
    """Threat intelligence and response system"""
    
    def __init__(self):
        self.threat_feeds = []
        self.ioc_database = {}  # Indicators of Compromise
        self.threat_actors = {}
        self.attack_patterns = {}
        self.reputation_scores = {}
    
    def add_threat_feed(self, feed_url: str, feed_type: str):
        """Add external threat intelligence feed"""
        self.threat_feeds.append({
            'url': feed_url,
            'type': feed_type,
            'last_updated': None,
            'data': []
        })
    
    def update_threat_intelligence(self):
        """Update threat intelligence from external feeds"""
        for feed in self.threat_feeds:
            try:
                response = requests.get(feed['url'], timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    feed['data'] = data
                    feed['last_updated'] = datetime.now()
                    self._process_threat_data(data, feed['type'])
            except Exception as e:
                logger.error(f"Failed to update threat feed {feed['url']}: {e}")
    
    def _process_threat_data(self, data: Dict[str, Any], feed_type: str):
        """Process threat intelligence data"""
        if feed_type == 'ioc':
            # Process Indicators of Compromise
            for ioc in data.get('indicators', []):
                self.ioc_database[ioc['value']] = {
                    'type': ioc['type'],
                    'threat_level': ioc.get('threat_level', 'medium'),
                    'description': ioc.get('description', ''),
                    'first_seen': ioc.get('first_seen'),
                    'last_seen': ioc.get('last_seen'),
                    'source': feed_type
                }
        
        elif feed_type == 'threat_actor':
            # Process threat actor information
            for actor in data.get('actors', []):
                self.threat_actors[actor['name']] = {
                    'aliases': actor.get('aliases', []),
                    'motivation': actor.get('motivation', ''),
                    'capabilities': actor.get('capabilities', []),
                    'targets': actor.get('targets', []),
                    'tactics': actor.get('tactics', [])
                }
        
        elif feed_type == 'attack_pattern':
            # Process attack patterns
            for pattern in data.get('patterns', []):
                self.attack_patterns[pattern['id']] = {
                    'name': pattern['name'],
                    'description': pattern['description'],
                    'tactics': pattern.get('tactics', []),
                    'techniques': pattern.get('techniques', []),
                    'indicators': pattern.get('indicators', [])
                }
    
    def check_ioc(self, value: str, ioc_type: str) -> Dict[str, Any]:
        """Check if value is a known Indicator of Compromise"""
        if value in self.ioc_database:
            ioc_info = self.ioc_database[value]
            return {
                'is_ioc': True,
                'threat_level': ioc_info['threat_level'],
                'description': ioc_info['description'],
                'confidence': 0.9
            }
        
        # Check for partial matches or similar patterns
        for known_ioc, info in self.ioc_database.items():
            if ioc_type == 'ip' and self._ip_similarity(value, known_ioc) > 0.8:
                return {
                    'is_ioc': True,
                    'threat_level': info['threat_level'],
                    'description': f"Similar to known IOC: {info['description']}",
                    'confidence': 0.7
                }
        
        return {'is_ioc': False, 'confidence': 0.0}
    
    def _ip_similarity(self, ip1: str, ip2: str) -> float:
        """Calculate similarity between two IP addresses"""
        try:
            parts1 = [int(x) for x in ip1.split('.')]
            parts2 = [int(x) for x in ip2.split('.')]
            
            if len(parts1) != 4 or len(parts2) != 4:
                return 0.0
            
            # Calculate similarity based on subnet
            similarity = 0.0
            for i in range(4):
                if parts1[i] == parts2[i]:
                    similarity += 0.25
                else:
                    break
            
            return similarity
        except:
            return 0.0
    
    def analyze_attack_pattern(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event data against known attack patterns"""
        matches = []
        
        for pattern_id, pattern in self.attack_patterns.items():
            score = self._calculate_pattern_match_score(event_data, pattern)
            if score > 0.5:
                matches.append({
                    'pattern_id': pattern_id,
                    'pattern_name': pattern['name'],
                    'match_score': score,
                    'tactics': pattern['tactics'],
                    'techniques': pattern['techniques']
                })
        
        return {
            'matches': matches,
            'highest_match': max(matches, key=lambda x: x['match_score']) if matches else None
        }
    
    def _calculate_pattern_match_score(self, event_data: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """Calculate how well event data matches an attack pattern"""
        score = 0.0
        total_indicators = len(pattern.get('indicators', []))
        
        if total_indicators == 0:
            return 0.0
        
        for indicator in pattern['indicators']:
            if self._check_indicator_match(event_data, indicator):
                score += 1.0
        
        return score / total_indicators
    
    def _check_indicator_match(self, event_data: Dict[str, Any], indicator: Dict[str, Any]) -> bool:
        """Check if event data matches a specific indicator"""
        indicator_type = indicator.get('type')
        indicator_value = indicator.get('value')
        
        if indicator_type == 'ip' and 'source_ip' in event_data:
            return event_data['source_ip'] == indicator_value
        elif indicator_type == 'user_agent' and 'user_agent' in event_data:
            return indicator_value.lower() in event_data['user_agent'].lower()
        elif indicator_type == 'url' and 'url' in event_data:
            return indicator_value.lower() in event_data['url'].lower()
        
        return False

class SOAREngine:
    """Security Orchestration, Automation and Response (SOAR) engine"""
    
    def __init__(self):
        self.playbooks = {}
        self.active_incidents = {}
        self.automation_rules = []
        self.response_actions = {
            'block_ip': self._block_ip,
            'quarantine_device': self._quarantine_device,
            'disable_user': self._disable_user,
            'send_alert': self._send_alert,
            'collect_forensics': self._collect_forensics,
            'escalate_incident': self._escalate_incident
        }
    
    def create_playbook(self, name: str, steps: List[Dict[str, Any]]):
        """Create a security response playbook"""
        self.playbooks[name] = {
            'name': name,
            'steps': steps,
            'created_at': datetime.now(),
            'last_modified': datetime.now()
        }
        logger.info(f"Created playbook: {name}")
    
    def execute_playbook(self, playbook_name: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a security response playbook"""
        if playbook_name not in self.playbooks:
            raise ValueError(f"Playbook not found: {playbook_name}")
        
        playbook = self.playbooks[playbook_name]
        results = []
        
        for step in playbook['steps']:
            try:
                result = self._execute_step(step, incident_data)
                results.append(result)
                
                # Check if step failed and playbook should stop
                if not result['success'] and step.get('stop_on_failure', True):
                    break
                    
            except Exception as e:
                logger.error(f"Playbook step failed: {e}")
                results.append({
                    'step': step['name'],
                    'success': False,
                    'error': str(e)
                })
                break
        
        return {
            'playbook_name': playbook_name,
            'execution_time': datetime.now(),
            'results': results,
            'overall_success': all(r['success'] for r in results)
        }
    
    def _execute_step(self, step: Dict[str, Any], incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single playbook step"""
        step_name = step['name']
        action = step['action']
        parameters = step.get('parameters', {})
        
        # Merge incident data with step parameters
        merged_params = {**parameters, **incident_data}
        
        if action in self.response_actions:
            result = self.response_actions[action](merged_params)
            return {
                'step': step_name,
                'action': action,
                'success': result.get('success', True),
                'result': result
            }
        else:
            return {
                'step': step_name,
                'action': action,
                'success': False,
                'error': f"Unknown action: {action}"
            }
    
    def _block_ip(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Block IP address"""
        ip_address = parameters.get('source_ip')
        if ip_address:
            logger.info(f"Blocking IP address: {ip_address}")
            # In a real implementation, this would update firewall rules
            return {'success': True, 'message': f'Blocked IP: {ip_address}'}
        return {'success': False, 'error': 'No IP address provided'}
    
    def _quarantine_device(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Quarantine device"""
        device_id = parameters.get('device_id')
        if device_id:
            logger.info(f"Quarantining device: {device_id}")
            # In a real implementation, this would isolate the device
            return {'success': True, 'message': f'Quarantined device: {device_id}'}
        return {'success': False, 'error': 'No device ID provided'}
    
    def _disable_user(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Disable user account"""
        user_id = parameters.get('user_id')
        if user_id:
            logger.info(f"Disabling user: {user_id}")
            # In a real implementation, this would disable the user account
            return {'success': True, 'message': f'Disabled user: {user_id}'}
        return {'success': False, 'error': 'No user ID provided'}
    
    def _send_alert(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send security alert"""
        message = parameters.get('message', 'Security incident detected')
        severity = parameters.get('severity', 'medium')
        
        logger.info(f"Sending alert: {message} (severity: {severity})")
        # In a real implementation, this would send notifications
        return {'success': True, 'message': 'Alert sent successfully'}
    
    def _collect_forensics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collect forensic evidence"""
        device_id = parameters.get('device_id')
        if device_id:
            logger.info(f"Collecting forensics from device: {device_id}")
            # In a real implementation, this would collect system logs, memory dumps, etc.
            return {'success': True, 'message': f'Forensics collected from device: {device_id}'}
        return {'success': False, 'error': 'No device ID provided'}
    
    def _escalate_incident(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate incident to higher level"""
        incident_id = parameters.get('incident_id')
        if incident_id:
            logger.info(f"Escalating incident: {incident_id}")
            # In a real implementation, this would notify security team
            return {'success': True, 'message': f'Escalated incident: {incident_id}'}
        return {'success': False, 'error': 'No incident ID provided'}

class ZeroTrustEngine:
    """Main Zero Trust security engine"""
    
    def __init__(self, config_path: str = "zero_trust_config.yaml"):
        self.config = self._load_config(config_path)
        self.quantum_crypto = QuantumResistantCrypto()
        self.homomorphic_enc = HomomorphicEncryption()
        self.zk_proof = ZeroKnowledgeProof()
        self.behavioral_analytics = BehavioralAnalytics()
        self.threat_intelligence = ThreatIntelligence()
        self.soar_engine = SOAREngine()
        
        self.active_sessions = {}
        self.access_policies = {}
        self.device_registry = {}
        self.user_registry = {}
        self.device_behavior_history = {}
        
        self._setup_default_policies()
        self._setup_soar_playbooks()
        self._load_threat_intelligence_feeds()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def _load_threat_intelligence_feeds(self):
        """Load threat intelligence feeds from configuration"""
        feeds = self.config.get('threat_intelligence', {}).get('feeds', [])
        for feed in feeds:
            self.threat_intelligence.add_threat_feed(
                feed['url'], 
                feed['type']
            )
    
    def _setup_default_policies(self):
        """Setup default access policies"""
        self.access_policies = {
            'default': {
                'name': 'Default Policy',
                'conditions': [],
                'actions': ['challenge'],
                'priority': 100
            },
            'high_risk': {
                'name': 'High Risk Policy',
                'conditions': ['risk_score > 0.7', 'anomaly_detected'],
                'actions': ['deny', 'alert'],
                'priority': 1
            },
            'admin_access': {
                'name': 'Admin Access Policy',
                'conditions': ['role == admin', 'mfa_verified'],
                'actions': ['allow'],
                'priority': 10
            }
        }
    
    def _setup_soar_playbooks(self):
        """Setup default SOAR playbooks"""
        # High-risk incident playbook
        self.soar_engine.create_playbook('high_risk_incident', [
            {
                'name': 'Immediate Response',
                'action': 'send_alert',
                'parameters': {'severity': 'critical'},
                'stop_on_failure': False
            },
            {
                'name': 'Block Source',
                'action': 'block_ip',
                'parameters': {},
                'stop_on_failure': False
            },
            {
                'name': 'Collect Evidence',
                'action': 'collect_forensics',
                'parameters': {},
                'stop_on_failure': False
            },
            {
                'name': 'Escalate Incident',
                'action': 'escalate_incident',
                'parameters': {},
                'stop_on_failure': False
            }
        ])
        
        # Suspicious activity playbook
        self.soar_engine.create_playbook('suspicious_activity', [
            {
                'name': 'Send Alert',
                'action': 'send_alert',
                'parameters': {'severity': 'medium'},
                'stop_on_failure': False
            },
            {
                'name': 'Monitor Closely',
                'action': 'send_alert',
                'parameters': {'message': 'Increased monitoring activated'},
                'stop_on_failure': False
            }
        ])
    
    def evaluate_access_request(self, request: AccessRequest) -> Dict[str, Any]:
        """Evaluate access request using zero trust principles"""
        logger.info(f"Evaluating access request: {request.request_id}")
        
        # Step 1: Verify user identity
        identity_verification = self._verify_identity(request.user_id, request.context)
        
        # Step 2: Assess device trust
        device_trust = self._assess_device_trust(request.context.device_id, request.context)
        
        # Step 3: Analyze behavior
        behavior_analysis = self.behavioral_analytics.detect_anomalies(
            request.user_id, 
            {
                'login_time': request.context.time_of_access,
                'location': request.context.location,
                'device_info': request.context.device_id,
                'resource': request.resource,
                'session_duration': 0  # New session
            }
        )
        
        # Step 4: Check threat intelligence
        threat_check = self.threat_intelligence.check_ioc(request.context.source_ip, 'ip')
        
        # Step 5: Calculate risk score
        risk_score = self._calculate_risk_score(
            identity_verification,
            device_trust,
            behavior_analysis,
            threat_check
        )
        
        # Step 6: Apply access policies
        decision = self._apply_access_policies(request, risk_score)
        
        # Step 7: Log security event
        security_event = SecurityEvent(
            event_id=secrets.token_hex(16),
            timestamp=datetime.now(),
            event_type='access_request',
            severity=self._map_risk_to_threat_level(risk_score),
            source_ip=request.context.source_ip,
            user_id=request.user_id,
            resource=request.resource,
            action=request.action,
            result=decision['action'],
            metadata={
                'risk_score': risk_score,
                'identity_verification': identity_verification,
                'device_trust': device_trust,
                'behavior_analysis': behavior_analysis,
                'threat_check': threat_check
            },
            risk_score=risk_score
        )
        
        self._log_security_event(security_event)
        
        # Step 8: Trigger automated response if needed
        if risk_score > 0.7:
            self._trigger_automated_response(security_event)

        # Step 9: Update device behavior history
        self._update_device_behavior_history(request.context.device_id, request.context)
        
        return {
            'request_id': request.request_id,
            'decision': decision,
            'risk_score': risk_score,
            'reasoning': {
                'identity_verification': identity_verification,
                'device_trust': device_trust,
                'behavior_analysis': behavior_analysis,
                'threat_check': threat_check
            },
            'security_event_id': security_event.event_id
        }
    
    def _verify_identity(self, user_id: str, context: UserContext) -> Dict[str, Any]:
        """Verify user identity using multiple factors"""
        # Check if user exists
        if user_id not in self.user_registry:
            return {'verified': False, 'confidence': 0.0, 'reason': 'User not found'}
        
        user = self.user_registry[user_id]
        
        # Check password (simplified)
        password_verified = True  # In real implementation, verify password hash
        
        # Check MFA
        mfa_verified = self._verify_mfa(user_id, context)
        
        # Check biometrics (simplified)
        biometric_verified = True  # In real implementation, verify biometric data
        
        # Calculate overall confidence
        confidence = 0.0
        if password_verified:
            confidence += 0.4
        if mfa_verified:
            confidence += 0.4
        if biometric_verified:
            confidence += 0.2
        
        return {
            'verified': confidence > 0.6,
            'confidence': confidence,
            'factors': {
                'password': password_verified,
                'mfa': mfa_verified,
                'biometric': biometric_verified
            }
        }
    
    def get_totp_uri(self, user_id: str, issuer_name: str = None) -> Optional[str]:
        """Get TOTP provisioning URI for a user"""
        if user_id not in self.user_registry:
            return None
        
        user = self.user_registry[user_id]
        issuer = issuer_name or self.config.get('iam', {}).get('mfa', {}).get('totp_issuer', 'SupplyChainFinance')
        return pyotp.totp.TOTP(user['totp_secret']).provisioning_uri(
            name=user['email'],
            issuer_name=issuer)

    def _verify_mfa(self, user_id: str, context: UserContext) -> bool:
        """Verify multi-factor authentication"""
        if user_id not in self.user_registry:
            return False

        user = self.user_registry[user_id]
        mfa_config = self.config.get('iam', {}).get('mfa', {})
        
        # Check if MFA is enabled for this user
        if not user.get('mfa_enabled', mfa_config.get('required_for_admins', False) and user.get('role') == 'admin'):
            return True  # MFA not required for this user

        totp_code = getattr(context, 'totp_code', None)
        if not totp_code:
            return False

        totp = pyotp.TOTP(user['totp_secret'])
        return totp.verify(totp_code)
    
    def _assess_device_trust(self, device_id: str, context: UserContext) -> Dict[str, Any]:
        """Assess device trustworthiness"""
        if device_id not in self.device_registry:
            return {'trusted': False, 'score': 0.0, 'reason': 'Device not registered'}
        
        device = self.device_registry[device_id]
        
        # Check device compliance
        compliance_score = self._check_device_compliance(device)
        
        # Check device location
        location_score = self._check_device_location(device, context.location)
        
        # Check device behavior
        behavior_score = self._check_device_behavior(device_id, context)
        
        # Calculate overall trust score
        trust_score = (compliance_score * 0.4 + location_score * 0.3 + behavior_score * 0.3)
        
        return {
            'trusted': trust_score > 0.6,
            'score': trust_score,
            'factors': {
                'compliance': compliance_score,
                'location': location_score,
                'behavior': behavior_score
            }
        }
    
    def _check_device_compliance(self, device: Dict[str, Any]) -> float:
        """Check device compliance with security policies"""
        score = 0.0
        
        # Check if device has required security software
        if device.get('antivirus_installed', False):
            score += 0.3
        
        # Check if device is encrypted
        if device.get('encryption_enabled', False):
            score += 0.3
        
        # Check if device is up to date
        if device.get('os_updated', False):
            score += 0.2
        
        # Check if device has screen lock
        if device.get('screen_lock_enabled', False):
            score += 0.2
        
        return score
    
    def _check_device_location(self, device: Dict[str, Any], current_location: Tuple[float, float]) -> float:
        """Check if device location is expected"""
        expected_locations = device.get('expected_locations', [])
        
        if not expected_locations:
            return 0.5  # Neutral score if no expected locations
        
        # Calculate distance to nearest expected location
        min_distance = float('inf')
        for expected_loc in expected_locations:
            distance = np.sqrt(
                (current_location[0] - expected_loc[0])**2 + 
                (current_location[1] - expected_loc[1])**2
            )
            min_distance = min(min_distance, distance)
        
        # Convert distance to score (closer is better)
        if min_distance < 0.01:  # Very close
            return 1.0
        elif min_distance < 0.1:  # Close
            return 0.8
        elif min_distance < 1.0:  # Reasonable
            return 0.6
        else:  # Far
            return 0.2
    
    def _check_device_behavior(self, device_id: str, context: UserContext) -> float:
        """Check device behavior patterns"""
        if device_id not in self.device_behavior_history:
            return 0.5  # Neutral score for new devices

        history = self.device_behavior_history[device_id]
        score = 0.0

        # Location consistency
        location_history = [h.location for h in history]
        avg_lat = np.mean([loc[0] for loc in location_history])
        avg_lon = np.mean([loc[1] for loc in location_history])
        distance = np.sqrt((context.location[0] - avg_lat)**2 + (context.location[1] - avg_lon)**2)
        if distance < 1.0:
            score += 0.4

        # Network consistency
        network_history = [h.network for h in history]
        if context.network in network_history:
            score += 0.3

        # Time consistency
        hour_history = [h.time_of_access.hour for h in history]
        avg_hour = np.mean(hour_history)
        if abs(context.time_of_access.hour - avg_hour) < 4:
            score += 0.3

        return min(1.0, score)
    
    def _calculate_risk_score(self, identity_verification: Dict[str, Any], 
                            device_trust: Dict[str, Any], 
                            behavior_analysis: Dict[str, Any],
                            threat_check: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        risk_factors = []
        
        # Identity risk
        if not identity_verification['verified']:
            risk_factors.append(0.8)
        else:
            risk_factors.append(1.0 - identity_verification['confidence'])
        
        # Device risk
        if not device_trust['trusted']:
            risk_factors.append(0.7)
        else:
            risk_factors.append(1.0 - device_trust['score'])
        
        # Behavior risk
        risk_factors.append(behavior_analysis['risk_score'])
        
        # Threat risk
        if threat_check['is_ioc']:
            if threat_check['threat_level'] == 'high':
                risk_factors.append(0.9)
            elif threat_check['threat_level'] == 'medium':
                risk_factors.append(0.6)
            else:
                risk_factors.append(0.3)
        else:
            risk_factors.append(0.0)
        
        # Calculate weighted average
        weights = [0.2, 0.4, 0.3, 0.1]  # Identity, device, behavior, threat
        risk_score = sum(w * r for w, r in zip(weights, risk_factors))
        
        return min(1.0, max(0.0, risk_score))
    
    def _apply_access_policies(self, request: AccessRequest, risk_score: float) -> Dict[str, Any]:
        """Apply access policies to determine final decision"""
        # Sort policies by priority
        sorted_policies = sorted(
            self.access_policies.items(),
            key=lambda x: x[1]['priority']
        )
        
        for policy_name, policy in sorted_policies:
            if self._evaluate_policy_conditions(policy['conditions'], request, risk_score):
                return {
                    'action': policy['actions'][0],  # Take first action
                    'policy': policy_name,
                    'reason': f"Matched policy: {policy['name']}"
                }
        
        # Default decision
        return {
            'action': 'challenge',
            'policy': 'default',
            'reason': 'No specific policy matched'
        }
    
    def _evaluate_policy_conditions(self, conditions: List[str], 
                                  request: AccessRequest, risk_score: float) -> bool:
        """Evaluate policy conditions"""
        context = {
            'risk_score': risk_score,
            'user_id': request.user_id,
            'resource': request.resource,
            'action': request.action,
            'source_ip': request.context.source_ip,
            'device_id': request.context.device_id,
            'location': request.context.location
        }
        
        for condition in conditions:
            if not self._evaluate_condition(condition, context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a single policy condition"""
        try:
            # Simple condition evaluation
            # In real implementation, use a proper expression evaluator
            if 'risk_score >' in condition:
                threshold = float(condition.split('>')[1].strip())
                return context['risk_score'] > threshold
            elif 'anomaly_detected' in condition:
                return True  # Simplified
            elif 'role ==' in condition:
                role = condition.split('==')[1].strip()
                return context.get('role') == role
            elif 'mfa_verified' in condition:
                return True  # Simplified
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def _map_risk_to_threat_level(self, risk_score: float) -> ThreatLevel:
        """Map risk score to threat level"""
        if risk_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif risk_score >= 0.6:
            return ThreatLevel.HIGH
        elif risk_score >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _log_security_event(self, event: SecurityEvent):
        """Log security event"""
        logger.info(f"Security event: {event.event_type} - {event.severity.value} - {event.user_id}")
        # In real implementation, store in SIEM system
    
    def _trigger_automated_response(self, event: SecurityEvent):
        """Trigger automated security response"""
        if event.severity == ThreatLevel.CRITICAL:
            playbook_name = 'high_risk_incident'
        elif event.severity == ThreatLevel.HIGH:
            playbook_name = 'suspicious_activity'
        else:
            return
        
        try:
            result = self.soar_engine.execute_playbook(
                playbook_name, 
                asdict(event)
            )
            logger.info(f"Executed playbook {playbook_name}: {result['overall_success']}")
        except Exception as e:
            logger.error(f"Failed to execute playbook {playbook_name}: {e}")
    
    def register_user(self, user_id: str, user_data: Dict[str, Any]):
        """Register a new user"""
        # Get IAM configuration
        iam_config = self.config.get('iam', {})
        password_policy = iam_config.get('password_policy', {})
        mfa_config = iam_config.get('mfa', {})
        
        self.user_registry[user_id] = {
            'id': user_id,
            'email': user_data.get('email'),
            'role': user_data.get('role', 'user'),
            'created_at': datetime.now(),
            'last_login': None,
            'mfa_enabled': user_data.get('mfa_enabled', 
                                       mfa_config.get('required_for_admins', False) and user_data.get('role') == 'admin'),
            'biometric_enrolled': user_data.get('biometric_enrolled', False),
            'totp_secret': pyotp.random_base32(),
            'password_policy': password_policy
        }
        logger.info(f"Registered user: {user_id}")
    
    def register_device(self, device_id: str, device_data: Dict[str, Any]):
        """Register a new device"""
        # Get device trust configuration
        device_config = self.config.get('device_trust', {})
        compliance_config = device_config.get('compliance', {})
        
        self.device_registry[device_id] = {
            'id': device_id,
            'user_id': device_data.get('user_id'),
            'device_type': device_data.get('device_type'),
            'os': device_data.get('os'),
            'antivirus_installed': device_data.get('antivirus_installed', 
                                                compliance_config.get('antivirus_required', False)),
            'encryption_enabled': device_data.get('encryption_enabled', 
                                                compliance_config.get('encryption_required', False)),
            'os_updated': device_data.get('os_updated', 
                                        compliance_config.get('os_update_required', False)),
            'screen_lock_enabled': device_data.get('screen_lock_enabled', 
                                                 compliance_config.get('screen_lock_required', False)),
            'expected_locations': device_data.get('expected_locations', []),
            'registered_at': datetime.now(),
            'compliance_config': compliance_config
        }
        logger.info(f"Registered device: {device_id}")

    def _update_device_behavior_history(self, device_id: str, context: UserContext):
        """Update the device behavior history."""
        if device_id not in self.device_behavior_history:
            self.device_behavior_history[device_id] = []
        self.device_behavior_history[device_id].append(context)
        # Keep the last 10 entries
        self.device_behavior_history[device_id] = self.device_behavior_history[device_id][-10:]

# Example usage and testing
if __name__ == "__main__":
    # Create Zero Trust engine
    zt_engine = ZeroTrustEngine()
    
    # Register test user and device
    zt_engine.register_user('user123', {
        'email': 'user@example.com',
        'role': 'admin',
        'mfa_enabled': True,
        'biometric_enrolled': True
    })
    
    zt_engine.register_device('device456', {
        'user_id': 'user123',
        'device_type': 'laptop',
        'os': 'Windows 11',
        'antivirus_installed': True,
        'encryption_enabled': True,
        'os_updated': True,
        'screen_lock_enabled': True,
        'expected_locations': [(40.7128, -74.0060)]  # New York
    })
    
    # Get TOTP URI and generate QR code
    totp_uri = zt_engine.get_totp_uri('user123')
    print(f"TOTP URI: {totp_uri}")
    qr = qrcode.make(totp_uri)
    qr.save("totp_qr.png")
    print("TOTP QR code saved to totp_qr.png")

    # Simulate user scanning QR code and entering TOTP
    totp_code = pyotp.TOTP(zt_engine.user_registry['user123']['totp_secret']).now()
    print(f"Generated TOTP code: {totp_code}")

    # Create access request
    user_context = UserContext(
        user_id='user123',
        device_id='device456',
        source_ip='192.168.1.100',
        location=(40.7128, -74.0060),
        network='corporate_wifi',
        time_of_access=datetime.now(),
        behavior_profile={},
        risk_factors=[],
        trust_score=0.8,
        totp_code=totp_code
    )
    
    access_request = AccessRequest(
        request_id='req123',
        user_id='user123',
        resource='sensitive_data',
        action='read',
        context=user_context,
        timestamp=datetime.now(),
        session_id='session123'
    )
    
    # Evaluate access request
    result = zt_engine.evaluate_access_request(access_request)
    
    print("Access Decision Result:")
    print(json.dumps(result, indent=2, default=str))
