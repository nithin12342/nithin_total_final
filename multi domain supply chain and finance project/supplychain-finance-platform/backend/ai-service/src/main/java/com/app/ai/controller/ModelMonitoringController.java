package com.app.ai.controller;

import com.app.ai.service.ModelMonitoringService;
import com.app.supplychain.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai/monitoring")
@Tag(name = "Model Monitoring", description = "Model Monitoring and Performance Tracking")
public class ModelMonitoringController {
    
    @Autowired
    private ModelMonitoringService modelMonitoringService;
    
    @GetMapping("/performance")
    @Operation(summary = "Get model performance metrics", description = "Retrieve current performance metrics for all AI/ML models")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Model performance metrics retrieved successfully", 
            content = @Content(mediaType = "application/json", 
                schema = @Schema(implementation = ApiResponse.class))),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<ModelMonitoringService.ModelPerformanceMetrics>> getModelPerformanceMetrics() {
        try {
            ModelMonitoringService.ModelPerformanceMetrics metrics = modelMonitoringService.getModelPerformanceMetrics();
            return ResponseEntity.ok(new ApiResponse<>(metrics, "Model performance metrics retrieved successfully"));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                .body(new ApiResponse<>(null, "Error retrieving model performance metrics: " + e.getMessage()));
        }
    }
    
    @PostMapping("/retrain")
    @Operation(summary = "Trigger model retraining", description = "Manually trigger retraining of all AI/ML models")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Model retraining initiated successfully", 
            content = @Content(mediaType = "application/json", 
                schema = @Schema(implementation = ApiResponse.class))),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<Boolean>> triggerModelRetraining() {
        try {
            // This will trigger the retraining in the monitoring service
            modelMonitoringService.monitorModelPerformance();
            return ResponseEntity.ok(new ApiResponse<>(true, "Model retraining initiated successfully"));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                .body(new ApiResponse<>(false, "Error initiating model retraining: " + e.getMessage()));
        }
    }
}