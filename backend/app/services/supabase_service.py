import logging
import os
from typing import Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseService:
    _instance: Optional["SupabaseService"] = None

    def __new__(cls) -> "SupabaseService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._init_client()
        self._initialized: bool = True

    def _init_client(self) -> None:
        url: str = os.environ["SUPABASE_URL"]
        key: str = os.environ["SUPABASE_KEY"]  # service role key — bypasses RLS
        self._client: Client = create_client(url, key)
        logger.info("SupabaseService initialized (project: %s)", url)

    @property
    def client(self) -> Client:
        return self._client


supabase_service = SupabaseService()
