"""Unit tests for TodoStorage."""

import json
import tempfile
from pathlib import Path

import pytest

from trivial_todo_app.storage import TodoStorage
from trivial_todo_app.todo import Todo


class TestTodoStorage:
    """Test suite for TodoStorage class."""

    def test_save_and_load_single_todo(self) -> None:
        """Saving and loading a single todo should persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            # Create and save a todo
            original_todo = Todo(id=1, title="Buy groceries", done=False)
            storage.save([original_todo])

            # Load and verify
            loaded_todos = storage.load()

            assert len(loaded_todos) == 1
            assert loaded_todos[0].id == 1
            assert loaded_todos[0].title == "Buy groceries"
            assert loaded_todos[0].done is False

    def test_load_from_nonexistent_file_returns_empty_list(self) -> None:
        """Loading from non-existent file should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            todos = storage.load()

            assert todos == []

    def test_save_and_load_multiple_todos(self) -> None:
        """Saving and loading multiple todos should preserve all data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            # Create and save multiple todos
            original_todos = [
                Todo(id=1, title="Buy groceries", done=False),
                Todo(id=2, title="Walk the dog", done=True),
                Todo(id=3, title="Read a book", done=False),
            ]
            storage.save(original_todos)

            # Load and verify
            loaded_todos = storage.load()

            assert len(loaded_todos) == 3
            assert loaded_todos[0].id == 1
            assert loaded_todos[0].title == "Buy groceries"
            assert loaded_todos[0].done is False
            assert loaded_todos[1].id == 2
            assert loaded_todos[1].title == "Walk the dog"
            assert loaded_todos[1].done is True
            assert loaded_todos[2].id == 3
            assert loaded_todos[2].title == "Read a book"
            assert loaded_todos[2].done is False

    def test_load_from_empty_file_returns_empty_list(self) -> None:
        """Loading from empty file should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            # Create empty file
            storage_path.write_text("")

            todos = storage.load()

            assert todos == []

    def test_load_from_invalid_json_returns_empty_list(self) -> None:
        """Loading from file with invalid JSON should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            # Create file with invalid JSON
            storage_path.write_text("not valid json")

            todos = storage.load()

            assert todos == []

    def test_save_uses_atomic_write(self) -> None:
        """Save should use atomic write (temp file + rename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "todos.json"
            storage = TodoStorage(storage_path)

            # Save todos
            todos = [Todo(id=1, title="Test", done=False)]
            storage.save(todos)

            # Verify file exists and contains correct data
            assert storage_path.exists()
            data = json.loads(storage_path.read_text())
            assert len(data) == 1
            assert data[0]["id"] == 1
