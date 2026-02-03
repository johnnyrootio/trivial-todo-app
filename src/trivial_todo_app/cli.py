"""CLI entry point for trivial-todo-app."""

import typer

app = typer.Typer(help="Trivial Todo App - Add, list, and mark todos as done")


@app.command()
def add(title: str) -> None:
    """Add a new todo item."""
    typer.echo(f"TODO: Implement add - {title}")


@app.command()
def list() -> None:
    """List all todo items."""
    typer.echo("TODO: Implement list")


@app.command()
def done(todo_id: int) -> None:
    """Mark a todo item as done."""
    typer.echo(f"TODO: Implement done - {todo_id}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
