"""
Advanced Platform Engineering and DevOps
Demonstrating mastery of DevOps, SRE, and Platform Engineering from intermediate to advanced levels

This module showcases:
- Infrastructure as Code (IaC) with Terraform
- Kubernetes orchestration and management
- CI/CD pipeline automation
- Service mesh implementation
- Observability and monitoring
- Chaos engineering
- GitOps workflows
- Platform as a Service (PaaS) capabilities
- Multi-cloud deployment strategies
- SRE practices and SLIs/SLOs
"""

import yaml
import json
import time
import logging
import asyncio
import threading
import subprocess
import docker
import kubernetes
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import terraform
import ansible
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import requests
import psutil
import GPUtil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
import sqlite3
import redis
import consul
import vault
import nomad
import jenkins
import gitlab
import github
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import hashlib
import hmac
import secrets
import base64
import jwt
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceLevelIndicator:
    """Service Level Indicator definition"""
    name: str
    description: str
    metric_type: str  # 'counter', 'histogram', 'gauge'
    query: str
    target_value: float
    measurement_window: str  # e.g., '5m', '1h', '1d'

@dataclass
class ServiceLevelObjective:
    """Service Level Objective definition"""
    name: str
    description: str
    sli: ServiceLevelIndicator
    target_percentage: float  # e.g., 99.9
    error_budget: float
    measurement_window: str

@dataclass
class DeploymentStatus:
    """Deployment status information"""
    deployment_id: str
    service_name: str
    version: str
    status: str  # 'pending', 'running', 'failed', 'completed'
    start_time: datetime
    end_time: Optional[datetime]
    replicas: int
    ready_replicas: int
    metadata: Dict[str, Any]

class InfrastructureAsCode:
    """Infrastructure as Code management using Terraform"""
    
    def __init__(self, working_dir: str = "./terraform"):
        self.working_dir = working_dir
        self.terraform_client = terraform.Terraform(working_dir=working_dir)
        self.state_file = os.path.join(working_dir, "terraform.tfstate")
        
    def initialize_terraform(self):
        """Initialize Terraform workspace"""
        try:
            result = self.terraform_client.init()
            logger.info("Terraform initialized successfully")
            return result
        except Exception as e:
            logger.error(f"Terraform initialization failed: {e}")
            raise
    
    def plan_infrastructure(self, config_file: str) -> Dict[str, Any]:
        """Plan infrastructure changes"""
        try:
            result = self.terraform_client.plan(
                var_file=config_file,
                out="terraform.tfplan"
            )
            logger.info("Infrastructure plan generated")
            return {
                'plan_output': result,
                'plan_file': 'terraform.tfplan'
            }
        except Exception as e:
            logger.error(f"Infrastructure planning failed: {e}")
            raise
    
    def apply_infrastructure(self, plan_file: str) -> Dict[str, Any]:
        """Apply infrastructure changes"""
        try:
            result = self.terraform_client.apply(plan_file)
            logger.info("Infrastructure applied successfully")
            return {
                'apply_output': result,
                'state_file': self.state_file
            }
        except Exception as e:
            logger.error(f"Infrastructure application failed: {e}")
            raise
    
    def destroy_infrastructure(self) -> Dict[str, Any]:
        """Destroy infrastructure"""
        try:
            result = self.terraform_client.destroy(auto_approve=True)
            logger.info("Infrastructure destroyed successfully")
            return {'destroy_output': result}
        except Exception as e:
            logger.error(f"Infrastructure destruction failed: {e}")
            raise
    
    def get_infrastructure_state(self) -> Dict[str, Any]:
        """Get current infrastructure state"""
        try:
            result = self.terraform_client.show()
            return {'state': result}
        except Exception as e:
            logger.error(f"Failed to get infrastructure state: {e}")
            raise

class KubernetesOrchestrator:
    """Kubernetes orchestration and management"""
    
    def __init__(self, config_file: Optional[str] = None):
        if config_file:
            config.load_kube_config(config_file)
        else:
            config.load_incluster_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.metrics_v1 = client.CustomObjectsApi()
        
    def deploy_application(self, deployment_config: Dict[str, Any]) -> DeploymentStatus:
        """Deploy application to Kubernetes"""
        deployment_id = secrets.token_hex(8)
        
        try:
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=deployment_config['name'],
                    namespace=deployment_config.get('namespace', 'default')
                ),
                spec=client.V1DeploymentSpec(
                    replicas=deployment_config.get('replicas', 3),
                    selector=client.V1LabelSelector(
                        match_labels={"app": deployment_config['name']}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": deployment_config['name']}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=deployment_config['name'],
                                    image=deployment_config['image'],
                                    ports=[client.V1ContainerPort(
                                        container_port=deployment_config.get('port', 8080)
                                    )],
                                    resources=client.V1ResourceRequirements(
                                        requests=deployment_config.get('resources', {}).get('requests', {}),
                                        limits=deployment_config.get('resources', {}).get('limits', {})
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            # Apply deployment
            result = self.apps_v1.create_namespaced_deployment(
                namespace=deployment_config.get('namespace', 'default'),
                body=deployment
            )
            
            # Create service
            service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=f"{deployment_config['name']}-service"
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": deployment_config['name']},
                    ports=[client.V1ServicePort(
                        port=deployment_config.get('port', 8080),
                        target_port=deployment_config.get('port', 8080)
                    )],
                    type=deployment_config.get('service_type', 'ClusterIP')
                )
            )
            
            self.v1.create_namespaced_service(
                namespace=deployment_config.get('namespace', 'default'),
                body=service
            )
            
            return DeploymentStatus(
                deployment_id=deployment_id,
                service_name=deployment_config['name'],
                version=deployment_config.get('version', 'latest'),
                status='running',
                start_time=datetime.now(),
                end_time=None,
                replicas=deployment_config.get('replicas', 3),
                ready_replicas=0,  # Will be updated by monitoring
                metadata={'kubernetes_deployment': result.metadata.name}
            )
            
        except ApiException as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise
    
    def scale_application(self, deployment_name: str, namespace: str, replicas: int):
        """Scale application replicas"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Apply changes
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Scaled {deployment_name} to {replicas} replicas")
            
        except ApiException as e:
            logger.error(f"Scaling failed: {e}")
            raise
    
    def get_deployment_status(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """Get deployment status"""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            return {
                'name': deployment.metadata.name,
                'namespace': deployment.metadata.namespace,
                'replicas': deployment.spec.replicas,
                'ready_replicas': deployment.status.ready_replicas or 0,
                'available_replicas': deployment.status.available_replicas or 0,
                'unavailable_replicas': deployment.status.unavailable_replicas or 0,
                'conditions': [
                    {
                        'type': condition.type,
                        'status': condition.status,
                        'message': condition.message
                    }
                    for condition in deployment.status.conditions or []
                ]
            }
            
        except ApiException as e:
            logger.error(f"Failed to get deployment status: {e}")
            raise
    
    def create_ingress(self, ingress_config: Dict[str, Any]):
        """Create ingress for external access"""
        try:
            ingress = client.V1Ingress(
                metadata=client.V1ObjectMeta(
                    name=ingress_config['name'],
                    namespace=ingress_config.get('namespace', 'default'),
                    annotations=ingress_config.get('annotations', {})
                ),
                spec=client.V1IngressSpec(
                    rules=[
                        client.V1IngressRule(
                            host=rule['host'],
                            http=client.V1HTTPIngressRuleValue(
                                paths=[
                                    client.V1HTTPIngressPath(
                                        path=path['path'],
                                        path_type=path.get('path_type', 'Prefix'),
                                        backend=client.V1IngressBackend(
                                            service=client.V1IngressServiceBackend(
                                                name=path['service_name'],
                                                port=client.V1ServiceBackendPort(
                                                    number=path['service_port']
                                                )
                                            )
                                        )
                                    )
                                    for path in rule['paths']
                                ]
                            )
                        )
                        for rule in ingress_config['rules']
                    ]
                )
            )
            
            result = self.networking_v1.create_namespaced_ingress(
                namespace=ingress_config.get('namespace', 'default'),
                body=ingress
            )
            
            logger.info(f"Ingress created: {result.metadata.name}")
            return result
            
        except ApiException as e:
            logger.error(f"Ingress creation failed: {e}")
            raise

class CICDPipeline:
    """CI/CD pipeline automation"""
    
    def __init__(self, jenkins_url: str, jenkins_user: str, jenkins_token: str):
        self.jenkins_client = jenkins.Jenkins(
            jenkins_url, 
            username=jenkins_user, 
            password=jenkins_token
        )
        self.pipeline_configs = {}
        
    def create_pipeline(self, pipeline_name: str, pipeline_config: Dict[str, Any]):
        """Create CI/CD pipeline"""
        jenkinsfile = self._generate_jenkinsfile(pipeline_config)
        
        try:
            # Create pipeline job
            job_config = self._create_job_config(pipeline_name, jenkinsfile)
            self.jenkins_client.create_job(pipeline_name, job_config)
            
            self.pipeline_configs[pipeline_name] = pipeline_config
            logger.info(f"Pipeline created: {pipeline_name}")
            
        except Exception as e:
            logger.error(f"Pipeline creation failed: {e}")
            raise
    
    def _generate_jenkinsfile(self, config: Dict[str, Any]) -> str:
        """Generate Jenkinsfile from configuration"""
        jenkinsfile = f"""
pipeline {{
    agent any
    
    environment {{
        DOCKER_REGISTRY = '{config.get('docker_registry', 'localhost:5000')}'
        KUBERNETES_NAMESPACE = '{config.get('namespace', 'default')}'
        IMAGE_TAG = '${{BUILD_NUMBER}}'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Build') {{
            steps {{
                script {{
                    // Build application
                    sh 'docker build -t ${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}} .'
                }}
            }}
        }}
        
        stage('Test') {{
            steps {{
                script {{
                    // Run tests
                    sh 'docker run --rm ${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}} npm test'
                }}
            }}
        }}
        
        stage('Security Scan') {{
            steps {{
                script {{
                    // Security scanning
                    sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}}'
                }}
            }}
        }}
        
        stage('Push') {{
            steps {{
                script {{
                    // Push to registry
                    sh 'docker push ${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}}'
                }}
            }}
        }}
        
        stage('Deploy') {{
            steps {{
                script {{
                    // Deploy to Kubernetes
                    sh 'kubectl set image deployment/${{JOB_NAME}} ${{JOB_NAME}}=${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}} -n ${{KUBERNETES_NAMESPACE}}'
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            // Cleanup
            sh 'docker rmi ${{DOCKER_REGISTRY}}/${{JOB_NAME}}:${{IMAGE_TAG}} || true'
        }}
        
        success {{
            // Notify success
            echo 'Deployment successful'
        }}
        
        failure {{
            // Notify failure
            echo 'Deployment failed'
        }}
    }}
}}
"""
        return jenkinsfile
    
    def _create_job_config(self, job_name: str, jenkinsfile: str) -> str:
        """Create Jenkins job configuration"""
        config = f"""
<?xml version='1.0' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <description>CI/CD Pipeline for {job_name}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.90">
    <script>{jenkinsfile}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>H/5 * * * *</spec>
    </hudson.triggers.SCMTrigger>
  </triggers>
  <disabled>false</disabled>
</flow-definition>
"""
        return config
    
    def trigger_pipeline(self, pipeline_name: str, parameters: Dict[str, Any] = None):
        """Trigger pipeline execution"""
        try:
            if parameters:
                self.jenkins_client.build_job(pipeline_name, parameters)
            else:
                self.jenkins_client.build_job(pipeline_name)
            
            logger.info(f"Pipeline triggered: {pipeline_name}")
            
        except Exception as e:
            logger.error(f"Pipeline trigger failed: {e}")
            raise
    
    def get_pipeline_status(self, pipeline_name: str) -> Dict[str, Any]:
        """Get pipeline execution status"""
        try:
            job_info = self.jenkins_client.get_job_info(pipeline_name)
            builds = job_info.get('builds', [])
            
            if builds:
                latest_build = builds[0]
                build_info = self.jenkins_client.get_build_info(
                    pipeline_name, 
                    latest_build['number']
                )
                
                return {
                    'pipeline_name': pipeline_name,
                    'build_number': latest_build['number'],
                    'status': build_info['result'],
                    'duration': build_info['duration'],
                    'timestamp': build_info['timestamp'],
                    'url': build_info['url']
                }
            
            return {'pipeline_name': pipeline_name, 'status': 'no_builds'}
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            raise

class ServiceMesh:
    """Service mesh implementation using Istio"""
    
    def __init__(self, istio_namespace: str = "istio-system"):
        self.istio_namespace = istio_namespace
        self.networking_v1 = client.NetworkingV1Api()
        
    def create_virtual_service(self, virtual_service_config: Dict[str, Any]):
        """Create Istio virtual service"""
        try:
            # This would typically use Istio's custom resources
            # For demonstration, we'll create a simplified version
            
            virtual_service = {
                'apiVersion': 'networking.istio.io/v1alpha3',
                'kind': 'VirtualService',
                'metadata': {
                    'name': virtual_service_config['name'],
                    'namespace': virtual_service_config.get('namespace', 'default')
                },
                'spec': {
                    'hosts': virtual_service_config['hosts'],
                    'http': virtual_service_config.get('http', [])
                }
            }
            
            logger.info(f"Virtual service created: {virtual_service_config['name']}")
            return virtual_service
            
        except Exception as e:
            logger.error(f"Virtual service creation failed: {e}")
            raise
    
    def create_destination_rule(self, destination_rule_config: Dict[str, Any]):
        """Create Istio destination rule"""
        try:
            destination_rule = {
                'apiVersion': 'networking.istio.io/v1alpha3',
                'kind': 'DestinationRule',
                'metadata': {
                    'name': destination_rule_config['name'],
                    'namespace': destination_rule_config.get('namespace', 'default')
                },
                'spec': {
                    'host': destination_rule_config['host'],
                    'trafficPolicy': destination_rule_config.get('trafficPolicy', {})
                }
            }
            
            logger.info(f"Destination rule created: {destination_rule_config['name']}")
            return destination_rule
            
        except Exception as e:
            logger.error(f"Destination rule creation failed: {e}")
            raise
    
    def configure_circuit_breaker(self, service_name: str, 
                                circuit_breaker_config: Dict[str, Any]):
        """Configure circuit breaker for service"""
        try:
            destination_rule = {
                'apiVersion': 'networking.istio.io/v1alpha3',
                'kind': 'DestinationRule',
                'metadata': {
                    'name': f"{service_name}-circuit-breaker",
                    'namespace': 'default'
                },
                'spec': {
                    'host': service_name,
                    'trafficPolicy': {
                        'connectionPool': {
                            'tcp': {
                                'maxConnections': circuit_breaker_config.get('max_connections', 10)
                            },
                            'http': {
                                'http1MaxPendingRequests': circuit_breaker_config.get('max_pending_requests', 10),
                                'maxRequestsPerConnection': circuit_breaker_config.get('max_requests_per_connection', 2)
                            }
                        },
                        'outlierDetection': {
                            'consecutiveErrors': circuit_breaker_config.get('consecutive_errors', 3),
                            'interval': circuit_breaker_config.get('interval', '30s'),
                            'baseEjectionTime': circuit_breaker_config.get('base_ejection_time', '30s'),
                            'maxEjectionPercent': circuit_breaker_config.get('max_ejection_percent', 50)
                        }
                    }
                }
            }
            
            logger.info(f"Circuit breaker configured for: {service_name}")
            return destination_rule
            
        except Exception as e:
            logger.error(f"Circuit breaker configuration failed: {e}")
            raise

class ObservabilityStack:
    """Observability and monitoring stack"""
    
    def __init__(self):
        self.metrics = {
            'request_counter': Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status']),
            'request_duration': Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint']),
            'active_connections': Gauge('active_connections', 'Active connections'),
            'memory_usage': Gauge('memory_usage_bytes', 'Memory usage in bytes'),
            'cpu_usage': Gauge('cpu_usage_percent', 'CPU usage percentage'),
            'disk_usage': Gauge('disk_usage_bytes', 'Disk usage in bytes')
        }
        
        # Start Prometheus metrics server
        start_http_server(8000)
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'].set(disk.used)
            
            # GPU usage (if available)
            gpu_usage = 0
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = gpus[0].load * 100
            except:
                pass
            
            return {
                'cpu_percent': cpu_percent,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'disk_used': disk.used,
                'disk_percent': (disk.used / disk.total) * 100,
                'gpu_usage': gpu_usage,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def create_alert_rule(self, alert_config: Dict[str, Any]):
        """Create Prometheus alert rule"""
        alert_rule = {
            'groups': [
                {
                    'name': alert_config['group_name'],
                    'rules': [
                        {
                            'alert': alert_config['alert_name'],
                            'expr': alert_config['expression'],
                            'for': alert_config.get('for_duration', '5m'),
                            'labels': alert_config.get('labels', {}),
                            'annotations': alert_config.get('annotations', {})
                        }
                    ]
                }
            ]
        }
        
        logger.info(f"Alert rule created: {alert_config['alert_name']}")
        return alert_rule
    
    def setup_log_aggregation(self, log_config: Dict[str, Any]):
        """Setup log aggregation with ELK stack"""
        # This would typically involve configuring Elasticsearch, Logstash, and Kibana
        # For demonstration, we'll create a simplified configuration
        
        elasticsearch_config = {
            'cluster_name': log_config.get('cluster_name', 'supply-chain-logs'),
            'node_name': log_config.get('node_name', 'log-node-1'),
            'network_host': log_config.get('network_host', '0.0.0.0'),
            'http_port': log_config.get('http_port', 9200)
        }
        
        logstash_config = {
            'input': {
                'beats': {
                    'port': log_config.get('beats_port', 5044)
                }
            },
            'filter': {
                'grok': {
                    'match': {
                        'message': '%{COMBINEDAPACHELOG}'
                    }
                }
            },
            'output': {
                'elasticsearch': {
                    'hosts': [f"localhost:{elasticsearch_config['http_port']}"]
                }
            }
        }
        
        kibana_config = {
            'server_name': log_config.get('kibana_host', 'localhost'),
            'server_port': log_config.get('kibana_port', 5601),
            'elasticsearch_url': f"http://localhost:{elasticsearch_config['http_port']}"
        }
        
        logger.info("Log aggregation configured")
        return {
            'elasticsearch': elasticsearch_config,
            'logstash': logstash_config,
            'kibana': kibana_config
        }

class ChaosEngineering:
    """Chaos engineering for resilience testing"""
    
    def __init__(self, kubernetes_client):
        self.k8s_client = kubernetes_client
        self.chaos_experiments = {}
        
    def create_chaos_experiment(self, experiment_config: Dict[str, Any]):
        """Create chaos engineering experiment"""
        experiment_id = secrets.token_hex(8)
        
        experiment = {
            'id': experiment_id,
            'name': experiment_config['name'],
            'description': experiment_config['description'],
            'target': experiment_config['target'],
            'chaos_type': experiment_config['chaos_type'],
            'parameters': experiment_config.get('parameters', {}),
            'duration': experiment_config.get('duration', '5m'),
            'status': 'created',
            'created_at': datetime.now()
        }
        
        self.chaos_experiments[experiment_id] = experiment
        logger.info(f"Chaos experiment created: {experiment_id}")
        return experiment
    
    def execute_chaos_experiment(self, experiment_id: str):
        """Execute chaos engineering experiment"""
        if experiment_id not in self.chaos_experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.chaos_experiments[experiment_id]
        experiment['status'] = 'running'
        experiment['started_at'] = datetime.now()
        
        try:
            if experiment['chaos_type'] == 'pod_failure':
                self._simulate_pod_failure(experiment)
            elif experiment['chaos_type'] == 'network_delay':
                self._simulate_network_delay(experiment)
            elif experiment['chaos_type'] == 'resource_exhaustion':
                self._simulate_resource_exhaustion(experiment)
            elif experiment['chaos_type'] == 'service_unavailable':
                self._simulate_service_unavailable(experiment)
            else:
                raise ValueError(f"Unknown chaos type: {experiment['chaos_type']}")
            
            experiment['status'] = 'completed'
            experiment['completed_at'] = datetime.now()
            
        except Exception as e:
            experiment['status'] = 'failed'
            experiment['error'] = str(e)
            logger.error(f"Chaos experiment failed: {e}")
        
        return experiment
    
    def _simulate_pod_failure(self, experiment: Dict[str, Any]):
        """Simulate pod failure"""
        target_deployment = experiment['target']
        namespace = experiment['parameters'].get('namespace', 'default')
        
        # Scale down deployment to 0 replicas
        self.k8s_client.scale_application(
            target_deployment, 
            namespace, 
            0
        )
        
        # Wait for specified duration
        duration = self._parse_duration(experiment['duration'])
        time.sleep(duration)
        
        # Scale back up
        original_replicas = experiment['parameters'].get('original_replicas', 3)
        self.k8s_client.scale_application(
            target_deployment, 
            namespace, 
            original_replicas
        )
    
    def _simulate_network_delay(self, experiment: Dict[str, Any]):
        """Simulate network delay"""
        # This would typically use tools like Chaos Monkey or Litmus
        # For demonstration, we'll simulate the effect
        delay_ms = experiment['parameters'].get('delay_ms', 1000)
        duration = self._parse_duration(experiment['duration'])
        
        logger.info(f"Simulating network delay of {delay_ms}ms for {duration}s")
        time.sleep(duration)
    
    def _simulate_resource_exhaustion(self, experiment: Dict[str, Any]):
        """Simulate resource exhaustion"""
        resource_type = experiment['parameters'].get('resource_type', 'cpu')
        target_percentage = experiment['parameters'].get('target_percentage', 90)
        
        logger.info(f"Simulating {resource_type} exhaustion to {target_percentage}%")
        # In a real implementation, this would use tools like stress-ng
        duration = self._parse_duration(experiment['duration'])
        time.sleep(duration)
    
    def _simulate_service_unavailable(self, experiment: Dict[str, Any]):
        """Simulate service unavailability"""
        target_service = experiment['target']
        namespace = experiment['parameters'].get('namespace', 'default')
        
        # This would typically involve network policies or service mesh configuration
        logger.info(f"Simulating service unavailability for {target_service}")
        duration = self._parse_duration(experiment['duration'])
        time.sleep(duration)
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        if duration_str.endswith('s'):
            return int(duration_str[:-1])
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        else:
            return int(duration_str)

class SREPractices:
    """Site Reliability Engineering practices and SLIs/SLOs"""
    
    def __init__(self):
        self.slis = {}
        self.slos = {}
        self.error_budgets = {}
        
    def define_sli(self, sli: ServiceLevelIndicator):
        """Define Service Level Indicator"""
        self.slis[sli.name] = sli
        logger.info(f"SLI defined: {sli.name}")
    
    def define_slo(self, slo: ServiceLevelObjective):
        """Define Service Level Objective"""
        self.slos[slo.name] = slo
        self.error_budgets[slo.name] = {
            'total_budget': 100 - slo.target_percentage,
            'used_budget': 0.0,
            'remaining_budget': 100 - slo.target_percentage,
            'last_updated': datetime.now()
        }
        logger.info(f"SLO defined: {slo.name}")
    
    def calculate_sli_value(self, sli_name: str, time_window: str = '1h') -> float:
        """Calculate current SLI value"""
        if sli_name not in self.slis:
            raise ValueError(f"SLI not found: {sli_name}")
        
        sli = self.slis[sli_name]
        
        # This would typically query Prometheus or other monitoring system
        # For demonstration, we'll return a simulated value
        
        if sli.metric_type == 'counter':
            # Simulate availability calculation
            return 99.9  # 99.9% availability
        elif sli.metric_type == 'histogram':
            # Simulate latency calculation
            return 95.0  # 95th percentile latency
        elif sli.metric_type == 'gauge':
            # Simulate error rate calculation
            return 0.1  # 0.1% error rate
        
        return 0.0
    
    def calculate_slo_compliance(self, slo_name: str) -> Dict[str, Any]:
        """Calculate SLO compliance"""
        if slo_name not in self.slos:
            raise ValueError(f"SLO not found: {slo_name}")
        
        slo = self.slos[slo_name]
        current_sli_value = self.calculate_sli_value(slo.sli.name)
        
        # Calculate compliance
        if slo.sli.metric_type == 'counter':
            # For availability, higher is better
            compliance = current_sli_value >= slo.sli.target_value
        else:
            # For latency/error rate, lower is better
            compliance = current_sli_value <= slo.sli.target_value
        
        # Update error budget
        if not compliance:
            error_rate = abs(current_sli_value - slo.sli.target_value) / slo.sli.target_value
            self.error_budgets[slo_name]['used_budget'] += error_rate
            self.error_budgets[slo_name]['remaining_budget'] -= error_rate
        
        return {
            'slo_name': slo_name,
            'current_sli_value': current_sli_value,
            'target_value': slo.sli.target_value,
            'compliance': compliance,
            'error_budget': self.error_budgets[slo_name],
            'timestamp': datetime.now()
        }
    
    def generate_sre_report(self) -> Dict[str, Any]:
        """Generate SRE report"""
        report = {
            'timestamp': datetime.now(),
            'slis': {},
            'slos': {},
            'overall_health': 'healthy'
        }
        
        # Calculate SLI values
        for sli_name in self.slis:
            report['slis'][sli_name] = self.calculate_sli_value(sli_name)
        
        # Calculate SLO compliance
        compliance_count = 0
        total_slos = len(self.slos)
        
        for slo_name in self.slos:
            compliance = self.calculate_slo_compliance(slo_name)
            report['slos'][slo_name] = compliance
            
            if compliance['compliance']:
                compliance_count += 1
        
        # Determine overall health
        if compliance_count == total_slos:
            report['overall_health'] = 'healthy'
        elif compliance_count >= total_slos * 0.8:
            report['overall_health'] = 'degraded'
        else:
            report['overall_health'] = 'unhealthy'
        
        return report

class PlatformEngineering:
    """Main Platform Engineering orchestrator"""
    
    def __init__(self, config_path: str = "platform_config.yaml"):
        self.config = self._load_config(config_path)
        self.iac = InfrastructureAsCode()
        self.k8s_orchestrator = KubernetesOrchestrator()
        self.cicd_pipeline = CICDPipeline(
            self.config.get('jenkins_url', 'http://localhost:8080'),
            self.config.get('jenkins_user', 'admin'),
            self.config.get('jenkins_token', 'token')
        )
        self.service_mesh = ServiceMesh()
        self.observability = ObservabilityStack()
        self.chaos_engineering = ChaosEngineering(self.k8s_orchestrator)
        self.sre_practices = SREPractices()
        
        self.deployments = {}
        self.monitoring_active = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def deploy_platform(self, platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy complete platform"""
        logger.info("Starting platform deployment")
        
        deployment_results = {}
        
        # 1. Deploy infrastructure
        if platform_config.get('deploy_infrastructure', True):
            logger.info("Deploying infrastructure...")
            self.iac.initialize_terraform()
            plan_result = self.iac.plan_infrastructure(platform_config.get('terraform_config', 'main.tf'))
            apply_result = self.iac.apply_infrastructure(plan_result['plan_file'])
            deployment_results['infrastructure'] = apply_result
        
        # 2. Deploy applications
        if platform_config.get('deploy_applications', True):
            logger.info("Deploying applications...")
            for app_config in platform_config.get('applications', []):
                deployment_status = self.k8s_orchestrator.deploy_application(app_config)
                self.deployments[deployment_status.deployment_id] = deployment_status
                deployment_results[f"app_{app_config['name']}"] = deployment_status
        
        # 3. Configure service mesh
        if platform_config.get('configure_service_mesh', True):
            logger.info("Configuring service mesh...")
            for vs_config in platform_config.get('virtual_services', []):
                self.service_mesh.create_virtual_service(vs_config)
            
            for dr_config in platform_config.get('destination_rules', []):
                self.service_mesh.create_destination_rule(dr_config)
        
        # 4. Setup monitoring
        if platform_config.get('setup_monitoring', True):
            logger.info("Setting up monitoring...")
            self.observability.setup_log_aggregation(platform_config.get('logging', {}))
            
            for alert_config in platform_config.get('alerts', []):
                self.observability.create_alert_rule(alert_config)
        
        # 5. Define SLOs
        if platform_config.get('define_slos', True):
            logger.info("Defining SLOs...")
            for sli_config in platform_config.get('slis', []):
                sli = ServiceLevelIndicator(**sli_config)
                self.sre_practices.define_sli(sli)
            
            for slo_config in platform_config.get('slos', []):
                slo = ServiceLevelObjective(**slo_config)
                self.sre_practices.define_slo(slo)
        
        logger.info("Platform deployment completed")
        return deployment_results
    
    def start_monitoring(self):
        """Start platform monitoring"""
        self.monitoring_active = True
        
        def monitoring_worker():
            while self.monitoring_active:
                try:
                    # Collect system metrics
                    metrics = self.observability.collect_system_metrics()
                    
                    # Check SLO compliance
                    sre_report = self.sre_practices.generate_sre_report()
                    
                    # Log monitoring data
                    logger.info(f"Monitoring data: {metrics}")
                    logger.info(f"SRE report: {sre_report['overall_health']}")
                    
                    time.sleep(60)  # Monitor every minute
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
        
        logger.info("Platform monitoring started")
    
    def stop_monitoring(self):
        """Stop platform monitoring"""
        self.monitoring_active = False
        logger.info("Platform monitoring stopped")
    
    def run_chaos_experiment(self, experiment_config: Dict[str, Any]):
        """Run chaos engineering experiment"""
        experiment = self.chaos_engineering.create_chaos_experiment(experiment_config)
        result = self.chaos_engineering.execute_chaos_experiment(experiment['id'])
        
        logger.info(f"Chaos experiment completed: {result['status']}")
        return result
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status"""
        status = {
            'timestamp': datetime.now(),
            'deployments': {},
            'monitoring_active': self.monitoring_active,
            'sre_health': 'unknown'
        }
        
        # Get deployment statuses
        for deployment_id, deployment in self.deployments.items():
            if deployment.status == 'running':
                k8s_status = self.k8s_orchestrator.get_deployment_status(
                    deployment.service_name, 
                    'default'
                )
                status['deployments'][deployment_id] = k8s_status
        
        # Get SRE health
        try:
            sre_report = self.sre_practices.generate_sre_report()
            status['sre_health'] = sre_report['overall_health']
        except:
            pass
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Create platform engineering instance
    platform = PlatformEngineering()
    
    # Define platform configuration
    platform_config = {
        'deploy_infrastructure': False,  # Skip for demo
        'deploy_applications': True,
        'configure_service_mesh': True,
        'setup_monitoring': True,
        'define_slos': True,
        'applications': [
            {
                'name': 'supply-chain-api',
                'image': 'supply-chain-api:latest',
                'port': 8080,
                'replicas': 3,
                'resources': {
                    'requests': {'cpu': '100m', 'memory': '128Mi'},
                    'limits': {'cpu': '500m', 'memory': '512Mi'}
                }
            }
        ],
        'virtual_services': [
            {
                'name': 'supply-chain-vs',
                'hosts': ['supply-chain.example.com'],
                'http': [
                    {
                        'route': [
                            {
                                'destination': {
                                    'host': 'supply-chain-api-service',
                                    'port': {'number': 8080}
                                }
                            }
                        ]
                    }
                ]
            }
        ],
        'alerts': [
            {
                'group_name': 'supply-chain-alerts',
                'alert_name': 'HighErrorRate',
                'expression': 'rate(http_requests_total{status=~"5.."}[5m]) > 0.1',
                'for_duration': '5m',
                'labels': {'severity': 'warning'},
                'annotations': {'summary': 'High error rate detected'}
            }
        ],
        'slis': [
            {
                'name': 'availability',
                'description': 'Service availability',
                'metric_type': 'counter',
                'query': 'rate(http_requests_total[5m])',
                'target_value': 99.9,
                'measurement_window': '5m'
            }
        ],
        'slos': [
            {
                'name': 'availability_slo',
                'description': '99.9% availability',
                'sli': 'availability',
                'target_percentage': 99.9,
                'error_budget': 0.1,
                'measurement_window': '1h'
            }
        ]
    }
    
    try:
        # Deploy platform
        deployment_results = platform.deploy_platform(platform_config)
        print("Platform deployed successfully")
        
        # Start monitoring
        platform.start_monitoring()
        
        # Get platform status
        status = platform.get_platform_status()
        print(f"Platform status: {status['sre_health']}")
        
        # Run chaos experiment
        chaos_config = {
            'name': 'pod-failure-test',
            'description': 'Test pod failure resilience',
            'target': 'supply-chain-api',
            'chaos_type': 'pod_failure',
            'parameters': {
                'namespace': 'default',
                'original_replicas': 3
            },
            'duration': '30s'
        }
        
        chaos_result = platform.run_chaos_experiment(chaos_config)
        print(f"Chaos experiment result: {chaos_result['status']}")
        
        # Wait for monitoring
        time.sleep(120)
        
    except Exception as e:
        logger.error(f"Platform deployment failed: {e}")
    finally:
        # Stop monitoring
        platform.stop_monitoring()
