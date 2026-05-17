from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_session
from app.models.sqlalchemy_models import ThreatEvent, PIIEvent
from app.models.enums import ThreatType
from app.services.audit_service import audit_service
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("/")
async def get_threats(
    request: Request,
    threat_type: Optional[ThreatType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    offset = (page - 1) * page_size

    events = await audit_service.get_threat_events(
        session, organization_id,
        limit=page_size,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": e.id,
                "threat_type": e.threat_type.value if hasattr(e.threat_type, "value") else e.threat_type,
                "risk_level": e.risk_level.value if hasattr(e.risk_level, "value") else e.risk_level,
                "score": e.score,
                "detector_name": e.detector_name,
                "matched_pattern": e.matched_pattern,
                "action_taken": e.action_taken.value if hasattr(e.action_taken, "value") else e.action_taken,
                "details": e.details,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "total": len(events),
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
async def get_threat_stats(
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]

    total = await session.scalar(
        select(func.count(ThreatEvent.id)).where(ThreatEvent.organization_id == organization_id)
    )

    by_type = await session.execute(
        select(ThreatEvent.threat_type, func.count(ThreatEvent.id))
        .where(ThreatEvent.organization_id == organization_id)
        .group_by(ThreatEvent.threat_type)
    )

    by_severity = await session.execute(
        select(ThreatEvent.risk_level, func.count(ThreatEvent.id))
        .where(ThreatEvent.organization_id == organization_id)
        .group_by(ThreatEvent.risk_level)
    )

    return {
        "total_threats": total or 0,
        "by_type": {row[0].value if hasattr(row[0], "value") else row[0]: row[1] for row in by_type.fetchall()},
        "by_severity": {row[0].value if hasattr(row[0], "value") else row[0]: row[1] for row in by_severity.fetchall()},
    }


@router.get("/pii")
async def get_pii_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    offset = (page - 1) * page_size

    query = (
        select(PIIEvent)
        .where(PIIEvent.organization_id == organization_id)
        .order_by(desc(PIIEvent.created_at))
        .limit(page_size)
        .offset(offset)
    )
    result = await session.execute(query)
    events = result.scalars().all()

    return {
        "items": [
            {
                "id": e.id,
                "entity_type": e.entity_type.value if hasattr(e.entity_type, "value") else e.entity_type,
                "risk_level": e.risk_level.value if hasattr(e.risk_level, "value") else e.risk_level,
                "score": e.score,
                "text_preview": e.detected_text_preview,
                "was_redacted": e.was_redacted,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "total": len(events),
        "page": page,
        "page_size": page_size,
    }
