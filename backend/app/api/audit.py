from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.enums import AuditEventType
from app.services.audit_service import audit_service
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
async def get_audit_logs(
    request: Request,
    event_type: Optional[AuditEventType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    offset = (page - 1) * page_size

    logs = await audit_service.get_audit_logs(
        session, organization_id,
        event_type=event_type,
        limit=page_size,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": log.id,
                "event_type": log.event_type.value if hasattr(log.event_type, "value") else log.event_type,
                "actor_id": log.actor_id,
                "actor_type": log.actor_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "trace_id": log.trace_id,
                "severity": log.severity.value if hasattr(log.severity, "value") else log.severity,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total": len(logs),
        "page": page,
        "page_size": page_size,
    }


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    stats = await audit_service.get_dashboard_stats(session, organization_id)
    return stats


@router.get("/requests")
async def get_request_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    is_blocked: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    offset = (page - 1) * page_size

    logs = await audit_service.get_request_logs(
        session, organization_id,
        limit=page_size,
        offset=offset,
        is_blocked=is_blocked,
    )

    return {
        "items": [
            {
                "id": log.id,
                "model": log.model,
                "provider": log.provider.value if hasattr(log.provider, "value") else log.provider,
                "tokens": log.total_tokens,
                "latency_ms": log.latency_ms,
                "cost_usd": log.cost_usd,
                "action": log.action_taken.value if hasattr(log.action_taken, "value") else log.action_taken,
                "risk_score": log.risk_score,
                "is_blocked": log.is_blocked,
                "is_sanitized": log.is_sanitized,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total": len(logs),
        "page": page,
        "page_size": page_size,
    }
