"""CLI entry point for trivial-todo-app."""

import sys
from pathlib import Path

import typer

from trivial_todo_app.storage import TodoStorage
from trivial_todo_app.todo import TodoManager

app = typer.Typer(help="Trivial Todo App - Add, list, and mark todos as done")

DEFAULT_TODO_FILE = Path("todos.json")


@app.command()
def add(title: str) -> None:
    """Add a new todo item."""
    try:
        storage = TodoStorage(DEFAULT_TODO_FILE)
        manager = TodoManager(storage)
        new_todo = manager.add(title)
        typer.echo(f'Added todo #{new_todo.id}: "{new_todo.title}"')
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: Failed to save todo: {e}", err=True)
        sys.exit(1)


@app.command()
def list() -> None:
    """List all todo items."""
    try:
        storage = TodoStorage(DEFAULT_TODO_FILE)
        manager = TodoManager(storage)
        todos = manager.list_all()

        if not todos:
            typer.echo("No todos found")
        else:
            for todo in todos:
                status = "✓" if todo.done else " "
                typer.echo(f"[{status}] #{todo.id}: {todo.title}")
    except Exception as e:
        typer.echo(f"Error: Failed to load todos: {e}", err=True)
        sys.exit(1)


@app.command()
def done(todo_id: int) -> None:
    """Mark a todo item as done."""
    try:
        storage = TodoStorage(DEFAULT_TODO_FILE)
        manager = TodoManager(storage)

        # Get all todos to find the one we need
        todos = manager.list_all()
        todo = None
        for t in todos:
            if t.id == todo_id:
                todo = t
                break

        # Check if already done before calling mark_done
        if todo and todo.done:
            typer.echo(f"Todo #{todo_id} is already done")
            return

        manager.mark_done(todo_id)

        # Get the updated todo to display its title
        todos = manager.list_all()
        for t in todos:
            if t.id == todo_id:
                typer.echo(f'Marked todo #{todo_id} as done: "{t.title}"')
                return
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: Failed to save todo: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
