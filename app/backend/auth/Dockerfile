# ============================
# BUILD STAGE
# ============================
FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

ARG SKIP_TESTS=true

RUN mvn -B $( [ "$SKIP_TESTS" = "true" ] && echo "-DskipTests" ) clean package


# ============================
# RUNTIME STAGE (PRODUCTION)
# ============================
FROM eclipse-temurin:17-jre-alpine AS runtime

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080
ENV SPRING_PROFILES_ACTIVE=docker

ENTRYPOINT ["java", "-jar", "/app/app.jar"]


# ============================
# DEVELOPMENT STAGE (OPTIONAL)
# ============================
FROM eclipse-temurin:17-jdk-alpine AS dev

WORKDIR /app

COPY . .

RUN ./mvnw -q dependency:resolve

EXPOSE 8080

CMD ["./mvnw", "spring-boot:run"]