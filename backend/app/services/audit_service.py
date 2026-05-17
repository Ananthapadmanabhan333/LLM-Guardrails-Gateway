from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.sqlalchemy_models import AuditLog, RequestLog, ThreatEvent, PIIEvent
from app.models.enums import AuditEventType, RiskLevel


class AuditService:
    async def log_event(
        self,
        session: AsyncSession,
        organization_id: str,
        event_type: AuditEventType,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
        severity: RiskLevel = RiskLevel.LOW,
    ) -> AuditLog:
        entry = AuditLog(
            organization_id=organization_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            trace_id=trace_id,
            severity=severity,
        )
        session.add(entry)
        await session.flush()
        return entry

    async def get_audit_logs(
        self,
        session: AsyncSession,
        organization_id: str,
        event_type: Optional[AuditEventType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditLog]:
        query = select(AuditLog).where(AuditLog.organization_id == organization_id)

        if event_type:
            query = query.where(AuditLog.event_type == event_type)

        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_request_logs(
        self,
        session: AsyncSession,
        organization_id: str,
        limit: int = 50,
        offset: int = 0,
        is_blocked: Optional[bool] = None,
    ) -> List[RequestLog]:
        query = select(RequestLog).where(RequestLog.organization_id == organization_id)

        if is_blocked is not None:
            query = query.where(RequestLog.is_blocked == is_blocked)

        query = query.order_by(desc(RequestLog.created_at)).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_threat_events(
        self,
        session: AsyncSession,
        organization_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ThreatEvent]:
        query = (
            select(ThreatEvent)
            .where(ThreatEvent.organization_id == organization_id)
            .order_by(desc(ThreatEvent.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_dashboard_stats(self, session: AsyncSession, organization_id: str) -> Dict[str, Any]:
        total_requests = await session.scalar(
            select(func.count(RequestLog.id)).where(RequestLog.organization_id == organization_id)
        )
        blocked_requests = await session.scalar(
            select(func.count(RequestLog.id)).where(
                RequestLog.organization_id == organization_id,
                RequestLog.is_blocked == True,
            )
        )
        total_threats = await session.scalar(
            select(func.count(ThreatEvent.id)).where(ThreatEvent.organization_id == organization_id)
        )

        return {
            "total_requests": total_requests or 0,
            "blocked_requests": blocked_requests or 0,
            "total_threats": total_threats or 0,
            "block_rate": round((blocked_requests or 0) / max(total_requests or 1, 1) * 100, 2),
        }


audit_service = AuditService()
