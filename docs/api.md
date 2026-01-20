# API Documentation

## Base URL
`/api/v1`

## Endpoints

### 1. Chat Query
Submit a natural language question and receive a streaming response or structured answer.

- **URL**: `/chat/query`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Request Body**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What was the peak CPU usage for the checkout pod last hour?"
    }
  ],
  "context_filters": {
    "namespace": "default",
    "cluster": "production-us-east-1"
  }
}
```

**Response (Streamed)**
Server-Sent Events (SSE) or chunked JSON transfer depending on final implementation choice. 
Each chunk contains a delta of the text response.

**Response (Structured - Optional mode)**
```json
{
  "response": "The peak CPU usage for checkout-pod-123 was 1.2 cores at 14:30.",
  "metrics_used": [
    {
      "metric_name": "container_cpu_usage_seconds_total",
      "value": 1.2,
      "timestamp": "2023-10-27T14:30:00Z"
    }
  ]
}
```

### 2. List Available Metrics
Helper endpoint to see what metric types are supported for context.

- **URL**: `/metrics/available`
- **Method**: `GET`

**Response**
```json
{
  "cpu": ["usage", "throttling"],
  "memory": ["working_set", "rss"],
  "network": ["transmit_bytes", "receive_bytes"]
}
```

### 3. Health Check
Liveness probe for Kubernetes.

- **URL**: `/health`
- **Method**: `GET`

**Response**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "prometheus": "connected",
    "llm": "connected"
  }
}
```

## Error Handling

Standard HTTP status codes are used:
- `400 Bad Request`: Invalid input format.
- `401 Unauthorized`: Missing or invalid API token.
- `500 Internal Server Error`: Backend, Prometheus, or LLM failure.

All errors return a standard error object:
```json
{
  "error": {
    "code": "PROMETHEUS_TIMEOUT",
    "message": "Failed to fetch metrics within the timeout period.",
    "details": "Connection refused to prometheus-service:9090"
  }
}
```
