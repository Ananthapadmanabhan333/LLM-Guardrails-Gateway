# LLM Guardrails Gateway - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User / Application                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                     │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ Auth/RBAC    │ │ Rate Limiter │ │ Request Interceptor  │  │
│  │ JWT/OAuth2   │ │ Token Bucket │ │ Tracing Middleware    │  │
│  └─────────────┘ └──────────────┘ └──────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Guardrails Engine                          │
│  ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Prompt Inj.     │ │ Jailbreak    │ │ PII Scanner      │  │
│  │ Detection       │ │ Detection    │ │ (Presidio)       │  │
│  ├─────────────────┤ ├──────────────┤ ├──────────────────┤  │
│  │ Toxicity        │ │ Semantic     │ │ Context          │  │
│  │ Analysis        │ │ Firewall     │ │ Analyzer         │  │
│  ├─────────────────┤ ├──────────────┤ ├──────────────────┤  │
│  │ Policy Engine   │ │ Threat       │ │ Prompt           │  │
│  │ (YAML/JSON)     │ │ Scorer       │ │ Validator        │  │
│  └─────────────────┘ └──────────────┘ └──────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM Router                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ ┌──────┐  │
│  │ OpenAI   │ │ Anthropic│ │ Gemini   │ │ Groq │ │Ollama│  │
│  │ GPT-4/4o │ │ Claude 3 │ │ Pro/Flash│ │OSS  │ │Local │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────┘ └──────┘  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Routing: Cost-based / Latency-based / Capability    │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  Output Validation Engine                     │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ JSON Schema │ │ Hallucination│ │ Toxicity Filter     │  │
│  │ Validator   │ │ Detector     │ │                     │  │
│  ├─────────────┤ ├──────────────┤ ├──────────────────────┤  │
│  │ Citation    │ │ Compliance   │ │ Output Policy       │  │
│  │ Checker     │ │ Validator    │ │ Enforcement         │  │
│  └─────────────┘ └──────────────┘ └──────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Observability & Audit Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │OpenTele. │ │Prometheus│ │ Grafana  │ │ LangSmith      │  │
│  │Traces    │ │Metrics   │ │Dashboards│ │ Traces         │  │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├────────────────┤  │
│  │PostgreSQL│ │Audit Logs│ │Threat    │ │ Compliance     │  │
│  │Storage   │ │(Immutable)│ │Analytics │ │ Reports        │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Final Response                            │
└─────────────────────────────────────────────────────────────┘
```

## Threat Detection Pipeline

```
Input Prompt
    │
    ├──→ Regex Pattern Matching (40+ injection patterns)
    ├──→ Jailbreak Pattern Detection (25+ jailbreak patterns)
    ├──→ DAN/Developer Mode Detection
    ├──→ PII Scanning (10+ entity types)
    ├──→ Toxicity Analysis (15+ toxic categories)
    ├──→ Semantic Firewall Analysis
    │       ├── Instruction Hijack Detection
    │       ├── Prompt Leakage Detection
    │       ├── Adversarial Unicode Detection
    │       └── Prompt Mutation Detection
    ├──→ Context Analysis
    ├──→ Policy Engine Evaluation
    └──→ Threat Scoring & Risk Assessment
            │
            ▼
    Action: Allow / Sanitize / Block / Escalate
```

## Data Flow

1. Request arrives at API Gateway
2. Authentication & Rate Limiting
3. Request Interceptor adds tracing
4. Guardrails Engine processes request:
   - Runs all detectors in parallel
   - Evaluates policies
   - Calculates threat score
   - Determines action
5. If blocked: return error + audit log
6. If allowed: route to LLM provider
7. Output validation on response
8. Audit logging + metrics emission
9. Response returned to client

## Security Architecture

- **Defense in Depth**: Multiple detection layers
- **Zero Trust**: Every request is validated
- **Immutable Audit**: All events are logged
- **Least Privilege**: RBAC for all operations
- **Secure by Default**: Strict policies pre-configured
