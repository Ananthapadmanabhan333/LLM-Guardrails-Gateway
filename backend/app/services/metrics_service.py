from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.sqlalchemy_models import RequestLog, ThreatEvent, MetricsSnapshot


class MetricsService:
    async def get_latency_percentiles(
        self,
        session: AsyncSession,
        organization_id: str,
        hours: int = 24,
    ) -> Dict[str, float]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = select(RequestLog.latency_ms).where(
            RequestLog.organization_id == organization_id,
            RequestLog.created_at >= cutoff,
            RequestLog.latency_ms.isnot(None),
        )
        result = await session.execute(query)
        latencies = sorted([r[0] for r in result.fetchall() if r[0]])

        if not latencies:
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}

        n = len(latencies)
        return {
            "p50": latencies[int(n * 0.5)],
            "p95": latencies[int(n * 0.95)],
            "p99": latencies[int(n * 0.99)],
            "avg": sum(latencies) / n,
        }

    async def get_requests_over_time(
        self,
        session: AsyncSession,
        organization_id: str,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = select(
            func.date_trunc("hour", RequestLog.created_at).label("hour"),
            func.count(RequestLog.id).label("count"),
            func.sum(RequestLog.total_tokens).label("tokens"),
        ).where(
            RequestLog.organization_id == organization_id,
            RequestLog.created_at >= cutoff,
        ).group_by(
            func.date_trunc("hour", RequestLog.created_at),
        ).order_by(
            func.date_trunc("hour", RequestLog.created_at),
        )
        result = await session.execute(query)
        return [
            {
                "timestamp": row.hour.isoformat(),
                "count": row.count,
                "tokens": row.tokens or 0,
            }
            for row in result.fetchall()
        ]

    async def get_threats_over_time(
        self,
        session: AsyncSession,
        organization_id: str,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = select(
            func.date_trunc("hour", ThreatEvent.created_at).label("hour"),
            func.count(ThreatEvent.id).label("count"),
        ).where(
            ThreatEvent.organization_id == organization_id,
            ThreatEvent.created_at >= cutoff,
        ).group_by(
            func.date_trunc("hour", ThreatEvent.created_at),
        ).order_by(
            func.date_trunc("hour", ThreatEvent.created_at),
        )
        result = await session.execute(query)
        return [
            {"timestamp": row.hour.isoformat(), "count": row.count}
            for row in result.fetchall()
        ]

    async def get_summary(
        self,
        session: AsyncSession,
        organization_id: str,
    ) -> Dict[str, Any]:
        total = await session.scalar(
            select(func.count(RequestLog.id)).where(RequestLog.organization_id == organization_id)
        )
        total_tokens = await session.scalar(
            select(func.sum(RequestLog.total_tokens)).where(RequestLog.organization_id == organization_id)
        )
        total_cost = await session.scalar(
            select(func.sum(RequestLog.cost_usd)).where(RequestLog.organization_id == organization_id)
        )
        blocked = await session.scalar(
            select(func.count(RequestLog.id)).where(
                RequestLog.organization_id == organization_id,
                RequestLog.is_blocked == True,
            )
        )
        threats = await session.scalar(
            select(func.count(ThreatEvent.id)).where(ThreatEvent.organization_id == organization_id)
        )

        latency = await self.get_latency_percentiles(session, organization_id)

        return {
            "total_requests": total or 0,
            "total_tokens": total_tokens or 0,
            "total_cost": round(total_cost or 0, 6),
            "blocked_requests": blocked or 0,
            "total_threats": threats or 0,
            "block_rate": round((blocked or 0) / max(total or 1, 1) * 100, 2),
            "latency": latency,
        }


metrics_service = MetricsService()
