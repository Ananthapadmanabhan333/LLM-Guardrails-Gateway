from pydantic_settings import BaseSettings
from typing import List, Dict, Any, Optional
from enum import Enum
import os


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    app_name: str = "LLM Guardrails Gateway"
    version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/llm_guardrails"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    jwt_secret_key: str = "super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    api_key_header: str = "X-API-Key"

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    max_prompt_length: int = 32000
    max_response_length: int = 32000

    threat_score_threshold_block: float = 0.85
    threat_score_threshold_sanitize: float = 0.60
    threat_score_threshold_escalate: float = 0.40

    enable_otel_tracing: bool = True
    otel_service_name: str = "llm-guardrails-gateway"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    log_level: str = "INFO"
    log_format: str = "json"

    allowed_models: List[str] = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
        "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
        "gemini-1.5-pro", "gemini-1.5-flash",
        "mixtral-8x7b", "llama3-70b",
        "ollama/llama3", "ollama/mistral"
    ]

    default_model: str = "gpt-4o-mini"
    fallback_model: str = "claude-3-haiku"

    presidio_analyzer_url: str = "http://localhost:5001"
    presidio_anonymizer_url: str = "http://localhost:5002"

    enable_streaming: bool = True
    enable_websocket: bool = True
    enable_cors: bool = True
    cors_origins: List[str] = ["http://localhost:3000"]

    sentry_dsn: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "llm-guardrails-gateway"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
