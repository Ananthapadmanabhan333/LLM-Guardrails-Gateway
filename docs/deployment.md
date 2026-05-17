# Deployment Guide

## Prerequisites

- Docker & Docker Compose (v3.8+)
- Kubernetes cluster (for K8s deployment)
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

## Quick Start (Docker Compose)

```bash
# 1. Clone the repository
git clone <repo-url>
cd llm-guardrails-gateway

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit .env with your API keys

# 3. Start all services
docker-compose -f infra/docker-compose.yml up -d

# 4. Verify deployment
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0","service":"LLM Guardrails Gateway"}

# 5. Access dashboard
open http://localhost:3000
```

## Kubernetes Deployment

```bash
# 1. Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# 2. Configure secrets
kubectl apply -f infra/k8s/secrets.yaml
# Edit secrets with your values

# 3. Apply ConfigMap
kubectl apply -f infra/k8s/configmap.yaml

# 4. Deploy infrastructure
kubectl apply -f infra/k8s/postgres-deployment.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml

# 5. Deploy applications
kubectl apply -f infra/k8s/backend-deployment.yaml
kubectl apply -f infra/k8s/frontend-deployment.yaml

# 6. Configure ingress
kubectl apply -f infra/k8s/ingress.yaml

# 7. Verify deployment
kubectl get pods -n llm-guardrails
kubectl get svc -n llm-guardrails
```

## Manual Setup (Development)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Opens at http://localhost:3000
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| REDIS_URL | Redis connection string | Yes |
| JWT_SECRET_KEY | JWT signing secret | Yes |
| OPENAI_API_KEY | OpenAI API key | No |
| ANTHROPIC_API_KEY | Anthropic API key | No |
| GEMINI_API_KEY | Google Gemini API key | No |
| GROQ_API_KEY | Groq API key | No |
| OLLAMA_BASE_URL | Ollama server URL | No |

## Scaling

- Backend: Horizontally scalable (stateless)
- Database: Use read replicas for audit queries
- Redis: Cluster mode for high availability
- Kafka: Partition-based scaling for event streaming

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- OpenTelemetry: gRPC port 4317, HTTP port 4318
- Backend metrics: http://localhost:8000/metrics

## Production Checklist

- [ ] Change all default secrets and passwords
- [ ] Configure HTTPS/TLS certificates
- [ ] Set up database backups
- [ ] Configure monitoring alerts
- [ ] Set up log aggregation
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Set up CI/CD pipeline
- [ ] Configure autoscaling
- [ ] Set up disaster recovery
