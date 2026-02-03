"""Unit tests for Todo domain model and TodoManager."""

import pytest

from trivial_todo_app.storage import TodoStorage
from trivial_todo_app.todo import Todo


class TestTodoDataclass:
    """Tests for Todo dataclass."""

    def test_todo_creation_with_all_attributes(self):
        """Todo is created with correct id, title, and done attributes."""
        todo = Todo(id=1, title="Buy groceries", done=False)

        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.done is False

    def test_todo_done_defaults_to_false(self):
        """Todo done attribute defaults to False when not specified."""
        todo = Todo(id=1, title="Test task")

        assert todo.done is False


class TestTodoManager:
    """Tests for TodoManager business logic."""

    def test_init_accepts_storage(self, tmp_path):
        """TodoManager initializes with a TodoStorage instance."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        assert manager.storage is storage

    def test_add_creates_todo_with_id_1_for_empty_list(self, tmp_path):
        """Add creates todo with ID 1 when list is empty."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        todo = manager.add("Buy groceries")

        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.done is False

    def test_add_creates_todo_with_next_sequential_id(self, tmp_path):
        """Add creates todo with next sequential ID after existing todos."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        # Pre-populate with existing todos
        existing_todos = [
            Todo(id=1, title="First", done=False),
            Todo(id=2, title="Second", done=True),
        ]
        storage.save(existing_todos)

        manager = TodoManager(storage)
        todo = manager.add("Third task")

        assert todo.id == 3
        assert todo.title == "Third task"

    def test_add_saves_todo_to_storage(self, tmp_path):
        """Add persists the new todo to storage."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        manager.add("Test task")

        # Verify it was saved
        saved_todos = storage.load()
        assert len(saved_todos) == 1
        assert saved_todos[0].title == "Test task"

    def test_add_rejects_empty_title(self, tmp_path):
        """Add raises ValueError for empty title."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add("")

    def test_add_rejects_whitespace_only_title(self, tmp_path):
        """Add raises ValueError for whitespace-only title."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add("   ")

    def test_list_all_returns_empty_list_when_no_todos(self, tmp_path):
        """List all returns empty list when storage is empty."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        manager = TodoManager(storage)

        todos = manager.list_all()

        assert todos == []

    def test_list_all_returns_all_todos(self, tmp_path):
        """List all returns all todos from storage."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        # Pre-populate with todos
        existing_todos = [
            Todo(id=1, title="First", done=False),
            Todo(id=2, title="Second", done=True),
            Todo(id=3, title="Third", done=False),
        ]
        storage.save(existing_todos)

        manager = TodoManager(storage)
        todos = manager.list_all()

        assert len(todos) == 3
        assert todos[0].id == 1
        assert todos[1].id == 2
        assert todos[2].id == 3

    def test_mark_done_sets_done_flag(self, tmp_path):
        """Mark done sets the done flag to True."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        existing_todos = [
            Todo(id=1, title="First", done=False),
            Todo(id=2, title="Second", done=False),
        ]
        storage.save(existing_todos)

        manager = TodoManager(storage)
        manager.mark_done(1)

        # Verify it was marked done
        todos = storage.load()
        assert todos[0].done is True
        assert todos[1].done is False

    def test_mark_done_persists_to_storage(self, tmp_path):
        """Mark done persists the change to storage."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        existing_todos = [Todo(id=1, title="Test", done=False)]
        storage.save(existing_todos)

        manager = TodoManager(storage)
        manager.mark_done(1)

        # Load fresh from storage
        todos = storage.load()
        assert todos[0].done is True

    def test_mark_done_validates_todo_exists(self, tmp_path):
        """Mark done raises ValueError when todo doesn't exist."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        existing_todos = [Todo(id=1, title="Test", done=False)]
        storage.save(existing_todos)

        manager = TodoManager(storage)

        with pytest.raises(ValueError, match="Todo #999 not found"):
            manager.mark_done(999)

    def test_mark_done_validates_not_already_done(self, tmp_path):
        """Mark done raises ValueError when todo is already done."""
        from trivial_todo_app.todo import TodoManager

        storage = TodoStorage(tmp_path / "todos.json")
        existing_todos = [Todo(id=1, title="Test", done=True)]
        storage.save(existing_todos)

        manager = TodoManager(storage)

        with pytest.raises(ValueError, match="Todo #1 is already done"):
            manager.mark_done(1)
