from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate, UserRegister


def create_task(db: Session, task_in: TaskCreate) -> Task:
    """Create a new task record in the database."""
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority.value if hasattr(task_in.priority, "value") else task_in.priority,
        status=task_in.status.value if hasattr(task_in.status, "value") else task_in.status,
        due_date=task_in.due_date,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Retrieve a single task record by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Task]:
    """List tasks with optional status and priority filters and title search."""
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if search:
        # Case-insensitive substring search on title
        query = query.filter(Task.title.ilike(f"%{search.strip()}%"))

    return query.order_by(Task.id.desc()).all()


def get_tasks_summary(db: Session) -> Dict[str, int]:
    """Calculate task counts across all statuses."""
    total = db.query(func.count(Task.id)).scalar() or 0
    pending = db.query(func.count(Task.id)).filter(Task.status == "Pending").scalar() or 0
    in_progress = db.query(func.count(Task.id)).filter(Task.status == "In Progress").scalar() or 0
    completed = db.query(func.count(Task.id)).filter(Task.status == "Completed").scalar() or 0

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
    }


def update_task(db: Session, db_task: Task, task_update: TaskUpdate) -> Task:
    """Update fields of an existing task."""
    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, "value"):
                value = value.value
            setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, db_task: Task) -> None:
    """Delete a task record from the database."""
    db.delete(db_task)
    db.commit()


# --- User CRUD ---

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserRegister, password_hash: str) -> User:
    """Create a new user record."""
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=password_hash,
        full_name=user_in.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
