from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.metrics_service import metrics_service
from app.middleware.auth import authenticate_request
from app.observability import metrics as metrics_module

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/")
async def get_prometheus_metrics():
    return PlainTextResponse(content=metrics_module.get_metrics().decode("utf-8"))


@router.get("/summary")
async def get_summary(
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    return await metrics_service.get_summary(session, organization_id)


@router.get("/latency")
async def get_latency(
    hours: int = 24,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    return await metrics_service.get_latency_percentiles(session, organization_id, hours)


@router.get("/requests")
async def get_requests_over_time(
    hours: int = 24,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    return {
        "data": await metrics_service.get_requests_over_time(session, organization_id, hours),
        "period_hours": hours,
    }


@router.get("/threats")
async def get_threats_over_time(
    hours: int = 24,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    return {
        "data": await metrics_service.get_threats_over_time(session, organization_id, hours),
        "period_hours": hours,
    }
