import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.models.todo_model import TodoCreate, TodoUpdate
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)


class TodoService:
    async def list_user_todos(self, user_id: str) -> list[dict[str, Any]]:
        def _query() -> Any:
            return (
                supabase_service.client.table("todos")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

        result = await asyncio.to_thread(_query)
        return result.data or []

    async def get_todo(self, todo_id: str) -> Optional[dict[str, Any]]:
        def _query() -> Any:
            return (
                supabase_service.client.table("todos")
                .select("*")
                .eq("id", todo_id)
                .limit(1)
                .execute()
            )

        result = await asyncio.to_thread(_query)
        return result.data[0] if result.data else None

    async def create_todo(self, user_id: str, data: TodoCreate) -> dict[str, Any]:
        now: str = datetime.now(timezone.utc).isoformat()

        def _query() -> Any:
            return (
                supabase_service.client.table("todos")
                .insert(
                    {
                        "title": data.title,
                        "description": data.description,
                        "is_completed": False,
                        "user_id": user_id,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                .execute()
            )

        result = await asyncio.to_thread(_query)
        return result.data[0]

    async def update_todo(self, todo_id: str, data: TodoUpdate) -> dict[str, Any]:
        update_fields: dict[str, Any] = data.model_dump(exclude_none=True)
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

        def _query() -> Any:
            return (
                supabase_service.client.table("todos")
                .update(update_fields)
                .eq("id", todo_id)
                .execute()
            )

        result = await asyncio.to_thread(_query)
        return result.data[0]

    async def delete_todo(self, todo_id: str) -> None:
        def _query() -> Any:
            return (
                supabase_service.client.table("todos")
                .delete()
                .eq("id", todo_id)
                .execute()
            )

        await asyncio.to_thread(_query)


todo_service = TodoService()
