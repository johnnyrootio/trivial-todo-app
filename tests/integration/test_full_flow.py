"""Integration tests for full CLI flow.

These tests verify the complete workflow:
1. Add a todo via CLI
2. Verify the file is written correctly
3. List todos via CLI and verify output
4. Mark todo as done via CLI

Uses pytest fixtures for temp directory isolation and typer CliRunner
for CLI testing with real file I/O.
"""

import json
from collections.abc import Generator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from trivial_todo_app.cli import app


@pytest.fixture
def temp_todo_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    """Create a temporary directory and set it as the working directory.

    This fixture ensures that todos.json is written to the temp directory
    instead of the project root, providing test isolation.

    Args:
        tmp_path: pytest's built-in temp directory fixture
        monkeypatch: pytest's monkeypatch fixture for changing working directory

    Yields:
        Path to the temporary directory where todos.json will be written
    """
    # Change to temp directory so CLI writes todos.json there
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a typer CliRunner for testing CLI commands.

    Returns:
        CliRunner instance for invoking CLI commands
    """
    return CliRunner()


class TestFullFlow:
    """Integration tests for complete CLI workflows."""

    def test_add_todo_creates_file_and_list_shows_it(
        self, temp_todo_dir: Path, cli_runner: CliRunner
    ) -> None:
        """Adding a todo should create the file and list should show it.

        Flow:
        1. Add a todo via 'todo add'
        2. Verify todos.json exists and contains the todo
        3. Run 'todo list' and verify it displays the todo
        """
        # Step 1: Add a todo
        result = cli_runner.invoke(app, ["add", "Buy groceries"])
        assert result.exit_code == 0
        assert 'Added todo #1: "Buy groceries"' in result.stdout

        # Step 2: Verify the file was written
        todo_file = temp_todo_dir / "todos.json"
        assert todo_file.exists(), "todos.json should be created"

        # Verify file contents
        with open(todo_file) as f:
            todos_data = json.load(f)
        assert len(todos_data) == 1
        assert todos_data[0]["id"] == 1
        assert todos_data[0]["title"] == "Buy groceries"
        assert todos_data[0]["done"] is False

        # Step 3: List todos and verify output
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "[ ] #1: Buy groceries" in result.stdout

    def test_add_multiple_todos_and_list_all(
        self, temp_todo_dir: Path, cli_runner: CliRunner
    ) -> None:
        """Adding multiple todos should create file with all todos and list should show all.

        Flow:
        1. Add multiple todos
        2. Verify todos.json contains all todos
        3. Run 'todo list' and verify all are displayed
        """
        # Add multiple todos
        result1 = cli_runner.invoke(app, ["add", "Buy groceries"])
        assert result1.exit_code == 0

        result2 = cli_runner.invoke(app, ["add", "Walk the dog"])
        assert result2.exit_code == 0

        result3 = cli_runner.invoke(app, ["add", "Read a book"])
        assert result3.exit_code == 0

        # Verify file contains all todos
        todo_file = temp_todo_dir / "todos.json"
        assert todo_file.exists()

        with open(todo_file) as f:
            todos_data = json.load(f)
        assert len(todos_data) == 3
        assert todos_data[0]["title"] == "Buy groceries"
        assert todos_data[1]["title"] == "Walk the dog"
        assert todos_data[2]["title"] == "Read a book"

        # List all todos
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "[ ] #1: Buy groceries" in result.stdout
        assert "[ ] #2: Walk the dog" in result.stdout
        assert "[ ] #3: Read a book" in result.stdout

    def test_add_done_list_shows_completed(
        self, temp_todo_dir: Path, cli_runner: CliRunner
    ) -> None:
        """Marking a todo as done should update file and list should show it as completed.

        Flow:
        1. Add a todo
        2. Mark it as done via 'todo done'
        3. Verify todos.json shows done=true
        4. Run 'todo list' and verify it shows as completed
        """
        # Add a todo
        result = cli_runner.invoke(app, ["add", "Buy groceries"])
        assert result.exit_code == 0

        # Mark as done
        result = cli_runner.invoke(app, ["done", "1"])
        assert result.exit_code == 0
        assert 'Marked todo #1 as done: "Buy groceries"' in result.stdout

        # Verify file shows done=true
        todo_file = temp_todo_dir / "todos.json"
        with open(todo_file) as f:
            todos_data = json.load(f)
        assert todos_data[0]["done"] is True

        # List shows completed
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "[✓] #1: Buy groceries" in result.stdout

    def test_list_empty_when_no_todos(self, temp_todo_dir: Path, cli_runner: CliRunner) -> None:
        """Listing when no todos exist should show 'No todos found'.

        Flow:
        1. Run 'todo list' without adding any todos
        2. Verify it shows 'No todos found'
        3. Verify no todos.json file is created (or it doesn't exist)
        """
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No todos found" in result.stdout

        # File should not exist yet (no todos added)
        todo_file = temp_todo_dir / "todos.json"
        # Either file doesn't exist, or exists and is empty
        if todo_file.exists():
            with open(todo_file) as f:
                content = f.read()
            assert content in ("", "[]")

    def test_persistence_across_commands(self, temp_todo_dir: Path, cli_runner: CliRunner) -> None:
        """Todos should persist across separate CLI invocations.

        Flow:
        1. Add a todo in one CLI invocation
        2. Add another todo in a separate CLI invocation
        3. List in a third invocation and verify both are shown
        """
        # First invocation: add todo
        result1 = cli_runner.invoke(app, ["add", "First todo"])
        assert result1.exit_code == 0

        # Second invocation: add another todo
        result2 = cli_runner.invoke(app, ["add", "Second todo"])
        assert result2.exit_code == 0

        # Third invocation: list should show both
        result3 = cli_runner.invoke(app, ["list"])
        assert result3.exit_code == 0
        assert "[ ] #1: First todo" in result3.stdout
        assert "[ ] #2: Second todo" in result3.stdout

        # Verify file has both
        todo_file = temp_todo_dir / "todos.json"
        with open(todo_file) as f:
            todos_data = json.load(f)
        assert len(todos_data) == 2
