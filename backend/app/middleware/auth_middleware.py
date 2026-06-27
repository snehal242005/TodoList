import asyncio
import logging
import os
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
        supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        # cache_keys=True keeps the public keys in memory after the first fetch.
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        logger.info("JWKS client ready: %s", jwks_url)
    return _jwks_client


async def get_current_user(request: Request) -> CurrentUser:
    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token: str = auth_header[len("Bearer "):]

    try:
        client = _get_jwks_client()
        # get_signing_key_from_jwt does a network fetch on the first call only.
        signing_key = await asyncio.to_thread(client.get_signing_key_from_jwt, token)
        payload: dict = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256", "HS256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as exc:
        logger.error("Token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as exc:
        logger.error("Token verification error: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return CurrentUser(
        id=user_id,
        email=payload.get("email", ""),
    )
