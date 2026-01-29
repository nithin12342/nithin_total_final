FROM openjdk:11-jdk-slim

WORKDIR /app

# Copy maven executable and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Build all dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source files
COPY src src

# Build application
RUN ./mvnw package -DskipTests

# Run stage
FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=0 /app/target/*.jar app.jar

# Add wait-for-it script to wait for dependent services
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
