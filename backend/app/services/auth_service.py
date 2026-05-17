import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_api_key(self) -> Tuple[str, str, str]:
        api_key = f"glg_{uuid.uuid4().hex}"
        key_hash = self.hash_api_key(api_key)
        key_prefix = api_key[:12]
        return api_key, key_hash, key_prefix

    def create_access_token(self, user_id: str, organization_id: str, role: str = "member") -> str:
        payload = {
            "sub": user_id,
            "org_id": organization_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes),
            "iat": datetime.utcnow(),
            "jti": uuid.uuid4().hex,
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


auth_service = AuthService()
