from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import (
    ThreatType, RiskLevel, Action, ModelProvider,
    AuditEventType, PIIEntityType, RequestDirection
)


class ChatRequest(BaseModel):
    model: str = Field(default="gpt-4o-mini")
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None
    policies: Optional[List[str]] = None


class ChatResponse(BaseModel):
    id: str
    model: str
    provider: ModelProvider
    content: str
    finish_reason: str
    usage: Dict[str, int]
    latency_ms: float
    cost_usd: float
    guardrails: Optional[Dict[str, Any]] = None


class StreamChunk(BaseModel):
    id: str
    model: str
    content: str
    finish_reason: Optional[str] = None


class GuardrailsResult(BaseModel):
    threat_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.SAFE
    action: Action = Action.ALLOW
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    pii_found: List[Dict[str, Any]] = Field(default_factory=list)
    policy_violations: List[Dict[str, Any]] = Field(default_factory=list)
    sanitized_prompt: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class PolicyRule(BaseModel):
    name: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class PolicyDefinition(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    policy_type: str = "custom"
    rules: List[PolicyRule]
    is_active: bool = True
    priority: int = 0
    version: int = 1


class ThreatAnalysis(BaseModel):
    threat_type: ThreatType
    risk_level: RiskLevel
    score: float
    detector_name: str
    matched_pattern: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    threats: List[ThreatAnalysis]
    overall_risk_score: float
    overall_risk_level: RiskLevel
    recommended_action: Action
    pii_entities: List[Dict[str, Any]] = Field(default_factory=list)


class AuditEntry(BaseModel):
    id: str
    organization_id: str
    event_type: AuditEventType
    actor_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    trace_id: Optional[str] = None
    severity: RiskLevel
    created_at: datetime


class ProviderConfig(BaseModel):
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    is_active: bool = True
    cost_per_token: float = 0.0
    latency_p50_ms: float = 0.0


class ThreatDashboard(BaseModel):
    total_threats: int = 0
    blocked_requests: int = 0
    sanitized_requests: int = 0
    critical_threats: int = 0
    high_threats: int = 0
    medium_threats: int = 0
    low_threats: int = 0
    threats_by_type: Dict[str, int] = Field(default_factory=dict)
    threats_over_time: List[Dict[str, Any]] = Field(default_factory=list)
    top_attack_patterns: List[Dict[str, Any]] = Field(default_factory=list)


class MetricsResponse(BaseModel):
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    blocked_percentage: float = 0.0
    threat_percentage: float = 0.0
    requests_per_minute: float = 0.0
    active_organizations: int = 0


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    error: str
    code: str
    detail: Optional[str] = None
    trace_id: Optional[str] = None
