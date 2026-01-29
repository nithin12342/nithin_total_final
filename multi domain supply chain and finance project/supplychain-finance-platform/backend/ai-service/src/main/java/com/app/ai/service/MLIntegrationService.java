package com.app.ai.service;

import com.app.ai.model.DemandForecast;
import com.app.ai.model.FraudDetection;
import com.app.ai.model.RiskAssessment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class MLIntegrationService {
    
    private static final Logger logger = LoggerFactory.getLogger(MLIntegrationService.class);
    
    // Method to call Python demand forecasting model
    public DemandForecast predictDemand(String productId, String period) {
        logger.info("Predicting demand for product: {} with period: {}", productId, period);
        
        try {
            // Call the Python ML API
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python", 
                "../ai-ml/src/ml_api.py", 
                "predict_demand",
                "--product_id", productId,
                "--period", period
            );
            
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                // Parse the JSON output to create DemandForecast object
                String jsonOutput = output.toString().trim();
                // In a real implementation, we would parse the JSON
                // For now, we'll simulate the parsing
                
                // Simulated values from the Python script
                Integer predictedDemand = 100; // Would come from JSON parsing
                Double confidence = 0.85; // Would come from JSON parsing
                
                DemandForecast forecast = new DemandForecast(
                    productId, 
                    predictedDemand, 
                    confidence, 
                    LocalDateTime.now().plusDays(7), 
                    period
                );
                
                logger.info("Demand prediction successful for product: {}", productId);
                return forecast;
            } else {
                // Read error output
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder errorOutput = new StringBuilder();
                String errorLine;
                while ((errorLine = errorReader.readLine()) != null) {
                    errorOutput.append(errorLine).append("\n");
                }
                logger.error("Python script execution failed with exit code: {} and error: {}", exitCode, errorOutput.toString());
                throw new RuntimeException("Failed to execute demand forecasting model");
            }
        } catch (Exception e) {
            logger.error("Error predicting demand for product: {}", productId, e);
            throw new RuntimeException("Error in demand prediction", e);
        }
    }
    
    // Method to call Python fraud detection model
    public FraudDetection detectFraud(String transactionId, Double amount, String supplierId) {
        logger.info("Detecting fraud for transaction: {} with amount: {}", transactionId, amount);
        
        try {
            // Call the Python ML API
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python", 
                "../ai-ml/src/ml_api.py", 
                "detect_fraud",
                "--transaction_id", transactionId,
                "--amount", amount.toString(),
                "--supplier_id", supplierId
            );
            
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                // Parse the JSON output to create FraudDetection object
                String jsonOutput = output.toString().trim();
                // In a real implementation, we would parse the JSON
                // For now, we'll simulate the parsing
                
                // Simulated values from the Python script
                Double riskScore = 0.75; // Would come from JSON parsing
                Boolean isFraud = riskScore > 0.8; // Would come from JSON parsing
                Double confidence = 0.92; // Would come from JSON parsing
                
                FraudDetection fraudDetection = new FraudDetection(
                    transactionId,
                    riskScore,
                    isFraud,
                    LocalDateTime.now(),
                    "v1.0",
                    confidence
                );
                
                logger.info("Fraud detection successful for transaction: {}", transactionId);
                return fraudDetection;
            } else {
                // Read error output
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder errorOutput = new StringBuilder();
                String errorLine;
                while ((errorLine = errorReader.readLine()) != null) {
                    errorOutput.append(errorLine).append("\n");
                }
                logger.error("Python script execution failed with exit code: {} and error: {}", exitCode, errorOutput.toString());
                throw new RuntimeException("Failed to execute fraud detection model");
            }
        } catch (Exception e) {
            logger.error("Error detecting fraud for transaction: {}", transactionId, e);
            throw new RuntimeException("Error in fraud detection", e);
        }
    }
    
    // Method to call Python risk assessment model
    public RiskAssessment assessRisk(String supplierId) {
        logger.info("Assessing risk for supplier: {}", supplierId);
        
        try {
            // Call the Python ML API
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python", 
                "../ai-ml/src/ml_api.py", 
                "assess_risk",
                "--supplier_id", supplierId
            );
            
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                // Parse the JSON output to create RiskAssessment object
                String jsonOutput = output.toString().trim();
                // In a real implementation, we would parse the JSON
                // For now, we'll simulate the parsing
                
                // Simulated values from the Python script
                Double riskScore = 0.65; // Would come from JSON parsing
                String riskLevel = riskScore > 0.8 ? "HIGH" : (riskScore > 0.5 ? "MEDIUM" : "LOW"); // Would come from JSON parsing
                Double confidence = 0.88; // Would come from JSON parsing
                
                RiskAssessment riskAssessment = new RiskAssessment(
                    supplierId,
                    riskScore,
                    riskLevel,
                    LocalDateTime.now(),
                    "v1.0",
                    confidence
                );
                
                logger.info("Risk assessment successful for supplier: {}", supplierId);
                return riskAssessment;
            } else {
                // Read error output
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder errorOutput = new StringBuilder();
                String errorLine;
                while ((errorLine = errorReader.readLine()) != null) {
                    errorOutput.append(errorLine).append("\n");
                }
                logger.error("Python script execution failed with exit code: {} and error: {}", exitCode, errorOutput.toString());
                throw new RuntimeException("Failed to execute risk assessment model");
            }
        } catch (Exception e) {
            logger.error("Error assessing risk for supplier: {}", supplierId, e);
            throw new RuntimeException("Error in risk assessment", e);
        }
    }
    
    // Method to retrain models
    public boolean retrainModels() {
        logger.info("Retraining AI/ML models");
        
        try {
            // Call the Python ML API
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python", 
                "../ai-ml/src/ml_api.py", 
                "retrain"
            );
            
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                logger.info("ML API output: {}", line);
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                logger.info("Model retraining successful");
                return true;
            } else {
                // Read error output
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder errorOutput = new StringBuilder();
                String errorLine;
                while ((errorLine = errorReader.readLine()) != null) {
                    errorOutput.append(errorLine).append("\n");
                }
                logger.error("Model retraining failed with exit code: {} and error: {}", exitCode, errorOutput.toString());
                return false;
            }
        } catch (Exception e) {
            logger.error("Error retraining models", e);
            return false;
        }
    }
}