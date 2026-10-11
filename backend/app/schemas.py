import datetime
from enum import Enum
from typing import Optional, Union, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StatusEnum(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


# --- Task Schemas ---

class TaskBase(BaseModel):
    title: str = Field(..., description="Task title (required, non-empty)")
    description: Optional[str] = Field(None, description="Optional task description")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM, description="Low, Medium, or High")
    status: StatusEnum = Field(default=StatusEnum.PENDING, description="Pending, In Progress, or Completed")
    due_date: Optional[datetime.date] = Field(None, description="Optional due date in YYYY-MM-DD format")

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title is required and cannot be empty or whitespace-only.")
        return v.strip()

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date_format(cls, v: Optional[Union[str, datetime.date]]) -> Optional[datetime.date]:
        if v is None or v == "":
            return None
        if isinstance(v, datetime.date):
            return v
        try:
            return datetime.datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError("Due date must be a valid date in YYYY-MM-DD format (e.g. 2026-10-15).")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Optional updated title")
    description: Optional[str] = Field(None, description="Optional updated description")
    priority: Optional[PriorityEnum] = Field(None, description="Optional updated priority")
    status: Optional[StatusEnum] = Field(None, description="Optional updated status")
    due_date: Optional[Union[datetime.date, str]] = Field(None, description="Optional updated due date")

    @field_validator("title")
    @classmethod
    def validate_title_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty or whitespace-only.")
            return v.strip()
        return v

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date_update(cls, v: Optional[Union[str, datetime.date]]) -> Optional[datetime.date]:
        if v is None or v == "":
            return None
        if isinstance(v, datetime.date):
            return v
        try:
            return datetime.datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError("Due date must be a valid date in YYYY-MM-DD format (e.g. 2026-10-15).")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    due_date: Optional[datetime.date] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TaskSummaryResponse(BaseModel):
    total: int = Field(..., description="Total number of tasks")
    pending: int = Field(..., description="Number of tasks with Pending status")
    in_progress: int = Field(..., description="Number of tasks with In Progress status")
    completed: int = Field(..., description="Number of tasks with Completed status")


# --- AI Task Extraction Schemas ---

class TaskExtractRequest(BaseModel):
    text: str = Field(..., description="Plain-English task instruction to extract details from")

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Input instruction text cannot be empty.")
        return v.strip()


class TaskExtractResponse(BaseModel):
    title: str = Field(..., description="Extracted title of the task")
    priority: str = Field(default="Medium", description="Extracted priority: Low, Medium, or High")
    due_date: Optional[str] = Field(None, description="Extracted due date in YYYY-MM-DD format, or null")
    description: Optional[str] = Field(None, description="Extracted description or null")
    clarification_needed: Optional[str] = Field(
        None,
        description="Optional warning or clarification message for ambiguous dates or missing required details"
    )
    is_mock: bool = Field(default=False, description="Whether the extraction was performed by the mock fallback service")
    source: str = Field(default="AI", description="Provider model or engine used")


# --- Auth Schemas ---

class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
