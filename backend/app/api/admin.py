from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.sqlalchemy_models import Organization, User, APIKey
from app.models.enums import AuditEventType
from app.services.auth_service import auth_service
from app.services.audit_service import audit_service
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "LLM Guardrails Gateway",
    }


@router.get("/organizations")
async def list_organizations(
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    from sqlalchemy import select
    result = await session.execute(select(Organization))
    orgs = result.scalars().all()
    return {
        "organizations": [
            {
                "id": o.id,
                "name": o.name,
                "slug": o.slug,
                "is_active": o.is_active,
                "created_at": o.created_at.isoformat(),
            }
            for o in orgs
        ]
    }


@router.post("/organizations")
async def create_organization(
    request: Request,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    body = await request.json()
    org = Organization(
        name=body["name"],
        slug=body.get("slug", body["name"].lower().replace(" ", "-")),
        settings=body.get("settings", {}),
    )
    session.add(org)
    await session.flush()

    await audit_service.log_event(
        session, org.id, AuditEventType.CONFIG_CHANGED,
        actor_id=auth[1], resource_type="organization", resource_id=org.id,
        action="create_organization", details={"name": org.name},
    )

    return {"id": org.id, "name": org.name, "slug": org.slug}


@router.post("/api-keys")
async def create_api_key(
    request: Request,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    organization_id = auth[0]
    body = await request.json()
    name = body.get("name", "Default Key")

    api_key, key_hash, key_prefix = auth_service.generate_api_key()

    api_key_record = APIKey(
        organization_id=organization_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
        permissions=body.get("permissions", ["chat:write", "security:read"]),
    )
    session.add(api_key_record)
    await session.flush()

    await audit_service.log_event(
        session, organization_id, AuditEventType.API_KEY_CREATED,
        actor_id=auth[1], resource_type="api_key",
        action="create_api_key", details={"name": name, "key_prefix": key_prefix},
    )

    return {
        "api_key": api_key,
        "key_prefix": key_prefix,
        "name": name,
        "id": api_key_record.id,
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    session: AsyncSession = Depends(get_session),
    auth: tuple = Depends(authenticate_request),
):
    from sqlalchemy import select
    result = await session.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.organization_id == auth[0])
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    from datetime import datetime
    api_key.is_active = False
    api_key.revoked_at = datetime.utcnow()
    await session.flush()

    await audit_service.log_event(
        session, auth[0], AuditEventType.API_KEY_REVOKED,
        actor_id=auth[1], resource_type="api_key", resource_id=key_id,
        action="revoke_api_key", details={"key_prefix": api_key.key_prefix},
    )

    return {"status": "revoked", "key_id": key_id}
