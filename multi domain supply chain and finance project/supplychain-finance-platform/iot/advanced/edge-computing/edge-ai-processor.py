"""
Advanced Edge Computing and AI Processing
Demonstrating mastery of IoT and edge computing from intermediate to advanced levels

This module showcases:
- Edge AI processing with TensorFlow Lite
- Real-time data streaming and processing
- Edge-to-cloud synchronization
- Predictive maintenance algorithms
- Digital twin implementations
- Edge device management
- Real-time analytics and monitoring
- Swarm intelligence for IoT networks
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import cv2
import json
import time
import threading
import queue
import logging
import asyncio
import websockets
import paho.mqtt.client as mqtt
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque
import sqlite3
import pickle
import hashlib
import hmac
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import GPUtil
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import yaml
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SensorData:
    """Sensor data structure for edge processing"""
    device_id: str
    timestamp: datetime
    sensor_type: str
    value: float
    unit: str
    location: Tuple[float, float]
    quality_score: float
    metadata: Dict[str, Any]

@dataclass
class EdgeProcessingResult:
    """Result of edge processing operations"""
    device_id: str
    processing_type: str
    result: Any
    confidence: float
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class DigitalTwinState:
    """Digital twin state representation"""
    device_id: str
    state: str
    health_score: float
    predicted_failure_time: Optional[datetime]
    maintenance_recommendations: List[str]
    performance_metrics: Dict[str, float]
    last_updated: datetime

class EdgeAIModel:
    """Edge AI Model for real-time inference"""
    
    def __init__(self, model_path: str, model_type: str = "tflite"):
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.input_shape = None
        self.output_shape = None
        self.preprocessor = None
        self.postprocessor = None
        self.load_model()
    
    def load_model(self):
        """Load AI model for edge inference"""
        try:
            if self.model_type == "tflite":
                # Load TensorFlow Lite model
                self.model = tf.lite.Interpreter(model_path=self.model_path)
                self.model.allocate_tensors()
                
                # Get input and output details
                input_details = self.model.get_input_details()
                output_details = self.model.get_output_details()
                
                self.input_shape = input_details[0]['shape']
                self.output_shape = output_details[0]['shape']
                
                logger.info(f"Loaded TFLite model: {self.model_path}")
                
            elif self.model_type == "onnx":
                # Load ONNX model (would require onnxruntime)
                logger.info("ONNX model loading not implemented")
                
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """Preprocess input data"""
        if self.preprocessor:
            return self.preprocessor.transform(data)
        return data
    
    def postprocess(self, output: np.ndarray) -> Any:
        """Postprocess model output"""
        if self.postprocessor:
            return self.postprocessor(output)
        return output
    
    def predict(self, data: np.ndarray) -> Tuple[Any, float]:
        """Run inference on input data"""
        start_time = time.time()
        
        try:
            # Preprocess data
            processed_data = self.preprocess(data)
            
            # Ensure correct shape
            if processed_data.shape != tuple(self.input_shape[1:]):
                processed_data = processed_data.reshape(1, *self.input_shape[1:])
            
            # Run inference
            if self.model_type == "tflite":
                input_details = self.model.get_input_details()
                output_details = self.model.get_output_details()
                
                self.model.set_tensor(input_details[0]['index'], processed_data.astype(np.float32))
                self.model.invoke()
                
                output = self.model.get_tensor(output_details[0]['index'])
            else:
                output = processed_data  # Placeholder
            
            # Postprocess output
            result = self.postprocess(output)
            
            # Calculate confidence (simplified)
            confidence = float(np.max(output)) if hasattr(output, 'max') else 0.8
            
            processing_time = time.time() - start_time
            
            return result, confidence
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None, 0.0

class RealTimeDataProcessor:
    """Real-time data processing for edge devices"""
    
    def __init__(self, buffer_size: int = 1000, processing_interval: float = 1.0):
        self.buffer_size = buffer_size
        self.processing_interval = processing_interval
        self.data_buffer = deque(maxlen=buffer_size)
        self.processing_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.is_processing = False
        self.processors = {}
        self.callbacks = []
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
    
    def add_processor(self, name: str, processor: Callable):
        """Add a data processor"""
        self.processors[name] = processor
        logger.info(f"Added processor: {name}")
    
    def add_callback(self, callback: Callable):
        """Add a callback for processed results"""
        self.callbacks.append(callback)
    
    def add_data(self, data: SensorData):
        """Add sensor data to processing queue"""
        self.data_buffer.append(data)
        self.processing_queue.put(data)
    
    def _processing_loop(self):
        """Main processing loop"""
        self.is_processing = True
        
        while self.is_processing:
            try:
                # Get data from queue with timeout
                data = self.processing_queue.get(timeout=1.0)
                
                # Process data with all processors
                results = []
                for name, processor in self.processors.items():
                    try:
                        start_time = time.time()
                        result = processor(data)
                        processing_time = time.time() - start_time
                        
                        edge_result = EdgeProcessingResult(
                            device_id=data.device_id,
                            processing_type=name,
                            result=result,
                            confidence=0.8,  # Simplified
                            processing_time=processing_time,
                            timestamp=datetime.now(),
                            metadata={}
                        )
                        
                        results.append(edge_result)
                        
                    except Exception as e:
                        logger.error(f"Processor {name} failed: {e}")
                
                # Store results
                for result in results:
                    self.results_queue.put(result)
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(results)
                    except Exception as e:
                        logger.error(f"Callback failed: {e}")
                
                self.processing_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
    
    def stop_processing(self):
        """Stop the processing loop"""
        self.is_processing = False
        if self.processing_thread.is_alive():
            self.processing_thread.join()

class PredictiveMaintenanceEngine:
    """Predictive maintenance using edge AI"""
    
    def __init__(self, model_path: str):
        self.model = EdgeAIModel(model_path, "tflite")
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.device_history = {}
        self.failure_threshold = 0.7
        self.maintenance_threshold = 0.5
        
    def analyze_device_health(self, device_id: str, sensor_data: List[SensorData]) -> DigitalTwinState:
        """Analyze device health and predict maintenance needs"""
        
        # Extract features from sensor data
        features = self._extract_features(sensor_data)
        
        # Predict failure probability
        failure_probability, confidence = self.model.predict(features)
        
        # Detect anomalies
        anomaly_score = self._detect_anomalies(features)
        
        # Calculate health score
        health_score = self._calculate_health_score(failure_probability, anomaly_score)
        
        # Predict failure time
        predicted_failure_time = self._predict_failure_time(device_id, health_score)
        
        # Generate maintenance recommendations
        recommendations = self._generate_recommendations(health_score, features)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(sensor_data)
        
        # Determine device state
        if health_score < self.failure_threshold:
            state = "critical"
        elif health_score < self.maintenance_threshold:
            state = "maintenance_required"
        else:
            state = "healthy"
        
        return DigitalTwinState(
            device_id=device_id,
            state=state,
            health_score=health_score,
            predicted_failure_time=predicted_failure_time,
            maintenance_recommendations=recommendations,
            performance_metrics=performance_metrics,
            last_updated=datetime.now()
        )
    
    def _extract_features(self, sensor_data: List[SensorData]) -> np.ndarray:
        """Extract features from sensor data"""
        features = []
        
        for data in sensor_data:
            feature_vector = [
                data.value,
                data.quality_score,
                data.timestamp.hour,
                data.timestamp.dayofweek,
                data.location[0],  # latitude
                data.location[1],  # longitude
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _detect_anomalies(self, features: np.ndarray) -> float:
        """Detect anomalies in sensor data"""
        try:
            # Fit anomaly detector if not already fitted
            if not hasattr(self.anomaly_detector, 'decision_function'):
                self.anomaly_detector.fit(features)
            
            # Calculate anomaly score
            anomaly_scores = self.anomaly_detector.decision_function(features)
            return float(np.mean(anomaly_scores))
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return 0.0
    
    def _calculate_health_score(self, failure_probability: float, anomaly_score: float) -> float:
        """Calculate overall device health score"""
        # Normalize failure probability (0-1, where 1 is worst)
        failure_score = 1.0 - failure_probability
        
        # Normalize anomaly score (higher is better)
        anomaly_normalized = max(0, min(1, (anomaly_score + 1) / 2))
        
        # Weighted combination
        health_score = 0.7 * failure_score + 0.3 * anomaly_normalized
        
        return max(0, min(1, health_score))
    
    def _predict_failure_time(self, device_id: str, health_score: float) -> Optional[datetime]:
        """Predict when device might fail"""
        if health_score > 0.8:
            return None  # No failure predicted
        
        # Simple linear prediction based on health score
        days_to_failure = (1.0 - health_score) * 30  # Max 30 days
        
        return datetime.now() + timedelta(days=days_to_failure)
    
    def _generate_recommendations(self, health_score: float, features: np.ndarray) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []
        
        if health_score < 0.3:
            recommendations.append("Immediate maintenance required - device at risk of failure")
        elif health_score < 0.5:
            recommendations.append("Schedule maintenance within 7 days")
        elif health_score < 0.7:
            recommendations.append("Monitor closely - maintenance may be needed soon")
        
        # Feature-based recommendations
        if len(features) > 0:
            avg_value = np.mean(features[:, 0])  # Average sensor value
            if avg_value > 0.8:
                recommendations.append("High sensor readings detected - check calibration")
            elif avg_value < 0.2:
                recommendations.append("Low sensor readings detected - check connections")
        
        return recommendations
    
    def _calculate_performance_metrics(self, sensor_data: List[SensorData]) -> Dict[str, float]:
        """Calculate performance metrics"""
        if not sensor_data:
            return {}
        
        values = [data.value for data in sensor_data]
        quality_scores = [data.quality_score for data in sensor_data]
        
        return {
            "average_value": float(np.mean(values)),
            "value_std": float(np.std(values)),
            "average_quality": float(np.mean(quality_scores)),
            "data_points": len(sensor_data),
            "value_range": float(np.max(values) - np.min(values))
        }

class EdgeDeviceManager:
    """Manage edge devices and their communication"""
    
    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.devices = {}
        self.mqtt_client = None
        self.websocket_server = None
        self.connected_clients = set()
        
        self._setup_mqtt()
        self._setup_websocket()
    
    def _setup_mqtt(self):
        """Setup MQTT client for device communication"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def _setup_websocket(self):
        """Setup WebSocket server for real-time communication"""
        async def websocket_handler(websocket, path):
            self.connected_clients.add(websocket)
            logger.info(f"WebSocket client connected: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    await self._handle_websocket_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.connected_clients.remove(websocket)
                logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server in a separate thread
        def start_websocket_server():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            start_server = websockets.serve(websocket_handler, "localhost", 8765)
            loop.run_until_complete(start_server)
            loop.run_forever()
        
        websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
        websocket_thread.start()
        logger.info("WebSocket server started on localhost:8765")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("MQTT client connected successfully")
            client.subscribe("devices/+/sensor_data")
            client.subscribe("devices/+/status")
        else:
            logger.error(f"MQTT connection failed with code: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic_parts = msg.topic.split('/')
            device_id = topic_parts[1]
            message_type = topic_parts[2]
            
            data = json.loads(msg.payload.decode())
            
            if message_type == "sensor_data":
                sensor_data = SensorData(
                    device_id=device_id,
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    sensor_type=data['sensor_type'],
                    value=data['value'],
                    unit=data['unit'],
                    location=tuple(data['location']),
                    quality_score=data.get('quality_score', 1.0),
                    metadata=data.get('metadata', {})
                )
                
                self._process_device_data(device_id, sensor_data)
                
            elif message_type == "status":
                self._update_device_status(device_id, data)
                
        except Exception as e:
            logger.error(f"Failed to process MQTT message: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"MQTT client disconnected with code: {rc}")
    
    async def _handle_websocket_message(self, websocket, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'get_device_status':
                device_id = data.get('device_id')
                status = self.devices.get(device_id, {})
                await websocket.send(json.dumps({
                    'type': 'device_status',
                    'device_id': device_id,
                    'status': status
                }))
                
            elif command == 'get_all_devices':
                await websocket.send(json.dumps({
                    'type': 'all_devices',
                    'devices': list(self.devices.keys())
                }))
                
        except Exception as e:
            logger.error(f"WebSocket message handling failed: {e}")
    
    def _process_device_data(self, device_id: str, sensor_data: SensorData):
        """Process incoming device data"""
        if device_id not in self.devices:
            self.devices[device_id] = {
                'last_seen': datetime.now(),
                'sensor_data': deque(maxlen=1000),
                'status': 'active',
                'health_score': 1.0
            }
        
        self.devices[device_id]['sensor_data'].append(sensor_data)
        self.devices[device_id]['last_seen'] = datetime.now()
        
        # Broadcast to WebSocket clients
        self._broadcast_to_websockets({
            'type': 'sensor_data',
            'device_id': device_id,
            'data': asdict(sensor_data)
        })
    
    def _update_device_status(self, device_id: str, status_data: Dict[str, Any]):
        """Update device status"""
        if device_id not in self.devices:
            self.devices[device_id] = {}
        
        self.devices[device_id].update(status_data)
        self.devices[device_id]['last_seen'] = datetime.now()
    
    def _broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        message_str = json.dumps(message)
        
        async def broadcast():
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
        
        # Run broadcast in event loop
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast())
        except RuntimeError:
            # Create new event loop if none exists
            asyncio.run(broadcast())
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status of a specific device"""
        return self.devices.get(device_id, {})
    
    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all devices"""
        return self.devices.copy()
    
    def send_command_to_device(self, device_id: str, command: Dict[str, Any]):
        """Send command to a specific device"""
        topic = f"devices/{device_id}/commands"
        message = json.dumps(command)
        
        try:
            self.mqtt_client.publish(topic, message)
            logger.info(f"Sent command to device {device_id}: {command}")
        except Exception as e:
            logger.error(f"Failed to send command to device {device_id}: {e}")

class SwarmIntelligenceManager:
    """Swarm intelligence for IoT network optimization"""
    
    def __init__(self, network_size: int = 100):
        self.network_size = network_size
        self.nodes = {}
        self.connections = {}
        self.optimization_algorithms = {
            'ant_colony': self._ant_colony_optimization,
            'particle_swarm': self._particle_swarm_optimization,
            'genetic_algorithm': self._genetic_algorithm_optimization
        }
    
    def add_node(self, node_id: str, capabilities: List[str], location: Tuple[float, float]):
        """Add a node to the swarm network"""
        self.nodes[node_id] = {
            'capabilities': capabilities,
            'location': location,
            'status': 'active',
            'load': 0.0,
            'energy_level': 1.0,
            'neighbors': set()
        }
    
    def optimize_network(self, algorithm: str = 'ant_colony') -> Dict[str, Any]:
        """Optimize network using swarm intelligence"""
        if algorithm not in self.optimization_algorithms:
            raise ValueError(f"Unknown optimization algorithm: {algorithm}")
        
        return self.optimization_algorithms[algorithm]()
    
    def _ant_colony_optimization(self) -> Dict[str, Any]:
        """Ant Colony Optimization for network routing"""
        # Simplified ACO implementation
        num_ants = 50
        num_iterations = 100
        alpha = 1.0  # Pheromone importance
        beta = 2.0   # Distance importance
        evaporation_rate = 0.1
        
        # Initialize pheromone trails
        pheromones = {}
        for node1 in self.nodes:
            for node2 in self.nodes:
                if node1 != node2:
                    pheromones[(node1, node2)] = 1.0
        
        best_path = None
        best_distance = float('inf')
        
        for iteration in range(num_iterations):
            # Each ant finds a path
            for ant in range(num_ants):
                path = self._ant_find_path(pheromones, alpha, beta)
                distance = self._calculate_path_distance(path)
                
                if distance < best_distance:
                    best_distance = distance
                    best_path = path
            
            # Update pheromones
            self._update_pheromones(pheromones, best_path, best_distance, evaporation_rate)
        
        return {
            'algorithm': 'ant_colony',
            'best_path': best_path,
            'best_distance': best_distance,
            'optimization_time': time.time()
        }
    
    def _particle_swarm_optimization(self) -> Dict[str, Any]:
        """Particle Swarm Optimization for load balancing"""
        num_particles = 30
        num_iterations = 50
        w = 0.9  # Inertia weight
        c1 = 2.0  # Cognitive parameter
        c2 = 2.0  # Social parameter
        
        # Initialize particles
        particles = []
        for i in range(num_particles):
            particle = {
                'position': np.random.random(len(self.nodes)),
                'velocity': np.random.random(len(self.nodes)) * 0.1,
                'best_position': None,
                'best_fitness': float('inf')
            }
            particles.append(particle)
        
        global_best_position = None
        global_best_fitness = float('inf')
        
        for iteration in range(num_iterations):
            for particle in particles:
                # Calculate fitness
                fitness = self._calculate_load_balancing_fitness(particle['position'])
                
                # Update personal best
                if fitness < particle['best_fitness']:
                    particle['best_fitness'] = fitness
                    particle['best_position'] = particle['position'].copy()
                
                # Update global best
                if fitness < global_best_fitness:
                    global_best_fitness = fitness
                    global_best_position = particle['position'].copy()
            
            # Update particle velocities and positions
            for particle in particles:
                r1, r2 = np.random.random(2)
                
                particle['velocity'] = (w * particle['velocity'] +
                                      c1 * r1 * (particle['best_position'] - particle['position']) +
                                      c2 * r2 * (global_best_position - particle['position']))
                
                particle['position'] += particle['velocity']
                particle['position'] = np.clip(particle['position'], 0, 1)
        
        return {
            'algorithm': 'particle_swarm',
            'best_load_distribution': global_best_position.tolist(),
            'best_fitness': global_best_fitness,
            'optimization_time': time.time()
        }
    
    def _genetic_algorithm_optimization(self) -> Dict[str, Any]:
        """Genetic Algorithm for network topology optimization"""
        population_size = 50
        num_generations = 100
        mutation_rate = 0.1
        crossover_rate = 0.8
        
        # Initialize population
        population = []
        for i in range(population_size):
            individual = self._generate_random_topology()
            population.append(individual)
        
        best_individual = None
        best_fitness = float('inf')
        
        for generation in range(num_generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._calculate_topology_fitness(individual)
                fitness_scores.append(fitness)
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Selection, crossover, and mutation
            new_population = []
            
            # Elitism: keep best individual
            new_population.append(best_individual)
            
            # Generate new individuals
            while len(new_population) < population_size:
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                if np.random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                if np.random.random() < mutation_rate:
                    child1 = self._mutate(child1)
                if np.random.random() < mutation_rate:
                    child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:population_size]
        
        return {
            'algorithm': 'genetic_algorithm',
            'best_topology': best_individual,
            'best_fitness': best_fitness,
            'optimization_time': time.time()
        }
    
    def _ant_find_path(self, pheromones: Dict, alpha: float, beta: float) -> List[str]:
        """Ant finds a path through the network"""
        start_node = np.random.choice(list(self.nodes.keys()))
        path = [start_node]
        unvisited = set(self.nodes.keys()) - {start_node}
        
        current = start_node
        while unvisited:
            probabilities = []
            for next_node in unvisited:
                pheromone = pheromones.get((current, next_node), 0.1)
                distance = self._calculate_distance(current, next_node)
                probability = (pheromone ** alpha) * ((1.0 / distance) ** beta)
                probabilities.append(probability)
            
            # Select next node based on probabilities
            probabilities = np.array(probabilities)
            probabilities = probabilities / np.sum(probabilities)
            next_node = np.random.choice(list(unvisited), p=probabilities)
            
            path.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        
        return path
    
    def _calculate_path_distance(self, path: List[str]) -> float:
        """Calculate total distance of a path"""
        total_distance = 0.0
        for i in range(len(path) - 1):
            total_distance += self._calculate_distance(path[i], path[i + 1])
        return total_distance
    
    def _calculate_distance(self, node1: str, node2: str) -> float:
        """Calculate distance between two nodes"""
        loc1 = self.nodes[node1]['location']
        loc2 = self.nodes[node2]['location']
        return np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
    
    def _update_pheromones(self, pheromones: Dict, best_path: List[str], 
                          best_distance: float, evaporation_rate: float):
        """Update pheromone trails"""
        # Evaporate existing pheromones
        for key in pheromones:
            pheromones[key] *= (1 - evaporation_rate)
        
        # Add pheromones to best path
        if best_path:
            pheromone_deposit = 1.0 / best_distance
            for i in range(len(best_path) - 1):
                edge = (best_path[i], best_path[i + 1])
                if edge in pheromones:
                    pheromones[edge] += pheromone_deposit
    
    def _calculate_load_balancing_fitness(self, load_distribution: np.ndarray) -> float:
        """Calculate fitness for load balancing"""
        # Minimize variance in load distribution
        return float(np.var(load_distribution))
    
    def _generate_random_topology(self) -> Dict[str, Any]:
        """Generate random network topology"""
        topology = {}
        for node_id in self.nodes:
            topology[node_id] = {
                'connections': np.random.choice(
                    list(self.nodes.keys()), 
                    size=np.random.randint(1, 4), 
                    replace=False
                ).tolist()
            }
        return topology
    
    def _calculate_topology_fitness(self, topology: Dict[str, Any]) -> float:
        """Calculate fitness of network topology"""
        # Minimize total connection cost while maintaining connectivity
        total_cost = 0.0
        for node_id, config in topology.items():
            for connected_node in config['connections']:
                total_cost += self._calculate_distance(node_id, connected_node)
        return total_cost
    
    def _tournament_selection(self, population: List, fitness_scores: List[float], 
                            tournament_size: int = 3) -> Dict[str, Any]:
        """Tournament selection for genetic algorithm"""
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[np.argmin(tournament_fitness)]
        return population[winner_index]
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Crossover operation for genetic algorithm"""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Simple crossover: swap connections for half the nodes
        nodes = list(self.nodes.keys())
        crossover_point = len(nodes) // 2
        
        for i in range(crossover_point):
            node_id = nodes[i]
            child1[node_id], child2[node_id] = child2[node_id], child1[node_id]
        
        return child1, child2
    
    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Mutation operation for genetic algorithm"""
        mutated = individual.copy()
        
        # Randomly change connections for some nodes
        for node_id in np.random.choice(list(self.nodes.keys()), 
                                      size=np.random.randint(1, 3), 
                                      replace=False):
            mutated[node_id]['connections'] = np.random.choice(
                list(self.nodes.keys()), 
                size=np.random.randint(1, 4), 
                replace=False
            ).tolist()
        
        return mutated

class EdgeComputingOrchestrator:
    """Main orchestrator for edge computing operations"""
    
    def __init__(self, config_path: str = "edge_config.yaml"):
        self.config = self._load_config(config_path)
        self.data_processor = RealTimeDataProcessor(
            buffer_size=self.config.get('buffer_size', 1000),
            processing_interval=self.config.get('processing_interval', 1.0)
        )
        self.device_manager = EdgeDeviceManager(
            mqtt_broker=self.config.get('mqtt_broker', 'localhost'),
            mqtt_port=self.config.get('mqtt_port', 1883)
        )
        self.swarm_manager = SwarmIntelligenceManager(
            network_size=self.config.get('network_size', 100)
        )
        self.maintenance_engines = {}
        
        self._setup_processing_pipeline()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def _setup_processing_pipeline(self):
        """Setup the data processing pipeline"""
        # Add predictive maintenance processor
        maintenance_processor = PredictiveMaintenanceEngine(
            model_path=self.config.get('maintenance_model_path', 'models/maintenance.tflite')
        )
        
        def maintenance_processor_func(data: SensorData):
            return maintenance_processor.analyze_device_health(data.device_id, [data])
        
        self.data_processor.add_processor('predictive_maintenance', maintenance_processor_func)
        
        # Add anomaly detection processor
        def anomaly_detector_func(data: SensorData):
            # Simple anomaly detection based on value thresholds
            if data.value > 100 or data.value < 0:
                return {'anomaly_detected': True, 'severity': 'high'}
            elif data.value > 80 or data.value < 10:
                return {'anomaly_detected': True, 'severity': 'medium'}
            else:
                return {'anomaly_detected': False, 'severity': 'low'}
        
        self.data_processor.add_processor('anomaly_detection', anomaly_detector_func)
        
        # Add callback for processed results
        def results_callback(results: List[EdgeProcessingResult]):
            for result in results:
                logger.info(f"Processing result: {result.processing_type} for device {result.device_id}")
                
                # Send results to cloud if needed
                if result.confidence > 0.8:
                    self._send_to_cloud(result)
        
        self.data_processor.add_callback(results_callback)
    
    def _send_to_cloud(self, result: EdgeProcessingResult):
        """Send processing results to cloud"""
        # In a real implementation, this would send data to cloud services
        logger.info(f"Sending result to cloud: {result.processing_type}")
    
    def start(self):
        """Start the edge computing orchestrator"""
        logger.info("Starting Edge Computing Orchestrator")
        
        # Start all components
        # The data processor and device manager are already running in their own threads
        
        logger.info("Edge Computing Orchestrator started successfully")
    
    def stop(self):
        """Stop the edge computing orchestrator"""
        logger.info("Stopping Edge Computing Orchestrator")
        
        self.data_processor.stop_processing()
        
        if self.device_manager.mqtt_client:
            self.device_manager.mqtt_client.loop_stop()
            self.device_manager.mqtt_client.disconnect()
        
        logger.info("Edge Computing Orchestrator stopped")

# Example usage and testing
if __name__ == "__main__":
    # Create edge computing orchestrator
    orchestrator = EdgeComputingOrchestrator()
    
    try:
        # Start the orchestrator
        orchestrator.start()
        
        # Simulate some sensor data
        for i in range(10):
            sensor_data = SensorData(
                device_id=f"device_{i % 3}",
                timestamp=datetime.now(),
                sensor_type="temperature",
                value=np.random.normal(25, 5),
                unit="celsius",
                location=(40.7128 + np.random.normal(0, 0.01), -74.0060 + np.random.normal(0, 0.01)),
                quality_score=np.random.uniform(0.8, 1.0),
                metadata={"sensor_model": "DS18B20", "calibration_date": "2023-01-01"}
            )
            
            orchestrator.data_processor.add_data(sensor_data)
            time.sleep(1)
        
        # Run for a while
        time.sleep(30)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        orchestrator.stop()
