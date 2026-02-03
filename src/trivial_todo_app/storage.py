"""JSON file storage for todos."""

import json
import tempfile
from pathlib import Path

from trivial_todo_app.todo import Todo


class TodoStorage:
    """Simple JSON file storage for todos."""

    def __init__(self, storage_path: Path = Path("todos.json")) -> None:
        """Initialize storage with a file path."""
        self.storage_path = storage_path

    def load(self) -> list[Todo]:
        """Load todos from JSON file."""
        if not self.storage_path.exists():
            return []
        try:
            data = json.loads(self.storage_path.read_text())
            return [Todo(id=item["id"], title=item["title"], done=item["done"]) for item in data]
        except json.JSONDecodeError:
            return []

    def save(self, todos: list[Todo]) -> None:
        """Save todos to JSON file using atomic write."""
        data = [{"id": t.id, "title": t.title, "done": t.done} for t in todos]
        json_data = json.dumps(data)

        # Atomic write: write to temp file in same directory, then rename
        fd, temp_path = tempfile.mkstemp(
            dir=self.storage_path.parent, prefix=".tmp_todos_", suffix=".json"
        )
        try:
            Path(temp_path).write_text(json_data)
            Path(temp_path).replace(self.storage_path)
        finally:
            try:
                import os

                os.close(fd)
            except OSError:
                pass
