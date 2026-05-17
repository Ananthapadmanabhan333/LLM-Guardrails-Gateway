"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("settings", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("key_hash", sa.String(512), nullable=False),
        sa.Column("key_prefix", sa.String(8), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("permissions", postgresql.JSONB(), nullable=True),
        sa.Column("rate_limit_multiplier", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "policies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("policy_type", sa.String(50), nullable=True),
        sa.Column("rules", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "request_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("api_key_id", sa.String(), nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("direction", sa.Enum("INBOUND", "OUTBOUND", name="requestdirection"), nullable=False),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("provider", sa.Enum("OPENAI", "ANTHROPIC", "GEMINI", "GROQ", "OLLAMA", name="modelprovider"), nullable=True),
        sa.Column("prompt_preview", sa.Text(), nullable=True),
        sa.Column("response_preview", sa.Text(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("response_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("action_taken", sa.Enum("ALLOW", "SANITIZE", "BLOCK", "ESCALATE", "HUMAN_REVIEW", name="action"), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("threat_types", postgresql.JSONB(), nullable=True),
        sa.Column("is_blocked", sa.Boolean(), nullable=True),
        sa.Column("is_sanitized", sa.Boolean(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.Enum(
            "REQUEST_RECEIVED", "REQUEST_ALLOWED", "REQUEST_BLOCKED",
            "REQUEST_SANITIZED", "REQUEST_ESCALATED", "RESPONSE_SENT",
            "RESPONSE_BLOCKED", "RESPONSE_SANITIZED", "POLICY_VIOLATION",
            "THREAT_DETECTED", "AUTH_FAILURE", "RATE_LIMIT_HIT",
            "API_KEY_CREATED", "API_KEY_REVOKED", "POLICY_CREATED",
            "POLICY_UPDATED", "CONFIG_CHANGED",
            name="auditeventtype"
        ), nullable=False),
        sa.Column("actor_id", sa.String(255), nullable=True),
        sa.Column("actor_type", sa.String(50), nullable=True),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("action", sa.String(100), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=True),
        sa.Column("severity", sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE", name="risklevel"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "threat_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("request_log_id", sa.String(), nullable=True),
        sa.Column("threat_type", sa.Enum(
            "PROMPT_INJECTION", "JAILBREAK", "PII_LEAKAGE",
            "TOXICITY", "ADVERSARIAL", "POLICY_VIOLATION", "UNKNOWN",
            name="threattype"
        ), nullable=False),
        sa.Column("risk_level", sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE", name="risklevel"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("detector_name", sa.String(100), nullable=True),
        sa.Column("matched_pattern", sa.Text(), nullable=True),
        sa.Column("input_preview", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("action_taken", sa.Enum("ALLOW", "SANITIZE", "BLOCK", "ESCALATE", "HUMAN_REVIEW", name="action"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pii_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("request_log_id", sa.String(), nullable=True),
        sa.Column("entity_type", sa.Enum(
            "EMAIL", "PHONE", "CREDIT_CARD", "SSN", "AADHAAR",
            "API_KEY", "PASSWORD", "SECRET", "ACCESS_TOKEN",
            "IP_ADDRESS", "LOCATION", "PERSON_NAME", "BANK_ACCOUNT",
            "PASSPORT", "DRIVERS_LICENSE", "CUSTOM",
            name="piientitytype"
        ), nullable=False),
        sa.Column("risk_level", sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE", name="risklevel"), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("detected_text_preview", sa.String(255), nullable=True),
        sa.Column("field_context", sa.String(100), nullable=True),
        sa.Column("was_redacted", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "metrics_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("metric_name", sa.String(255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("labels", postgresql.JSONB(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_api_keys_org", "api_keys", ["organization_id"])
    op.create_index("idx_policies_org", "policies", ["organization_id"])
    op.create_index("idx_request_logs_org", "request_logs", ["organization_id"])
    op.create_index("idx_request_logs_trace", "request_logs", ["trace_id"])
    op.create_index("idx_request_logs_created", "request_logs", ["created_at"])
    op.create_index("idx_audit_logs_org", "audit_logs", ["organization_id"])
    op.create_index("idx_audit_logs_event", "audit_logs", ["event_type"])
    op.create_index("idx_audit_logs_created", "audit_logs", ["created_at"])
    op.create_index("idx_threat_events_org", "threat_events", ["organization_id"])
    op.create_index("idx_threat_events_type", "threat_events", ["threat_type"])
    op.create_index("idx_threat_events_created", "threat_events", ["created_at"])
    op.create_index("idx_pii_events_org", "pii_events", ["organization_id"])
    op.create_index("idx_metrics_snapshot_org", "metrics_snapshots", ["organization_id"])
    op.create_index("idx_metrics_snapshot_name", "metrics_snapshots", ["metric_name"])
    op.create_index("idx_metrics_snapshot_ts", "metrics_snapshots", ["timestamp"])


def downgrade() -> None:
    op.drop_table("metrics_snapshots")
    op.drop_table("pii_events")
    op.drop_table("threat_events")
    op.drop_table("audit_logs")
    op.drop_table("request_logs")
    op.drop_table("policies")
    op.drop_table("api_keys")
    op.drop_table("users")
    op.drop_table("organizations")
