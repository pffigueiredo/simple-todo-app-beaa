from datetime import datetime
from typing import List, Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import TodoItem, TodoItemCreate, TodoItemUpdate


class TodoService:
    """Service layer for todo operations."""

    def create_todo(self, todo_data: TodoItemCreate) -> TodoItem:
        """Create a new todo item."""
        with get_session() as session:
            todo = TodoItem(**todo_data.model_dump())
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return todo

    def get_all_todos(self) -> List[TodoItem]:
        """Get all todo items ordered by creation date."""
        with get_session() as session:
            statement = select(TodoItem).order_by(desc(TodoItem.created_at))
            todos = session.exec(statement).all()
            return list(todos)

    def get_todo_by_id(self, todo_id: int) -> Optional[TodoItem]:
        """Get a specific todo item by ID."""
        with get_session() as session:
            return session.get(TodoItem, todo_id)

    def update_todo(self, todo_id: int, update_data: TodoItemUpdate) -> Optional[TodoItem]:
        """Update a todo item."""
        with get_session() as session:
            todo = session.get(TodoItem, todo_id)
            if todo is None:
                return None

            # Update fields if provided
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(todo, field, value)

            todo.updated_at = datetime.utcnow()
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return todo

    def toggle_todo_completion(self, todo_id: int) -> Optional[TodoItem]:
        """Toggle the completion status of a todo item."""
        with get_session() as session:
            todo = session.get(TodoItem, todo_id)
            if todo is None:
                return None

            todo.completed = not todo.completed
            todo.updated_at = datetime.utcnow()
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return todo

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo item."""
        with get_session() as session:
            todo = session.get(TodoItem, todo_id)
            if todo is None:
                return False

            session.delete(todo)
            session.commit()
            return True
