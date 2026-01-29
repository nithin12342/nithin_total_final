"""
Advanced MLOps Pipeline for Data Science
Demonstrating mastery of data science from intermediate to advanced levels

This module showcases:
- Automated ML pipeline orchestration
- Model versioning and experiment tracking
- Feature engineering and selection
- Model deployment and monitoring
- A/B testing and model comparison
- Data drift detection and model retraining
- Automated hyperparameter optimization
- Model explainability and interpretability
- Federated learning implementations
- Real-time model serving
"""

import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
import mlflow.tracking
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
import optuna
import shap
import lime
import lime.lime_tabular
from datetime import datetime, timedelta
import logging
import json
import yaml
import os
import sys
from typing import Dict, List, Tuple, Any, Optional, Union
import asyncio
import threading
import queue
import time
from dataclasses import dataclass, asdict
import requests
import redis
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import docker
import kubernetes
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import GPUtil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    rmse: float
    timestamp: datetime
    dataset_version: str
    hyperparameters: Dict[str, Any]

@dataclass
class ExperimentResult:
    """ML experiment result"""
    experiment_id: str
    model_name: str
    metrics: ModelMetrics
    feature_importance: Dict[str, float]
    training_time: float
    prediction_time: float
    model_size: int
    timestamp: datetime

class FeatureEngineeringPipeline:
    """Advanced feature engineering pipeline"""
    
    def __init__(self):
        self.feature_transforms = {}
        self.feature_selectors = {}
        self.encoders = {}
        self.scalers = {}
    
    def create_features(self, data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Create engineered features"""
        logger.info("Starting feature engineering pipeline")
        
        # Create time-based features
        data = self._create_time_features(data)
        
        # Create interaction features
        data = self._create_interaction_features(data)
        
        # Create statistical features
        data = self._create_statistical_features(data)
        
        # Create domain-specific features
        data = self._create_domain_features(data, target_column)
        
        # Handle missing values
        data = self._handle_missing_values(data)
        
        # Encode categorical variables
        data = self._encode_categorical_features(data)
        
        # Scale numerical features
        data = self._scale_features(data)
        
        logger.info(f"Feature engineering completed. Shape: {data.shape}")
        return data
    
    def _create_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        if 'timestamp' in data.columns:
            data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
            data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
            data['month'] = pd.to_datetime(data['timestamp']).dt.month
            data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
            data['is_business_hours'] = data['hour'].between(9, 17).astype(int)
        
        return data
    
    def _create_interaction_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        # Create polynomial features for top correlated pairs
        correlations = data[numerical_cols].corr().abs()
        top_pairs = []
        
        for i in range(len(correlations.columns)):
            for j in range(i+1, len(correlations.columns)):
                col1, col2 = correlations.columns[i], correlations.columns[j]
                if correlations.loc[col1, col2] > 0.5:
                    top_pairs.append((col1, col2))
        
        # Create interaction features for top pairs
        for col1, col2 in top_pairs[:5]:  # Limit to top 5 pairs
            data[f'{col1}_x_{col2}'] = data[col1] * data[col2]
            data[f'{col1}_div_{col2}'] = data[col1] / (data[col2] + 1e-8)
        
        return data
    
    def _create_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create statistical features"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            # Rolling statistics
            data[f'{col}_rolling_mean_7'] = data[col].rolling(window=7, min_periods=1).mean()
            data[f'{col}_rolling_std_7'] = data[col].rolling(window=7, min_periods=1).std()
            data[f'{col}_rolling_max_7'] = data[col].rolling(window=7, min_periods=1).max()
            data[f'{col}_rolling_min_7'] = data[col].rolling(window=7, min_periods=1).min()
            
            # Lag features
            data[f'{col}_lag_1'] = data[col].shift(1)
            data[f'{col}_lag_3'] = data[col].shift(3)
            data[f'{col}_lag_7'] = data[col].shift(7)
            
            # Difference features
            data[f'{col}_diff_1'] = data[col].diff(1)
            data[f'{col}_diff_7'] = data[col].diff(7)
        
        return data
    
    def _create_domain_features(self, data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Create domain-specific features for supply chain"""
        # Supply chain specific features
        if 'inventory_level' in data.columns and 'demand' in data.columns:
            data['inventory_turnover'] = data['demand'] / (data['inventory_level'] + 1e-8)
            data['stockout_risk'] = (data['inventory_level'] - data['demand']).clip(lower=0)
        
        if 'supplier_rating' in data.columns and 'delivery_time' in data.columns:
            data['supplier_efficiency'] = data['supplier_rating'] / (data['delivery_time'] + 1e-8)
        
        if 'price' in data.columns and 'cost' in data.columns:
            data['profit_margin'] = (data['price'] - data['cost']) / data['price']
            data['markup_ratio'] = data['price'] / (data['cost'] + 1e-8)
        
        return data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        for col in data.columns:
            if data[col].isnull().sum() > 0:
                if data[col].dtype in ['object', 'category']:
                    # Categorical: fill with mode
                    data[col].fillna(data[col].mode()[0] if not data[col].mode().empty else 'Unknown', inplace=True)
                else:
                    # Numerical: fill with median
                    data[col].fillna(data[col].median(), inplace=True)
        
        return data
    
    def _encode_categorical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                data[col] = self.encoders[col].fit_transform(data[col].astype(str))
            else:
                # Handle unseen categories
                unique_values = set(data[col].astype(str).unique())
                known_values = set(self.encoders[col].classes_)
                unseen_values = unique_values - known_values
                
                if unseen_values:
                    # Add unseen values to encoder
                    all_values = list(known_values) + list(unseen_values)
                    self.encoders[col] = LabelEncoder()
                    self.encoders[col].fit(all_values)
                
                data[col] = self.encoders[col].transform(data[col].astype(str))
        
        return data
    
    def _scale_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            if col not in self.scalers:
                self.scalers[col] = StandardScaler()
                data[col] = self.scalers[col].fit_transform(data[[col]]).flatten()
            else:
                data[col] = self.scalers[col].transform(data[[col]]).flatten()
        
        return data

class ModelVersioning:
    """Model versioning and experiment tracking"""
    
    def __init__(self, tracking_uri: str = "sqlite:///mlflow.db"):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = mlflow.tracking.MlflowClient()
        self.experiment_name = "supply_chain_ml"
        
        # Create experiment if it doesn't exist
        try:
            self.experiment_id = self.client.create_experiment(self.experiment_name)
        except:
            self.experiment_id = self.client.get_experiment_by_name(self.experiment_name).experiment_id
    
    def log_experiment(self, model, metrics: ModelMetrics, 
                      features: List[str], hyperparameters: Dict[str, Any]) -> str:
        """Log ML experiment"""
        with mlflow.start_run(experiment_id=self.experiment_id) as run:
            # Log parameters
            mlflow.log_params(hyperparameters)
            
            # Log metrics
            mlflow.log_metric("accuracy", metrics.accuracy)
            mlflow.log_metric("precision", metrics.precision)
            mlflow.log_metric("recall", metrics.recall)
            mlflow.log_metric("f1_score", metrics.f1_score)
            mlflow.log_metric("mse", metrics.mse)
            mlflow.log_metric("rmse", metrics.rmse)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(features, model.feature_importances_))
                mlflow.log_dict(feature_importance, "feature_importance.json")
            
            # Log model metadata
            mlflow.log_param("model_type", type(model).__name__)
            mlflow.log_param("dataset_version", metrics.dataset_version)
            mlflow.log_param("timestamp", metrics.timestamp.isoformat())
            
            return run.info.run_id
    
    def get_best_model(self, metric: str = "accuracy") -> Optional[Dict[str, Any]]:
        """Get the best model based on metric"""
        runs = self.client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} DESC"],
            max_results=1
        )
        
        if runs:
            run = runs[0]
            return {
                'run_id': run.info.run_id,
                'metrics': run.data.metrics,
                'params': run.data.params,
                'model_uri': f"runs:/{run.info.run_id}/model"
            }
        
        return None
    
    def compare_models(self, metric: str = "accuracy", top_k: int = 5) -> List[Dict[str, Any]]:
        """Compare top K models"""
        runs = self.client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} DESC"],
            max_results=top_k
        )
        
        results = []
        for run in runs:
            results.append({
                'run_id': run.info.run_id,
                'metrics': run.data.metrics,
                'params': run.data.params,
                'model_uri': f"runs:/{run.info.run_id}/model"
            })
        
        return results

class HyperparameterOptimization:
    """Automated hyperparameter optimization using Optuna"""
    
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials
        self.study = None
    
    def optimize_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series, 
                             X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Optimize Random Forest hyperparameters"""
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'bootstrap': trial.suggest_categorical('bootstrap', [True, False])
            }
            
            model = RandomForestRegressor(random_state=42, **params)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_val)
            mse = mean_squared_error(y_val, y_pred)
            
            return mse
        
        self.study = optuna.create_study(direction='minimize')
        self.study.optimize(objective, n_trials=self.n_trials)
        
        return {
            'best_params': self.study.best_params,
            'best_score': self.study.best_value,
            'n_trials': len(self.study.trials)
        }
    
    def optimize_classifier(self, X_train: pd.DataFrame, y_train: pd.Series,
                          X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Optimize classifier hyperparameters"""
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'class_weight': trial.suggest_categorical('class_weight', [None, 'balanced'])
            }
            
            model = RandomForestClassifier(random_state=42, **params)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_val)
            accuracy = accuracy_score(y_val, y_pred)
            
            return accuracy
        
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=self.n_trials)
        
        return {
            'best_params': self.study.best_params,
            'best_score': self.study.best_value,
            'n_trials': len(self.study.trials)
        }

class ModelExplainability:
    """Model explainability and interpretability"""
    
    def __init__(self):
        self.explainer = None
        self.shap_explainer = None
    
    def explain_model(self, model, X_test: pd.DataFrame, feature_names: List[str]) -> Dict[str, Any]:
        """Generate model explanations using SHAP and LIME"""
        explanations = {}
        
        # SHAP explanations
        try:
            self.shap_explainer = shap.TreeExplainer(model)
            shap_values = self.shap_explainer.shap_values(X_test)
            
            explanations['shap'] = {
                'values': shap_values.tolist() if isinstance(shap_values, np.ndarray) else shap_values,
                'feature_names': feature_names,
                'base_value': self.shap_explainer.expected_value
            }
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            explanations['shap'] = None
        
        # LIME explanations
        try:
            self.explainer = lime.lime_tabular.LimeTabularExplainer(
                X_test.values,
                feature_names=feature_names,
                mode='regression' if hasattr(model, 'predict') else 'classification'
            )
            
            lime_explanations = []
            for i in range(min(10, len(X_test))):  # Explain first 10 instances
                exp = self.explainer.explain_instance(
                    X_test.iloc[i].values,
                    model.predict,
                    num_features=len(feature_names)
                )
                lime_explanations.append({
                    'instance_id': i,
                    'explanation': exp.as_list(),
                    'prediction': model.predict([X_test.iloc[i].values])[0]
                })
            
            explanations['lime'] = lime_explanations
        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            explanations['lime'] = None
        
        return explanations
    
    def get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            return dict(zip(feature_names, model.feature_importances_))
        else:
            return {}

class DataDriftDetector:
    """Data drift detection and monitoring"""
    
    def __init__(self):
        self.reference_data = None
        self.drift_threshold = 0.05
        self.ks_statistic = None
        self.psi_scores = {}
    
    def set_reference_data(self, data: pd.DataFrame):
        """Set reference data for drift detection"""
        self.reference_data = data.copy()
        logger.info(f"Reference data set with shape: {data.shape}")
    
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect data drift in current data"""
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        drift_results = {}
        
        # Statistical drift detection
        drift_results['statistical'] = self._detect_statistical_drift(current_data)
        
        # PSI (Population Stability Index) drift detection
        drift_results['psi'] = self._detect_psi_drift(current_data)
        
        # Feature-wise drift detection
        drift_results['feature_drift'] = self._detect_feature_drift(current_data)
        
        # Overall drift score
        drift_results['overall_drift_score'] = self._calculate_overall_drift_score(drift_results)
        
        return drift_results
    
    def _detect_statistical_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect statistical drift using Kolmogorov-Smirnov test"""
        from scipy import stats
        
        numerical_cols = current_data.select_dtypes(include=[np.number]).columns
        drift_detected = {}
        
        for col in numerical_cols:
            if col in self.reference_data.columns:
                ks_stat, p_value = stats.ks_2samp(
                    self.reference_data[col].dropna(),
                    current_data[col].dropna()
                )
                
                drift_detected[col] = {
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'drift_detected': p_value < self.drift_threshold
                }
        
        return drift_detected
    
    def _detect_psi_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect drift using Population Stability Index"""
        numerical_cols = current_data.select_dtypes(include=[np.number]).columns
        psi_scores = {}
        
        for col in numerical_cols:
            if col in self.reference_data.columns:
                psi_score = self._calculate_psi(
                    self.reference_data[col],
                    current_data[col]
                )
                psi_scores[col] = {
                    'psi_score': psi_score,
                    'drift_level': self._interpret_psi_score(psi_score)
                }
        
        return psi_scores
    
    def _calculate_psi(self, reference: pd.Series, current: pd.Series) -> float:
        """Calculate Population Stability Index"""
        # Create bins
        bins = np.linspace(
            min(reference.min(), current.min()),
            max(reference.max(), current.max()),
            11
        )
        
        # Calculate distributions
        ref_dist = np.histogram(reference, bins=bins)[0] / len(reference)
        curr_dist = np.histogram(current, bins=bins)[0] / len(current)
        
        # Avoid division by zero
        ref_dist = np.where(ref_dist == 0, 0.0001, ref_dist)
        curr_dist = np.where(curr_dist == 0, 0.0001, curr_dist)
        
        # Calculate PSI
        psi = np.sum((curr_dist - ref_dist) * np.log(curr_dist / ref_dist))
        
        return psi
    
    def _interpret_psi_score(self, psi_score: float) -> str:
        """Interpret PSI score"""
        if psi_score < 0.1:
            return "No significant change"
        elif psi_score < 0.2:
            return "Moderate change"
        else:
            return "Significant change"
    
    def _detect_feature_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect feature-wise drift"""
        feature_drift = {}
        
        for col in current_data.columns:
            if col in self.reference_data.columns:
                # Calculate distribution similarity
                if current_data[col].dtype in ['object', 'category']:
                    # Categorical drift
                    ref_dist = self.reference_data[col].value_counts(normalize=True)
                    curr_dist = current_data[col].value_counts(normalize=True)
                    
                    # Calculate Jaccard similarity
                    common_categories = set(ref_dist.index) & set(curr_dist.index)
                    if common_categories:
                        jaccard_sim = len(common_categories) / len(set(ref_dist.index) | set(curr_dist.index))
                        feature_drift[col] = {
                            'drift_score': 1 - jaccard_sim,
                            'drift_type': 'categorical'
                        }
                else:
                    # Numerical drift
                    ref_mean = self.reference_data[col].mean()
                    curr_mean = current_data[col].mean()
                    ref_std = self.reference_data[col].std()
                    
                    if ref_std > 0:
                        drift_score = abs(curr_mean - ref_mean) / ref_std
                        feature_drift[col] = {
                            'drift_score': drift_score,
                            'drift_type': 'numerical'
                        }
        
        return feature_drift
    
    def _calculate_overall_drift_score(self, drift_results: Dict[str, Any]) -> float:
        """Calculate overall drift score"""
        scores = []
        
        # Statistical drift scores
        for col, result in drift_results['statistical'].items():
            if result['drift_detected']:
                scores.append(result['ks_statistic'])
        
        # PSI scores
        for col, result in drift_results['psi'].items():
            scores.append(result['psi_score'])
        
        # Feature drift scores
        for col, result in drift_results['feature_drift'].items():
            scores.append(result['drift_score'])
        
        return np.mean(scores) if scores else 0.0

class ModelDeployment:
    """Model deployment and serving"""
    
    def __init__(self):
        self.deployed_models = {}
        self.model_metrics = {
            'prediction_counter': Counter('model_predictions_total', 'Total predictions', ['model_name']),
            'prediction_latency': Histogram('model_prediction_duration_seconds', 'Prediction latency', ['model_name']),
            'model_accuracy': Gauge('model_accuracy', 'Model accuracy', ['model_name']),
            'model_drift_score': Gauge('model_drift_score', 'Model drift score', ['model_name'])
        }
        
        # Start Prometheus metrics server
        start_http_server(8000)
    
    def deploy_model(self, model, model_name: str, version: str = "1.0") -> str:
        """Deploy model for serving"""
        deployment_id = f"{model_name}_v{version}_{int(time.time())}"
        
        self.deployed_models[deployment_id] = {
            'model': model,
            'model_name': model_name,
            'version': version,
            'deployed_at': datetime.now(),
            'predictions_count': 0,
            'last_prediction': None
        }
        
        logger.info(f"Model deployed: {deployment_id}")
        return deployment_id
    
    def predict(self, deployment_id: str, data: pd.DataFrame) -> np.ndarray:
        """Make predictions using deployed model"""
        if deployment_id not in self.deployed_models:
            raise ValueError(f"Model not found: {deployment_id}")
        
        model_info = self.deployed_models[deployment_id]
        model = model_info['model']
        
        # Record metrics
        start_time = time.time()
        
        try:
            predictions = model.predict(data)
            
            # Update metrics
            prediction_time = time.time() - start_time
            self.model_metrics['prediction_counter'].labels(model_name=model_info['model_name']).inc()
            self.model_metrics['prediction_latency'].labels(model_name=model_info['model_name']).observe(prediction_time)
            
            # Update deployment info
            model_info['predictions_count'] += len(predictions)
            model_info['last_prediction'] = datetime.now()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed for {deployment_id}: {e}")
            raise
    
    def get_model_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get model deployment status"""
        if deployment_id not in self.deployed_models:
            return {'status': 'not_found'}
        
        model_info = self.deployed_models[deployment_id]
        
        return {
            'deployment_id': deployment_id,
            'model_name': model_info['model_name'],
            'version': model_info['version'],
            'deployed_at': model_info['deployed_at'],
            'predictions_count': model_info['predictions_count'],
            'last_prediction': model_info['last_prediction'],
            'status': 'active'
        }
    
    def list_deployed_models(self) -> List[Dict[str, Any]]:
        """List all deployed models"""
        return [
            self.get_model_status(deployment_id)
            for deployment_id in self.deployed_models.keys()
        ]

class MLOpsPipeline:
    """Main MLOps pipeline orchestrator"""
    
    def __init__(self, config_path: str = "mlops_config.yaml"):
        self.config = self._load_config(config_path)
        self.feature_engineering = FeatureEngineeringPipeline()
        self.model_versioning = ModelVersioning()
        self.hyperparameter_optimization = HyperparameterOptimization()
        self.model_explainability = ModelExplainability()
        self.drift_detector = DataDriftDetector()
        self.model_deployment = ModelDeployment()
        
        self.training_queue = queue.Queue()
        self.prediction_queue = queue.Queue()
        self.is_running = False
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def train_model(self, data: pd.DataFrame, target_column: str, 
                   model_type: str = "regression") -> ExperimentResult:
        """Train a new model"""
        logger.info(f"Starting model training for {model_type}")
        
        # Feature engineering
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        X_engineered = self.feature_engineering.create_features(X, target_column)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_engineered, y, test_size=0.2, random_state=42
        )
        
        # Hyperparameter optimization
        if model_type == "regression":
            opt_result = self.hyperparameter_optimization.optimize_random_forest(
                X_train, y_train, X_test, y_test
            )
            model = RandomForestRegressor(random_state=42, **opt_result['best_params'])
        else:
            opt_result = self.hyperparameter_optimization.optimize_classifier(
                X_train, y_train, X_test, y_test
            )
            model = RandomForestClassifier(random_state=42, **opt_result['best_params'])
        
        # Train final model
        start_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Evaluate model
        y_pred = model.predict(X_test)
        
        if model_type == "regression":
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            accuracy = 1 - (mse / np.var(y_test))  # R² score approximation
            precision = recall = f1_score = 0.0  # Not applicable for regression
        else:
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            precision = report['weighted avg']['precision']
            recall = report['weighted avg']['recall']
            f1_score = report['weighted avg']['f1-score']
            mse = rmse = 0.0  # Not applicable for classification
        
        # Create metrics
        metrics = ModelMetrics(
            model_id=secrets.token_hex(8),
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            mse=mse,
            rmse=rmse,
            timestamp=datetime.now(),
            dataset_version="1.0",
            hyperparameters=opt_result['best_params']
        )
        
        # Model explainability
        explanations = self.model_explainability.explain_model(
            model, X_test, X_engineered.columns.tolist()
        )
        
        # Log experiment
        run_id = self.model_versioning.log_experiment(
            model, metrics, X_engineered.columns.tolist(), opt_result['best_params']
        )
        
        # Create experiment result
        result = ExperimentResult(
            experiment_id=run_id,
            model_name=f"{model_type}_model",
            metrics=metrics,
            feature_importance=self.model_explainability.get_feature_importance(
                model, X_engineered.columns.tolist()
            ),
            training_time=training_time,
            prediction_time=0.0,  # Will be measured during deployment
            model_size=sys.getsizeof(model),
            timestamp=datetime.now()
        )
        
        logger.info(f"Model training completed. Run ID: {run_id}")
        return result
    
    def deploy_best_model(self, model_type: str = "regression") -> str:
        """Deploy the best model based on performance"""
        best_model_info = self.model_versioning.get_best_model()
        
        if not best_model_info:
            raise ValueError("No trained models found")
        
        # Load model from MLflow
        model = mlflow.sklearn.load_model(best_model_info['model_uri'])
        
        # Deploy model
        deployment_id = self.model_deployment.deploy_model(
            model, f"{model_type}_model", "1.0"
        )
        
        logger.info(f"Best model deployed: {deployment_id}")
        return deployment_id
    
    def monitor_model_performance(self, deployment_id: str, 
                                new_data: pd.DataFrame) -> Dict[str, Any]:
        """Monitor model performance and detect drift"""
        # Detect data drift
        drift_results = self.drift_detector.detect_drift(new_data)
        
        # Update drift metrics
        self.model_deployment.model_metrics['model_drift_score'].labels(
            model_name=self.model_deployment.deployed_models[deployment_id]['model_name']
        ).set(drift_results['overall_drift_score'])
        
        # Check if retraining is needed
        retrain_needed = drift_results['overall_drift_score'] > 0.2
        
        return {
            'drift_results': drift_results,
            'retrain_needed': retrain_needed,
            'monitoring_timestamp': datetime.now()
        }
    
    def start_continuous_learning(self):
        """Start continuous learning pipeline"""
        self.is_running = True
        
        def training_worker():
            while self.is_running:
                try:
                    # Get training request from queue
                    training_request = self.training_queue.get(timeout=1.0)
                    
                    # Process training request
                    result = self.train_model(
                        training_request['data'],
                        training_request['target_column'],
                        training_request.get('model_type', 'regression')
                    )
                    
                    logger.info(f"Continuous learning completed: {result.experiment_id}")
                    self.training_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Continuous learning error: {e}")
        
        # Start training worker thread
        training_thread = threading.Thread(target=training_worker, daemon=True)
        training_thread.start()
        
        logger.info("Continuous learning pipeline started")
    
    def stop_continuous_learning(self):
        """Stop continuous learning pipeline"""
        self.is_running = False
        logger.info("Continuous learning pipeline stopped")

# Example usage and testing
if __name__ == "__main__":
    # Create MLOps pipeline
    mlops_pipeline = MLOpsPipeline()
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=n_samples, freq='H'),
        'inventory_level': np.random.normal(100, 20, n_samples),
        'demand': np.random.poisson(50, n_samples),
        'supplier_rating': np.random.uniform(1, 5, n_samples),
        'delivery_time': np.random.exponential(5, n_samples),
        'price': np.random.normal(100, 10, n_samples),
        'cost': np.random.normal(80, 8, n_samples),
        'season': np.random.choice(['spring', 'summer', 'fall', 'winter'], n_samples)
    })
    
    # Add target variable
    data['target'] = data['demand'] * data['price'] - data['cost'] * data['inventory_level']
    
    # Set reference data for drift detection
    mlops_pipeline.drift_detector.set_reference_data(data.head(800))
    
    # Train model
    result = mlops_pipeline.train_model(data, 'target', 'regression')
    print(f"Training completed: {result.experiment_id}")
    
    # Deploy best model
    deployment_id = mlops_pipeline.deploy_best_model('regression')
    print(f"Model deployed: {deployment_id}")
    
    # Test prediction
    test_data = data.drop(columns=['target']).head(10)
    predictions = mlops_pipeline.model_deployment.predict(deployment_id, test_data)
    print(f"Predictions: {predictions}")
    
    # Monitor performance
    monitoring_result = mlops_pipeline.monitor_model_performance(deployment_id, data.tail(200))
    print(f"Drift score: {monitoring_result['drift_results']['overall_drift_score']}")
    
    # Start continuous learning
    mlops_pipeline.start_continuous_learning()
    
    # Add training request to queue
    mlops_pipeline.training_queue.put({
        'data': data,
        'target_column': 'target',
        'model_type': 'regression'
    })
    
    # Wait for processing
    time.sleep(5)
    
    # Stop continuous learning
    mlops_pipeline.stop_continuous_learning()
