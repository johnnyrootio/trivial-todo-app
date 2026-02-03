"""JSON file storage for todos."""

from pathlib import Path

from trivial_todo_app.todo import Todo


class TodoStorage:
    """Simple JSON file storage for todos."""

    def __init__(self, storage_path: Path = Path("todos.json")) -> None:
        """Initialize storage with a file path."""
        self.storage_path = storage_path

    def load(self) -> list[Todo]:
        """Load todos from JSON file."""
        # TODO: Implement JSON loading
        return []

    def save(self, todos: list[Todo]) -> None:
        """Save todos to JSON file."""
        # TODO: Implement JSON saving
        pass
