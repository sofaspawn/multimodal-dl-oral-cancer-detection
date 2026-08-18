import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from app.core.config import settings

# In production, use a proper secret from env
SECRET_KEY = "dev-secret-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


@dataclass
class TokenPayload:
    sub: int  # user_id
    exp: float  # unix timestamp


def _sign(payload: dict) -> str:
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")
    sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def _verify(token: str) -> dict | None:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        if not hmac.compare_digest(sig_b64, expected_b64):
            return None
        # Add padding back for decoding
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def create_access_token(user_id: int) -> str:
    payload = {"sub": user_id, "exp": time.time() + TOKEN_EXPIRE_HOURS * 3600}
    return _sign(payload)


def decode_token(token: str) -> TokenPayload | None:
    payload = _verify(token)
    if payload is None:
        return None
    return TokenPayload(sub=payload["sub"], exp=payload["exp"])


def hash_password(password: str) -> str:
    return hashlib.sha256((SECRET_KEY + password).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
