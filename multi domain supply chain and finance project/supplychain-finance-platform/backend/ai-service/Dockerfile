# Use OpenJDK 17 as base image
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Copy the JAR file (assuming it will be built)
COPY target/ai-service-1.0.0.jar app.jar

# Install Python and required dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python ML models and dependencies
COPY ../ai-ml /app/ai-ml

# Install Python dependencies
RUN pip3 install pandas numpy scikit-learn joblib xgboost tensorflow torch

# Expose port
EXPOSE 8082

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]