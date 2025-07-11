from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TodoItem(SQLModel, table=True):
    """Todo item model for storing tasks in the database."""

    __tablename__ = "todo_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoItemCreate(SQLModel, table=False):
    """Schema for creating new todo items."""

    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)


class TodoItemUpdate(SQLModel, table=False):
    """Schema for updating todo items."""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
