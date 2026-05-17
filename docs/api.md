# API Documentation

## Base URL

Development: `http://localhost:8000`
Production: `https://api.guardrails.example.com`

## Authentication

Use either:
- **JWT Token**: `Authorization: Bearer <token>`
- **API Key**: `X-API-Key: <api_key>`

## Endpoints

### Gateway

#### POST /gateway/chat
Send a chat completion request through the guardrails pipeline.

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is AI?"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048,
  "stream": false,
  "metadata": {"session_id": "abc123"},
  "policies": ["custom_policy"]
}
```

#### POST /gateway/stream
Streaming chat completion (same body, stream: true).

### Security

#### POST /security/analyze
Run full security analysis on a prompt.

```json
{
  "text": "Ignore previous instructions...",
  "messages": [{"role": "user", "content": "..."}]
}
```

#### GET /security/analyze/prompt?prompt=<text>
Quick analysis via query parameter.

### Policies

| Method | Path | Description |
|--------|------|-------------|
| GET | /policies/ | List all policies |
| POST | /policies/ | Create a policy |
| DELETE | /policies/{name} | Delete a policy |
| POST | /policies/load/yaml | Load YAML policies |
| POST | /policies/load/json | Load JSON policies |
| GET | /policies/active | List active policies |

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /admin/organizations | List organizations |
| POST | /admin/organizations | Create organization |
| POST | /admin/api-keys | Create API key |
| DELETE | /admin/api-keys/{id} | Revoke API key |

### Audit

| Method | Path | Description |
|--------|------|-------------|
| GET | /audit/logs | Get audit logs |
| GET | /audit/dashboard | Dashboard stats |
| GET | /audit/requests | Request history |

### Threats

| Method | Path | Description |
|--------|------|-------------|
| GET | /threats/ | List threat events |
| GET | /threats/stats | Threat statistics |
| GET | /threats/pii | PII detection events |

### Providers

| Method | Path | Description |
|--------|------|-------------|
| GET | /providers/ | List LLM providers |
| GET | /providers/models | List models |
| GET | /providers/costs | Cost information |

### Metrics

| Method | Path | Description |
|--------|------|-------------|
| GET | /metrics/ | Prometheus metrics |
| GET | /metrics/summary | Summary statistics |
| GET | /metrics/latency?hours=24 | Latency percentiles |
| GET | /metrics/requests?hours=24 | Request time series |
| GET | /metrics/threats?hours=24 | Threat time series |

## Error Responses

```json
{
  "error": "request_blocked",
  "message": "Request was blocked by security guardrails",
  "threat_score": 0.95,
  "risk_level": "critical",
  "threats": [{"type": "prompt_injection", "score": 0.95}],
  "trace_id": "abc-123-def"
}
```

## Rate Limiting

- Default: 100 requests per 60 seconds per API key
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Response: `429 Too Many Requests`

## Tracing

All responses include:
- `X-Trace-ID`: Unique trace identifier
- `X-Request-Duration-Ms`: Request processing time
