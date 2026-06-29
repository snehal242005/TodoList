import asyncio
import logging
import os
import traceback
from typing import Optional

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Request

from app.models.user_model import CurrentUser

logger = logging.getLogger(__name__)

# Module-level singleton — fetches JWKS once and caches the keys.
_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        # .strip() removes any \r\n that Windows echo adds when storing secrets
        supabase_url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
        if not supabase_url:
            print("[JWKS] ERROR: SUPABASE_URL env var is empty or missing")
            raise RuntimeError("SUPABASE_URL is not set")
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        print(f"[JWKS] Initialising client with URL: {jwks_url}")
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        print("[JWKS] Client ready")
        logger.info("JWKS client ready: %s", jwks_url)
    return _jwks_client


async def get_current_user(request: Request) -> CurrentUser:
    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token: str = auth_header[len("Bearer "):]
    print(f"[AUTH] Verifying token — alg header: {_peek_alg(token)}, length: {len(token)}")

    try:
        client = _get_jwks_client()
        # get_signing_key_from_jwt fetches JWKS on first call, then uses cache.
        signing_key = await asyncio.to_thread(client.get_signing_key_from_jwt, token)
        print(f"[AUTH] Signing key obtained: {signing_key.key_id}")
        payload: dict = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256", "HS256"],
            options={"verify_aud": False},
        )
        print(f"[AUTH] Token valid — sub={payload.get('sub')}, email={payload.get('email')}")
    except jwt.ExpiredSignatureError:
        print("[AUTH] Token expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as exc:
        print(f"[AUTH] InvalidTokenError: {type(exc).__name__}: {exc}")
        logger.error("Token verification failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=401, detail=f"Invalid token: {type(exc).__name__}")
    except Exception as exc:
        print(f"[AUTH] EXCEPTION type : {type(exc).__name__}")
        print(f"[AUTH] EXCEPTION msg  : {exc}")
        traceback.print_exc()
        logger.error("Token verification error: %s", exc, exc_info=True)
        raise HTTPException(status_code=401, detail=f"Token error: {type(exc).__name__}: {exc}")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return CurrentUser(
        id=user_id,
        email=payload.get("email", ""),
    )


def _peek_alg(token: str) -> str:
    """Decode the JWT header without verification to log the algorithm."""
    try:
        return jwt.get_unverified_header(token).get("alg", "unknown")
    except Exception:
        return "unreadable"
