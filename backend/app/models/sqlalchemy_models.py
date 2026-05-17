import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Boolean,
    ForeignKey, JSON, Integer, Enum as SAEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import (
    ThreatType, RiskLevel, Action, ModelProvider,
    AuditEventType, PIIEntityType, RequestDirection
)


def generate_uuid():
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    settings = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    policies = relationship("Policy", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="member")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    key_hash = Column(String(512), nullable=False)
    key_prefix = Column(String(8), nullable=False)
    name = Column(String(255))
    permissions = Column(JSONB, default=list)
    rate_limit_multiplier = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="api_keys")

    __table_args__ = (
        Index("idx_api_keys_org", "organization_id"),
    )


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    policy_type = Column(String(50), default="custom")
    rules = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    priority = Column(Integer, default=0)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="policies")

    __table_args__ = (
        Index("idx_policies_org", "organization_id"),
    )


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=True)
    trace_id = Column(String(64), nullable=False)
    direction = Column(SAEnum(RequestDirection), nullable=False)
    model = Column(String(255))
    provider = Column(SAEnum(ModelProvider), nullable=True)
    prompt_preview = Column(Text)
    response_preview = Column(Text)
    prompt_tokens = Column(Integer, default=0)
    response_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float)
    cost_usd = Column(Float, default=0.0)
    action_taken = Column(SAEnum(Action), default=Action.ALLOW)
    risk_score = Column(Float, default=0.0)
    threat_types = Column(JSONB, default=list)
    is_blocked = Column(Boolean, default=False)
    is_sanitized = Column(Boolean, default=False)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")

    __table_args__ = (
        Index("idx_request_logs_org", "organization_id"),
        Index("idx_request_logs_trace", "trace_id"),
        Index("idx_request_logs_created", "created_at"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    event_type = Column(SAEnum(AuditEventType), nullable=False)
    actor_id = Column(String(255))
    actor_type = Column(String(50))
    resource_type = Column(String(50))
    resource_id = Column(String(255))
    action = Column(String(100))
    details = Column(JSONB, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    trace_id = Column(String(64))
    severity = Column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_logs_org", "organization_id"),
        Index("idx_audit_logs_event", "event_type"),
        Index("idx_audit_logs_created", "created_at"),
    )


class ThreatEvent(Base):
    __tablename__ = "threat_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    request_log_id = Column(String, ForeignKey("request_logs.id"), nullable=True)
    threat_type = Column(SAEnum(ThreatType), nullable=False)
    risk_level = Column(SAEnum(RiskLevel), nullable=False)
    score = Column(Float, nullable=False)
    detector_name = Column(String(100))
    matched_pattern = Column(Text)
    input_preview = Column(Text)
    details = Column(JSONB, default=dict)
    action_taken = Column(SAEnum(Action))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_threat_events_org", "organization_id"),
        Index("idx_threat_events_type", "threat_type"),
        Index("idx_threat_events_created", "created_at"),
    )


class PIIEvent(Base):
    __tablename__ = "pii_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    request_log_id = Column(String, ForeignKey("request_logs.id"), nullable=True)
    entity_type = Column(SAEnum(PIIEntityType), nullable=False)
    risk_level = Column(SAEnum(RiskLevel), nullable=False)
    score = Column(Float)
    detected_text_preview = Column(String(255))
    field_context = Column(String(100))
    was_redacted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pii_events_org", "organization_id"),
    )


class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    labels = Column(JSONB, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_metrics_snapshot_org", "organization_id"),
        Index("idx_metrics_snapshot_name", "metric_name"),
        Index("idx_metrics_snapshot_ts", "timestamp"),
    )
