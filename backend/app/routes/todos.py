import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth_middleware import get_current_user
from app.models.todo_model import TodoCreate, TodoResponse, TodoUpdate
from app.models.user_model import CurrentUser
from app.services.todo_service import todo_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=list[TodoResponse],
    summary="List todos",
    description="Returns all todos for the authenticated user, newest first.",
)
async def list_todos(
    current_user: CurrentUser = Depends(get_current_user),
) -> list[TodoResponse]:
    try:
        todos = await todo_service.list_user_todos(current_user.id)
        return [TodoResponse.model_validate(t) for t in todos]
    except Exception as exc:
        logger.error("Failed to list todos: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch todos")


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a todo",
    description="Creates a new todo for the authenticated user.",
)
async def create_todo(
    data: TodoCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> TodoResponse:
    try:
        todo = await todo_service.create_todo(current_user.id, data)
        return TodoResponse.model_validate(todo)
    except Exception as exc:
        logger.error("Failed to create todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create todo")


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a todo",
    description="Returns a single todo by ID. Only the owner can access it.",
)
async def get_todo(
    todo_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> TodoResponse:
    try:
        todo = await todo_service.get_todo(todo_id)
    except Exception as exc:
        logger.error("Failed to fetch todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch todo")

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoResponse.model_validate(todo)


@router.patch(
    "/{todo_id}/complete",
    response_model=TodoResponse,
    summary="Mark todo as complete",
    description="Sets is_completed=True. Only the owner can mark complete.",
)
async def mark_complete(
    todo_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> TodoResponse:
    try:
        todo = await todo_service.get_todo(todo_id)
    except Exception as exc:
        logger.error("Failed to fetch todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch todo")

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        updated = await todo_service.update_todo(todo_id, TodoUpdate(is_completed=True))
        return TodoResponse.model_validate(updated)
    except Exception as exc:
        logger.error("Failed to mark complete: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to update todo")


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update a todo",
    description="Updates title, description, or is_completed. Only the owner can update.",
)
async def update_todo(
    todo_id: str,
    data: TodoUpdate,
    current_user: CurrentUser = Depends(get_current_user),
) -> TodoResponse:
    try:
        todo = await todo_service.get_todo(todo_id)
    except Exception as exc:
        logger.error("Failed to fetch todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch todo")

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        updated = await todo_service.update_todo(todo_id, data)
        return TodoResponse.model_validate(updated)
    except Exception as exc:
        logger.error("Failed to update todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to update todo")


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
    description="Deletes a todo. Only the owner can delete.",
)
async def delete_todo(
    todo_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    try:
        todo = await todo_service.get_todo(todo_id)
    except Exception as exc:
        logger.error("Failed to fetch todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch todo")

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        await todo_service.delete_todo(todo_id)
    except Exception as exc:
        logger.error("Failed to delete todo: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to delete todo")
