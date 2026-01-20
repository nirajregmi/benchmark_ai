# System Architecture

## Overview
The AI Observability Platform is a specialized assistant designed to bridge the gap between complex infrastructure metrics (Prometheus) and natural language queries. It leverages a Large Language Model (LLama-3.3-70B) to interpret user intent, fetch relevant data, and explain the results in plain English.

## System Components

### 1. Frontend (React + Vite)
- **Role**: User Interface for chat-based interaction.
- **Key Responsibilities**:
  - Render chat history with distinct visualization for User vs Assistant.
  - Stream real-time responses from the backend.
  - visualize key metric data points (if structured data is returned).
- **State Management**: React Context or lightweight store (Zustand/Redux Toolkit) for conversation history.

### 2. Backend (FastAPI)
- **Role**: Central orchestrator and API gateway.
- **Key Responsibilities**:
  - **API Layer**: Exposes REST endpoints for the frontend.
  - **Intelligence Pipeline**:
    1. **Intent Detection**: Analyzes user query to determine what metrics are needed (e.g., "CPU", "Memory", "Traffic") and the time range.
    2. **Prometheus Gateway**: Generates PromQL and executes queries against the OpenShift-hosted Prometheus.
    3. **Data Aggregation**: Normalizes raw time-series data into a context-efficient summary (Min/Max/Avg/Trend).
    4. **LLM Integration**: Constructs a prompt with the user query + aggregated data and streams the LLM's explanation.
  - **Security**: Validates requests and manages environment-specific configurations.

### 3. Prometheus (OpenShift)
- **Role**: Metric storage and query engine.
- **Integration**: The backend communicates via the Prometheus HTTP API (`/api/v1/query_range`).

### 4. LLM Engine (LLaMA-3.3-70B)
- **Role**: Reasoning and Natural Language Generation.
- **Constraint**: **NEVER** calls the metric database directly. It only analyzes the data provided in its context window by the backend.

## Data Flow

1. **User Request**: "Why did the payment-service crash yesterday?"
2. **Backend (Intent)**: Determines `service="payment-service"`, `metric=["memory_usage", "error_rate"]`, `time_range="yesterday"`.
3. **Backend (Prometheus)**: 
   - Generates PromQL: `sum(rate(container_cpu_usage_seconds_total{pod=~"payment-service.*"}[5m]))`
   - Fetches data.
4. **Backend (Aggregation)**: Calculates "Peak CPU: 85%", "Avg Memory: 400MB", "Error Spike: 22:00".
5. **Backend (LLM)**: Sends prompt including the stats above.
6. **LLM**: Generates "The payment service showed a memory spike at 22:00 which correlates with the crash..."
7. **Frontend**: Displays streaming text to the user.

## Security & Scalability
- **Stateless Backend**: The API is stateless, allowing horizontal scaling on Kubernetes.
- **Read-Only Access**: The system only reads metrics; it cannot modify infrastructure state.
- **Input Sanitization**: All user inputs are sanitized before being processed by the LLM or used in PromQL generation.
