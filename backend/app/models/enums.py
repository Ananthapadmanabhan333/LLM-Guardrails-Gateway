from enum import Enum


class ThreatType(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    PII_LEAKAGE = "pii_leakage"
    TOXICITY = "toxicity"
    ADVERSARIAL = "adversarial"
    POLICY_VIOLATION = "policy_violation"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class Action(str, Enum):
    ALLOW = "allow"
    SANITIZE = "sanitize"
    BLOCK = "block"
    ESCALATE = "escalate"
    HUMAN_REVIEW = "human_review"


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"


class RequestDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class AuditEventType(str, Enum):
    REQUEST_RECEIVED = "request_received"
    REQUEST_ALLOWED = "request_allowed"
    REQUEST_BLOCKED = "request_blocked"
    REQUEST_SANITIZED = "request_sanitized"
    REQUEST_ESCALATED = "request_escalated"
    RESPONSE_SENT = "response_sent"
    RESPONSE_BLOCKED = "response_blocked"
    RESPONSE_SANITIZED = "response_sanitized"
    POLICY_VIOLATION = "policy_violation"
    THREAT_DETECTED = "threat_detected"
    AUTH_FAILURE = "auth_failure"
    RATE_LIMIT_HIT = "rate_limit_hit"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    POLICY_CREATED = "policy_created"
    POLICY_UPDATED = "policy_updated"
    CONFIG_CHANGED = "config_changed"


class PIIEntityType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    AADHAAR = "aadhaar"
    API_KEY = "api_key"
    PASSWORD = "password"
    SECRET = "secret"
    ACCESS_TOKEN = "access_token"
    IP_ADDRESS = "ip_address"
    LOCATION = "location"
    PERSON_NAME = "person_name"
    BANK_ACCOUNT = "bank_account"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    CUSTOM = "custom"
