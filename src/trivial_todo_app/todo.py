"""Todo data model."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trivial_todo_app.storage import TodoStorage


@dataclass
class Todo:
    """A todo item with title and done status."""

    id: int
    title: str
    done: bool = False


class TodoManager:
    """Manages todo business logic and coordinates with storage."""

    def __init__(self, storage: "TodoStorage") -> None:
        """Initialize manager with storage."""
        self.storage = storage

    def add(self, title: str) -> Todo:
        """Add a new todo with the given title."""
        # Validate title
        if not title.strip():
            raise ValueError("Title cannot be empty")

        todos = self.storage.load()

        # Generate next sequential ID
        next_id = max(todo.id for todo in todos) + 1 if todos else 1

        # Create new todo
        new_todo = Todo(id=next_id, title=title, done=False)

        # Append and save
        todos.append(new_todo)
        self.storage.save(todos)

        return new_todo

    def list_all(self) -> list[Todo]:
        """Return all todos from storage."""
        return self.storage.load()

    def mark_done(self, todo_id: int) -> None:
        """Mark a todo as done."""
        todos = self.storage.load()

        # Find the todo
        todo = None
        for t in todos:
            if t.id == todo_id:
                todo = t
                break

        # Validate todo exists
        if todo is None:
            raise ValueError(f"Todo #{todo_id} not found")

        # Validate not already done
        if todo.done:
            raise ValueError(f"Todo #{todo_id} is already done")

        # Mark as done and save
        todo.done = True
        self.storage.save(todos)
