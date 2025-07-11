import pytest
from app.database import reset_db
from app.todo_service import TodoService
from app.models import TodoItemCreate


@pytest.fixture
def new_db():
    """Create a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_todo_service_integration(new_db):
    """Test the todo service integration with database."""
    todo_service = TodoService()

    # Test creating a todo
    todo_data = TodoItemCreate(title="Integration Test", description="Testing integration")
    todo = todo_service.create_todo(todo_data)

    assert todo.id is not None
    assert todo.title == "Integration Test"
    assert todo.description == "Testing integration"
    assert not todo.completed

    # Test retrieving all todos
    todos = todo_service.get_all_todos()
    assert len(todos) == 1
    assert todos[0].title == "Integration Test"

    # Test toggling completion
    if todo.id is not None:
        updated_todo = todo_service.toggle_todo_completion(todo.id)
        assert updated_todo is not None
        assert updated_todo.completed

    # Test deleting todo
    if todo.id is not None:
        success = todo_service.delete_todo(todo.id)
        assert success

        # Verify deletion
        todos_after_delete = todo_service.get_all_todos()
        assert len(todos_after_delete) == 0


def test_todo_ordering(new_db):
    """Test that todos are ordered correctly."""
    todo_service = TodoService()

    # Create multiple todos
    todo_service.create_todo(TodoItemCreate(title="First Todo"))
    todo_service.create_todo(TodoItemCreate(title="Second Todo"))
    todo_service.create_todo(TodoItemCreate(title="Third Todo"))

    todos = todo_service.get_all_todos()
    assert len(todos) == 3

    # Should be ordered newest first
    assert todos[0].title == "Third Todo"
    assert todos[1].title == "Second Todo"
    assert todos[2].title == "First Todo"


def test_todo_completion_states(new_db):
    """Test handling of different completion states."""
    todo_service = TodoService()

    # Create two todos
    todo1 = todo_service.create_todo(TodoItemCreate(title="Todo 1"))
    todo_service.create_todo(TodoItemCreate(title="Todo 2"))

    # Mark one as completed
    if todo1.id is not None:
        todo_service.toggle_todo_completion(todo1.id)

    # Get all todos and check states
    todos = todo_service.get_all_todos()

    # Find the todos by title
    todo1_updated = next((t for t in todos if t.title == "Todo 1"), None)
    todo2_unchanged = next((t for t in todos if t.title == "Todo 2"), None)

    assert todo1_updated is not None
    assert todo2_unchanged is not None

    assert todo1_updated.completed
    assert not todo2_unchanged.completed


def test_todo_edge_cases(new_db):
    """Test edge cases and boundary conditions."""
    todo_service = TodoService()

    # Test with empty description
    todo_empty_desc = todo_service.create_todo(TodoItemCreate(title="Empty Desc"))
    assert todo_empty_desc.description == ""

    # Test with very long title (up to limit)
    long_title = "A" * 200
    todo_long_title = todo_service.create_todo(TodoItemCreate(title=long_title))
    assert todo_long_title.title == long_title

    # Test with very long description (up to limit)
    long_desc = "B" * 1000
    todo_long_desc = todo_service.create_todo(TodoItemCreate(title="Long Desc", description=long_desc))
    assert todo_long_desc.description == long_desc

    # Test operations on non-existent todos
    result = todo_service.get_todo_by_id(999)
    assert result is None

    result = todo_service.toggle_todo_completion(999)
    assert result is None

    result = todo_service.delete_todo(999)
    assert not result
