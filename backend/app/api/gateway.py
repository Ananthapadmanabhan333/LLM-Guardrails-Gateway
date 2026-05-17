import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.schemas import ChatRequest, ChatResponse, GuardrailsResult
from app.models.enums import Action, AuditEventType, RiskLevel
from app.engine.guardrails import guardrails_engine
from app.routing.router import llm_router
from app.routing.cost_optimizer import cost_optimizer
from app.output.validator import output_validator
from app.output.hallucination_detector import hallucination_detector
from app.output.compliance import compliance_validator
from app.middleware.auth import authenticate_request
from app.middleware.rate_limiter import rate_limiter
from app.services.audit_service import audit_service
from app.observability import metrics as metrics_module
from app.observability.logging import logger

router = APIRouter(prefix="/gateway", tags=["Gateway"])


@router.post("/chat")
async def chat_completion(
    request: Request,
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id, user_id, role = auth

    await rate_limiter.check_rate_limit(request)
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))

    start_time = datetime.utcnow()

    guardrails_result = await guardrails_engine.process_request(
        messages=chat_request.messages,
        model=chat_request.model,
        organization_id=organization_id,
        policies=chat_request.policies,
    )

    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    if guardrails_result.action in (Action.BLOCK, Action.ESCALATE):
        metrics_module.record_request(
            provider="guardrails",
            model=chat_request.model,
            action=guardrails_result.action.value,
            organization=organization_id,
        )
        metrics_module.record_blocked(
            threat_type=",".join(t.get("type", "unknown") for t in guardrails_result.threats),
            organization=organization_id,
        )

        for threat in guardrails_result.threats:
            metrics_module.record_threat(
                threat_type=threat.get("type", "unknown"),
                severity=guardrails_result.risk_level.value,
                organization=organization_id,
            )

        background_tasks.add_task(
            audit_service.log_event,
            session, organization_id,
            AuditEventType.REQUEST_BLOCKED,
            actor_id=user_id,
            resource_type="chat",
            details={
                "model": chat_request.model,
                "threat_score": guardrails_result.threat_score,
                "risk_level": guardrails_result.risk_level.value,
                "threats": guardrails_result.threats,
                "trace_id": trace_id,
            },
            trace_id=trace_id,
            severity=guardrails_result.risk_level,
        )

        raise HTTPException(
            status_code=403,
            detail={
                "error": "request_blocked",
                "message": "Request was blocked by security guardrails",
                "threat_score": guardrails_result.threat_score,
                "risk_level": guardrails_result.risk_level.value,
                "threats": guardrails_result.threats,
                "trace_id": trace_id,
            },
        )

    provider_result = await llm_router.route(chat_request, guardrails_result)

    if "error" in provider_result:
        raise HTTPException(status_code=502, detail=provider_result)

    output_validation = output_validator.validate(provider_result.get("content", ""))

    if output_validation["action"] == "block":
        background_tasks.add_task(
            audit_service.log_event,
            session, organization_id,
            AuditEventType.RESPONSE_BLOCKED,
            actor_id=user_id,
            resource_type="chat",
            details={
                "model": chat_request.model,
                "issues": output_validation["issues"],
                "trace_id": trace_id,
            },
            trace_id=trace_id,
            severity=RiskLevel.HIGH,
        )
        raise HTTPException(
            status_code=422,
            detail={
                "error": "response_blocked",
                "message": "Model output was blocked by output guardrails",
                "issues": output_validation["issues"],
                "trace_id": trace_id,
            },
        )

    hallucination_check = hallucination_detector.analyze(provider_result.get("content", ""))
    compliance_check = compliance_validator.validate(provider_result.get("content", ""))

    total_tokens = provider_result.get("usage", {}).get("total_tokens", 0)
    estimated_cost = cost_optimizer.estimate_cost(
        chat_request.model,
        provider_result.get("usage", {}).get("prompt_tokens", 0),
        provider_result.get("usage", {}).get("completion_tokens", 0),
    )

    metrics_module.record_request(
        provider=provider_result.get("provider", "unknown"),
        model=chat_request.model,
        action="allow",
        organization=organization_id,
    )
    metrics_module.record_tokens(
        provider=provider_result.get("provider", "unknown"),
        model=chat_request.model,
        token_type="total",
        count=total_tokens,
    )
    if estimated_cost > 0:
        metrics_module.record_cost(
            provider=provider_result.get("provider", "unknown"),
            model=chat_request.model,
            cost=estimated_cost,
            organization=organization_id,
        )
    if guardrails_result.pii_found:
        for pii in guardrails_result.pii_found:
            metrics_module.record_pii(
                entity_type=pii.get("entity_type", "unknown"),
                organization=organization_id,
            )

    background_tasks.add_task(
        audit_service.log_event,
        session, organization_id,
        AuditEventType.RESPONSE_SENT,
        actor_id=user_id,
        resource_type="chat",
        details={
            "model": chat_request.model,
            "provider": provider_result.get("provider"),
            "tokens": total_tokens,
            "cost": estimated_cost,
            "latency_ms": duration_ms,
            "guardrails": guardrails_result.dict() if hasattr(guardrails_result, "dict") else guardrails_result.model_dump(),
            "output_validation": output_validation,
            "hallucination_check": hallucination_check,
            "compliance_check": compliance_check,
            "trace_id": trace_id,
        },
        trace_id=trace_id,
        severity=guardrails_result.risk_level,
    )

    return ChatResponse(
        id=str(uuid.uuid4()),
        model=chat_request.model,
        provider=provider_result.get("provider", "unknown"),
        content=provider_result.get("content", ""),
        finish_reason=provider_result.get("finish_reason", "stop"),
        usage=provider_result.get("usage", {}),
        latency_ms=duration_ms,
        cost_usd=estimated_cost,
        guardrails={
            "threat_score": guardrails_result.threat_score,
            "risk_level": guardrails_result.risk_level.value,
            "action": guardrails_result.action.value,
            "output_valid": output_validation["valid"],
            "hallucination_risk": hallucination_check["hallucination_risk_score"],
            "compliant": compliance_check["compliant"],
        },
    )


@router.post("/stream")
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    if not chat_request.stream:
        chat_request.stream = True
    return await chat_completion(request, chat_request, background_tasks, session, auth)
