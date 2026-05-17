import hashlib
import hmac
from typing import Optional, Tuple
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.models.enums import Action

security = HTTPBearer(auto_error=False)


def verify_api_key(request: Request) -> Tuple[Optional[str], Optional[str]]:
    api_key = request.headers.get(settings.api_key_header)
    if not api_key:
        return None, None

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:8]

    return key_hash, key_prefix


async def authenticate_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Tuple[str, str, str]:
    organization_id = "default"
    user_id = "anonymous"
    role = "viewer"

    token = None
    if credentials:
        token = credentials.credentials

    api_key_hash, api_key_prefix = verify_api_key(request)

    if token:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            organization_id = payload.get("org_id", "default")
            user_id = payload.get("sub", "anonymous")
            role = payload.get("role", "viewer")
        except JWTError:
            pass

    return organization_id, user_id, role


def create_access_token(
    user_id: str,
    organization_id: str,
    role: str = "member",
) -> str:
    from datetime import datetime, timedelta
    payload = {
        "sub": user_id,
        "org_id": organization_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
