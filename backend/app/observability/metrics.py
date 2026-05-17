from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Dict, Any, Optional
import time


request_counter = Counter(
    "llm_gateway_requests_total",
    "Total LLM gateway requests",
    ["provider", "model", "action", "organization"],
)

blocked_requests_counter = Counter(
    "llm_gateway_blocked_requests_total",
    "Total blocked requests",
    ["threat_type", "organization"],
)

request_latency_histogram = Histogram(
    "llm_gateway_request_duration_ms",
    "Request latency in milliseconds",
    ["provider", "model"],
    buckets=[50, 100, 200, 500, 1000, 2000, 5000, 10000, 30000],
)

token_counter = Counter(
    "llm_gateway_tokens_total",
    "Total tokens used",
    ["provider", "model", "type"],
)

cost_counter = Counter(
    "llm_gateway_cost_total",
    "Total cost in USD",
    ["provider", "model", "organization"],
)

threat_counter = Counter(
    "llm_gateway_threats_total",
    "Total threats detected",
    ["threat_type", "severity", "organization"],
)

active_connections = Gauge(
    "llm_gateway_active_connections",
    "Number of active connections",
)

pii_detection_counter = Counter(
    "llm_gateway_pii_detections_total",
    "PII detections",
    ["entity_type", "organization"],
)

policy_violation_counter = Counter(
    "llm_gateway_policy_violations_total",
    "Policy violations",
    ["policy_name", "organization"],
)

rate_limit_hits = Counter(
    "llm_gateway_rate_limit_hits_total",
    "Rate limit hits",
    ["organization"],
)


def record_request(provider: str, model: str, action: str, organization: str = "default"):
    request_counter.labels(provider=provider, model=model, action=action, organization=organization).inc()


def record_blocked(threat_type: str, organization: str = "default"):
    blocked_requests_counter.labels(threat_type=threat_type, organization=organization).inc()


def record_latency(provider: str, model: str, duration_ms: float):
    request_latency_histogram.labels(provider=provider, model=model).observe(duration_ms)


def record_tokens(provider: str, model: str, token_type: str, count: int):
    token_counter.labels(provider=provider, model=model, type=token_type).inc(count)


def record_cost(provider: str, model: str, cost: float, organization: str = "default"):
    cost_counter.labels(provider=provider, model=model, organization=organization).inc(cost)


def record_threat(threat_type: str, severity: str, organization: str = "default"):
    threat_counter.labels(threat_type=threat_type, severity=severity, organization=organization).inc()


def record_pii(entity_type: str, organization: str = "default"):
    pii_detection_counter.labels(entity_type=entity_type, organization=organization).inc()


def record_policy_violation(policy_name: str, organization: str = "default"):
    policy_violation_counter.labels(policy_name=policy_name, organization=organization).inc()


def set_active_connections(count: int):
    active_connections.set(count)


def get_metrics():
    return generate_latest(REGISTRY)
