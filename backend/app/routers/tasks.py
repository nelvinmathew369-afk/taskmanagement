from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskSummaryResponse,
    PriorityEnum,
    StatusEnum,
)
from app import crud

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task and returns its generated ID along with all task details."
)
def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a task and return its generated ID.
    - **title**: Required; empty or whitespace-only titles are rejected with HTTP 422.
    - **description**: Optional text.
    - **priority**: Low, Medium, or High (default: Medium). Invalid priorities rejected with HTTP 422.
    - **status**: Pending, In Progress, or Completed (default: Pending). Invalid statuses rejected with HTTP 422.
    - **due_date**: Optional date in YYYY-MM-DD format. Malformed dates rejected with HTTP 422.
    """
    created = crud.create_task(db=db, task_in=task_in)
    return created


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="List tasks with filters and search",
    description="List tasks; support status and priority filters and title search."
)
def list_tasks_endpoint(
    status_filter: Optional[StatusEnum] = Query(
        None,
        alias="status",
        description="Filter tasks by status: 'Pending', 'In Progress', or 'Completed'"
    ),
    priority_filter: Optional[PriorityEnum] = Query(
        None,
        alias="priority",
        description="Filter tasks by priority: 'Low', 'Medium', or 'High'"
    ),
    search: Optional[str] = Query(
        None,
        description="Case-insensitive substring search query matching against task title"
    ),
    db: Session = Depends(get_db)
):
    """
    List tasks with optional filters:
    - **status**: filter by status (Pending, In Progress, Completed)
    - **priority**: filter by priority (Low, Medium, High)
    - **search**: search term to match against task titles
    """
    status_val = status_filter.value if status_filter else None
    priority_val = priority_filter.value if priority_filter else None
    return crud.list_tasks(
        db=db,
        status=status_val,
        priority=priority_val,
        search=search
    )


# CRITICAL ROUTE ORDERING:
# /tasks/summary MUST precede /tasks/{id} so that the path parameter {id} does not capture the literal string 'summary'.
@router.get(
    "/summary",
    response_model=TaskSummaryResponse,
    summary="Get task status counts summary",
    description="Return total, pending, in-progress and completed task counts. Accessible without being interpreted as a task ID."
)
def get_task_summary(
    db: Session = Depends(get_db)
):
    """
    Returns counts for all task statuses:
    - total: overall task count
    - pending: count of tasks with status 'Pending'
    - in_progress: count of tasks with status 'In Progress'
    - completed: count of tasks with status 'Completed'
    """
    return crud.get_tasks_summary(db=db)


@router.get(
    "/{id}",
    response_model=TaskResponse,
    summary="Retrieve a task by ID",
    description="Retrieve one task by its unique numeric ID. Returns HTTP 404 if not found."
)
def get_task(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve one task by ID:
    - Returns task details if found.
    - Returns 404 Not Found if task ID does not exist.
    """
    task = crud.get_task_by_id(db=db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    return task


@router.patch(
    "/{id}",
    response_model=TaskResponse,
    summary="Update task fields",
    description="Update supplied task fields or status. Validates all updated fields."
)
def update_task_endpoint(
    id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update supplied task fields or status:
    - Any provided field is validated (title cannot be empty, priority/status must be valid, due_date must be valid format).
    - Returns 404 Not Found if task ID does not exist.
    """
    db_task = crud.get_task_by_id(db=db, task_id=id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    return crud.update_task(db=db, db_task=db_task, task_update=task_update)


@router.delete(
    "/{id}",
    summary="Delete a task",
    description="Delete a task by ID. Returns HTTP 404 if not found."
)
def delete_task_endpoint(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a task by ID:
    - Returns 404 Not Found if task ID does not exist.
    - Returns success message confirming deletion.
    """
    db_task = crud.get_task_by_id(db=db, task_id=id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    crud.delete_task(db=db, db_task=db_task)
    return {"message": f"Task with ID {id} deleted successfully", "id": id}
