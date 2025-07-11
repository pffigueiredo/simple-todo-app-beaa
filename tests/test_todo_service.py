import pytest
from datetime import datetime
from app.todo_service import TodoService
from app.models import TodoItemCreate, TodoItemUpdate
from app.database import reset_db


@pytest.fixture
def todo_service():
    """Create a fresh todo service with clean database."""
    reset_db()
    return TodoService()


@pytest.fixture
def sample_todo_data():
    """Sample todo data for testing."""
    return TodoItemCreate(title="Test Todo", description="This is a test todo item")


def test_create_todo(todo_service, sample_todo_data):
    """Test creating a new todo item."""
    todo = todo_service.create_todo(sample_todo_data)

    assert todo.id is not None
    assert todo.title == "Test Todo"
    assert todo.description == "This is a test todo item"
    assert not todo.completed
    assert isinstance(todo.created_at, datetime)
    assert isinstance(todo.updated_at, datetime)


def test_create_todo_minimal(todo_service):
    """Test creating a todo with minimal data."""
    todo_data = TodoItemCreate(title="Minimal Todo")
    todo = todo_service.create_todo(todo_data)

    assert todo.id is not None
    assert todo.title == "Minimal Todo"
    assert todo.description == ""
    assert not todo.completed


def test_get_all_todos_empty(todo_service):
    """Test getting all todos when none exist."""
    todos = todo_service.get_all_todos()
    assert todos == []


def test_get_all_todos_with_data(todo_service):
    """Test getting all todos with multiple items."""
    # Create multiple todos
    todo1 = todo_service.create_todo(TodoItemCreate(title="First Todo"))
    todo2 = todo_service.create_todo(TodoItemCreate(title="Second Todo"))

    todos = todo_service.get_all_todos()
    assert len(todos) == 2

    # Should be ordered by creation date (newest first)
    assert todos[0].id == todo2.id
    assert todos[1].id == todo1.id


def test_get_todo_by_id_exists(todo_service, sample_todo_data):
    """Test getting a todo by ID when it exists."""
    created_todo = todo_service.create_todo(sample_todo_data)

    if created_todo.id is not None:
        retrieved_todo = todo_service.get_todo_by_id(created_todo.id)
        assert retrieved_todo is not None
        assert retrieved_todo.id == created_todo.id
        assert retrieved_todo.title == created_todo.title


def test_get_todo_by_id_not_exists(todo_service):
    """Test getting a todo by ID when it doesn't exist."""
    todo = todo_service.get_todo_by_id(999)
    assert todo is None


def test_update_todo_success(todo_service, sample_todo_data):
    """Test updating a todo item successfully."""
    created_todo = todo_service.create_todo(sample_todo_data)

    if created_todo.id is not None:
        update_data = TodoItemUpdate(title="Updated Todo", description="Updated description", completed=True)

        updated_todo = todo_service.update_todo(created_todo.id, update_data)

        assert updated_todo is not None
        assert updated_todo.title == "Updated Todo"
        assert updated_todo.description == "Updated description"
        assert updated_todo.completed
        assert updated_todo.updated_at > created_todo.updated_at


def test_update_todo_partial(todo_service, sample_todo_data):
    """Test partial update of a todo item."""
    created_todo = todo_service.create_todo(sample_todo_data)

    if created_todo.id is not None:
        update_data = TodoItemUpdate(completed=True)

        updated_todo = todo_service.update_todo(created_todo.id, update_data)

        assert updated_todo is not None
        assert updated_todo.title == created_todo.title  # Unchanged
        assert updated_todo.description == created_todo.description  # Unchanged
        assert updated_todo.completed  # Changed


def test_update_todo_not_exists(todo_service):
    """Test updating a todo that doesn't exist."""
    update_data = TodoItemUpdate(title="Non-existent Todo")
    result = todo_service.update_todo(999, update_data)
    assert result is None


def test_toggle_todo_completion_success(todo_service, sample_todo_data):
    """Test toggling todo completion successfully."""
    created_todo = todo_service.create_todo(sample_todo_data)

    if created_todo.id is not None:
        # Toggle from False to True
        toggled_todo = todo_service.toggle_todo_completion(created_todo.id)
        assert toggled_todo is not None
        assert toggled_todo.completed

        # Toggle from True to False
        toggled_again = todo_service.toggle_todo_completion(created_todo.id)
        assert toggled_again is not None
        assert not toggled_again.completed


def test_toggle_todo_completion_not_exists(todo_service):
    """Test toggling completion for non-existent todo."""
    result = todo_service.toggle_todo_completion(999)
    assert result is None


def test_delete_todo_success(todo_service, sample_todo_data):
    """Test deleting a todo successfully."""
    created_todo = todo_service.create_todo(sample_todo_data)

    if created_todo.id is not None:
        # Delete the todo
        success = todo_service.delete_todo(created_todo.id)
        assert success

        # Verify it's gone
        retrieved_todo = todo_service.get_todo_by_id(created_todo.id)
        assert retrieved_todo is None


def test_delete_todo_not_exists(todo_service):
    """Test deleting a todo that doesn't exist."""
    success = todo_service.delete_todo(999)
    assert not success


def test_todo_lifecycle(todo_service):
    """Test complete todo lifecycle."""
    # Create
    todo_data = TodoItemCreate(title="Lifecycle Todo", description="Test lifecycle")
    created_todo = todo_service.create_todo(todo_data)
    assert created_todo.id is not None

    # Read
    retrieved_todo = todo_service.get_todo_by_id(created_todo.id)
    assert retrieved_todo is not None
    assert retrieved_todo.title == "Lifecycle Todo"

    # Update
    update_data = TodoItemUpdate(title="Updated Lifecycle Todo")
    updated_todo = todo_service.update_todo(created_todo.id, update_data)
    assert updated_todo is not None
    assert updated_todo.title == "Updated Lifecycle Todo"

    # Toggle completion
    toggled_todo = todo_service.toggle_todo_completion(created_todo.id)
    assert toggled_todo is not None
    assert toggled_todo.completed

    # Delete
    success = todo_service.delete_todo(created_todo.id)
    assert success

    # Verify deletion
    final_todo = todo_service.get_todo_by_id(created_todo.id)
    assert final_todo is None


def test_multiple_todos_ordering(todo_service):
    """Test that todos are properly ordered by creation date."""
    # Create todos with slight delay to ensure different timestamps
    todo_service.create_todo(TodoItemCreate(title="First"))
    todo_service.create_todo(TodoItemCreate(title="Second"))
    todo_service.create_todo(TodoItemCreate(title="Third"))

    todos = todo_service.get_all_todos()

    # Should be ordered newest first
    assert len(todos) == 3
    assert todos[0].title == "Third"
    assert todos[1].title == "Second"
    assert todos[2].title == "First"


def test_empty_title_handling(todo_service):
    """Test handling of empty titles."""
    # SQLModel allows empty strings, so this should work
    todo = todo_service.create_todo(TodoItemCreate(title=""))
    assert todo.title == ""


def test_long_title_and_description(todo_service):
    """Test handling of maximum length titles and descriptions."""
    long_title = "A" * 200  # Max length
    long_description = "B" * 1000  # Max length

    todo_data = TodoItemCreate(title=long_title, description=long_description)
    todo = todo_service.create_todo(todo_data)

    assert todo.title == long_title
    assert todo.description == long_description
