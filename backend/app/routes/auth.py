import asyncio
import logging
import os
import traceback

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth_middleware import get_current_user
from app.models.user_model import (
    CurrentUser,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Creates a Supabase Auth account and a matching profiles row.",
)
async def register(data: RegisterRequest) -> UserResponse:
    print("=" * 60)
    print(f"[REGISTER] Attempting admin.create_user for: {data.email}")

    # ── Step 1: admin.create_user ─────────────────────────────────
    # Uses the service-role key — never sends a confirmation email,
    # confirms the address immediately in the same call, and is not
    # subject to Supabase's email-per-hour rate limit.
    try:
        result = await asyncio.to_thread(
            supabase_service.client.auth.admin.create_user,
            {
                "email": data.email,
                "password": data.password,
                "email_confirm": True,
                "user_metadata": {"full_name": data.full_name},
            },
        )
        print(f"[REGISTER] admin.create_user result user={result.user}")
    except Exception as exc:
        print(f"[REGISTER] admin.create_user EXCEPTION type : {type(exc).__name__}")
        print(f"[REGISTER] admin.create_user EXCEPTION msg  : {exc}")
        print(f"[REGISTER] admin.create_user EXCEPTION attrs: {vars(exc) if hasattr(exc, '__dict__') else 'n/a'}")
        traceback.print_exc()
        msg = str(exc).lower()
        if "already registered" in msg or "already been registered" in msg or "already exists" in msg:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=f"Registration failed: {exc}")

    if not result.user:
        print(f"[REGISTER] admin.create_user returned no user — full result: {result}")
        raise HTTPException(status_code=400, detail="Registration failed: no user returned")

    user_id: str = result.user.id
    print(f"[REGISTER] User created & email confirmed. user_id={user_id}")

    # ── Step 2: upsert profile row ────────────────────────────────
    print(f"[REGISTER] Upserting profile full_name={data.full_name!r}")
    try:
        profile_result = await asyncio.to_thread(
            lambda: supabase_service.client.table("profiles")
            .upsert({"id": user_id, "full_name": data.full_name})
            .execute()
        )
        print(f"[REGISTER] Profile upsert OK: {profile_result.data}")
    except Exception as exc:
        print(f"[REGISTER] Profile upsert EXCEPTION type : {type(exc).__name__}")
        print(f"[REGISTER] Profile upsert EXCEPTION msg  : {exc}")
        traceback.print_exc()

    print(f"[REGISTER] Done — {data.email}")
    print("=" * 60)
    return UserResponse(id=user_id, email=data.email, full_name=data.full_name)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with email and password",
    description="Returns a JWT access_token on success.",
)
async def login(data: LoginRequest) -> LoginResponse:
    # Use httpx directly instead of client.auth.sign_in_with_password().
    # Calling sign_in_with_password() on the shared singleton client stores
    # the user session inside it, causing all subsequent table() queries to
    # send the user's JWT instead of the service-role key, which makes RLS
    # filter rows to only that user's data. Direct HTTP avoids this entirely.
    supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
    anon_key = os.environ["SUPABASE_ANON_KEY"]

    try:
        async with httpx.AsyncClient(timeout=10) as http:
            resp = await http.post(
                f"{supabase_url}/auth/v1/token?grant_type=password",
                headers={"apikey": anon_key, "Content-Type": "application/json"},
                json={"email": data.email, "password": data.password},
            )
            resp.raise_for_status()
            auth_data: dict = resp.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.error("Login HTTP error %s: %s", status, exc.response.text)
        if status in (400, 401):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=500, detail="Login failed")
    except Exception as exc:
        logger.error("Login failed: %s", exc)
        raise HTTPException(status_code=500, detail="Login failed")

    access_token: str = auth_data.get("access_token", "")
    user_obj: dict = auth_data.get("user", {})
    user_id: str = user_obj.get("id", "")
    email: str = user_obj.get("email", data.email)

    if not access_token or not user_id:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    try:
        profile_res = await asyncio.to_thread(
            lambda: supabase_service.client.table("profiles")
            .select("full_name")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        full_name: str = (
            profile_res.data[0].get("full_name", "") if profile_res.data else ""
        )
    except Exception as exc:
        logger.warning("Profile fetch failed: %s", exc)
        full_name = ""

    return LoginResponse(
        user=UserResponse(id=user_id, email=email, full_name=full_name),
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    "/logout",
    summary="Logout",
    description="Clears the client session. JWT expiry handles server-side invalidation.",
)
async def logout(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Returns the authenticated user's profile.",
)
async def me(current_user: CurrentUser = Depends(get_current_user)) -> UserResponse:
    try:
        profile_res = await asyncio.to_thread(
            lambda: supabase_service.client.table("profiles")
            .select("full_name")
            .eq("id", current_user.id)
            .limit(1)
            .execute()
        )
        full_name: str = (
            profile_res.data[0].get("full_name", "") if profile_res.data else ""
        )
    except Exception as exc:
        logger.error("Failed to fetch profile: %s", exc)
        full_name = ""

    return UserResponse(
        id=current_user.id, email=current_user.email, full_name=full_name
    )
