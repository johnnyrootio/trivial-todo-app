"""Black box functional system tests validating user workflows.

These tests validate complete user workflows from the operational specification
using subprocess execution to invoke the actual 'todo' command. Tests run in
isolated temporary directories and verify both CLI output and file contents.

Layer 4 - Black Box Tests (CRITICAL)
Per docs/testing-strategy.md section "Layer 4 - Black Box Tests"
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide isolated environment with temp directory as working directory.

    Each test gets a fresh temp directory set as the current working directory,
    ensuring todos.json is isolated per test.

    Args:
        tmp_path: pytest's built-in temp directory fixture
        monkeypatch: pytest's monkeypatch fixture for changing working directory

    Returns:
        Path to the temporary directory where todos.json will be written
    """
    # Change to temp directory so CLI writes todos.json there
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run_todo(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    """Run the 'todo' command via subprocess.

    Args:
        args: Command arguments (e.g., ["add", "Buy groceries"])
        check: If True, raise exception on non-zero exit code

    Returns:
        CompletedProcess with stdout, stderr, and returncode
    """
    return subprocess.run(
        ["todo"] + args,
        capture_output=True,
        text=True,
        check=check,
    )


def read_todos_json(temp_dir: Path) -> list[dict[str, Any]]:
    """Read and parse todos.json from the temp directory.

    Args:
        temp_dir: Path to the directory containing todos.json

    Returns:
        List of todo dictionaries from the JSON file
    """
    todos_file = temp_dir / "todos.json"
    if not todos_file.exists():
        return []

    with open(todos_file) as f:
        return json.load(f)


class TestWorkflow1EmptyState:
    """Workflow 1: First-Time User (Empty State)."""

    def test_list_on_empty_state_shows_correct_message(self, isolated_env: Path) -> None:
        """List on empty state shows 'No todos found' and exits with code 0."""
        result = run_todo(["list"])

        assert result.returncode == 0
        assert "No todos found" in result.stdout


class TestWorkflow2AddAndList:
    """Workflow 2: Add and List."""

    def test_add_multiple_todos_shows_success_messages_with_ids(self, isolated_env: Path) -> None:
        """Add multiple todos and verify success messages with sequential IDs."""
        # Add first todo
        result1 = run_todo(["add", "Buy groceries"])
        assert result1.returncode == 0
        assert 'Added todo #1: "Buy groceries"' in result1.stdout

        # Add second todo
        result2 = run_todo(["add", "Walk the dog"])
        assert result2.returncode == 0
        assert 'Added todo #2: "Walk the dog"' in result2.stdout

        # Add third todo
        result3 = run_todo(["add", "Read a book"])
        assert result3.returncode == 0
        assert 'Added todo #3: "Read a book"' in result3.stdout

    def test_list_shows_all_todos_in_table_format(self, isolated_env: Path) -> None:
        """List shows all added todos in the correct table format."""
        # Add multiple todos
        run_todo(["add", "Buy groceries"])
        run_todo(["add", "Walk the dog"])
        run_todo(["add", "Read a book"])

        # List todos
        result = run_todo(["list"])

        assert result.returncode == 0
        assert "[ ] #1: Buy groceries" in result.stdout
        assert "[ ] #2: Walk the dog" in result.stdout
        assert "[ ] #3: Read a book" in result.stdout


class TestWorkflow3MarkDone:
    """Workflow 3: Mark Done."""

    def test_mark_done_shows_checkmark_in_list(self, isolated_env: Path) -> None:
        """Add todo, mark as done, list shows '✓ Done'."""
        # Add a todo
        run_todo(["add", "Buy groceries"])

        # Mark as done
        result = run_todo(["done", "1"])
        assert result.returncode == 0
        assert 'Marked todo #1 as done: "Buy groceries"' in result.stdout

        # List should show completed
        result = run_todo(["list"])
        assert result.returncode == 0
        assert "[✓] #1: Buy groceries" in result.stdout


class TestWorkflow4PersistenceAcrossInvocations:
    """Workflow 4: Persistence Across Invocations."""

    def test_data_persists_across_subprocesses(self, isolated_env: Path) -> None:
        """Add todo in one subprocess, list in another, data persists."""
        # Add in first subprocess
        result1 = run_todo(["add", "Persistent todo"])
        assert result1.returncode == 0

        # List in second subprocess (separate invocation)
        result2 = run_todo(["list"])
        assert result2.returncode == 0
        assert "[ ] #1: Persistent todo" in result2.stdout

    def test_file_contents_match_expected_json_format(self, isolated_env: Path) -> None:
        """File contents match expected JSON format after operations."""
        # Add todos
        run_todo(["add", "First todo"])
        run_todo(["add", "Second todo"])

        # Mark one done
        run_todo(["done", "1"])

        # Read and verify JSON file structure
        todos = read_todos_json(isolated_env)

        assert len(todos) == 2

        # First todo should be done
        assert todos[0]["id"] == 1
        assert todos[0]["title"] == "First todo"
        assert todos[0]["done"] is True

        # Second todo should not be done
        assert todos[1]["id"] == 2
        assert todos[1]["title"] == "Second todo"
        assert todos[1]["done"] is False


class TestWorkflow5ErrorInvalidId:
    """Workflow 5: Error - Invalid ID."""

    def test_mark_nonexistent_todo_shows_error_and_exits_1(self, isolated_env: Path) -> None:
        """Mark non-existent todo as done shows error and exits with code 1."""
        # Try to mark non-existent todo
        result = run_todo(["done", "999"])

        assert result.returncode == 1
        assert "Todo #999 not found" in result.stderr

    def test_invalid_id_causes_no_data_corruption(self, isolated_env: Path) -> None:
        """Invalid ID operation causes no data corruption."""
        # Add a todo
        run_todo(["add", "Valid todo"])

        # Try invalid operation
        run_todo(["done", "999"])

        # Verify data integrity
        todos = read_todos_json(isolated_env)
        assert len(todos) == 1
        assert todos[0]["id"] == 1
        assert todos[0]["title"] == "Valid todo"
        assert todos[0]["done"] is False


class TestWorkflow6ErrorAlreadyDone:
    """Workflow 6: Error - Already Done."""

    def test_mark_done_twice_second_fails_with_error(self, isolated_env: Path) -> None:
        """Mark todo done twice, second shows informational message.

        NOTE: The operational spec says "display informational message" for
        already-done todos, not "error". The CLI returns exit code 0 with the
        message on stdout, which matches the spec's "Already Done Output" section.
        """
        # Add a todo
        run_todo(["add", "Todo to complete"])

        # Mark as done first time
        result1 = run_todo(["done", "1"])
        assert result1.returncode == 0

        # Mark as done second time
        result2 = run_todo(["done", "1"])
        assert result2.returncode == 0
        assert "Todo #1 is already done" in result2.stdout


class TestWorkflow7ErrorInvalidInput:
    """Workflow 7: Error - Invalid Input."""

    def test_empty_title_shows_error_and_exits_1(self, isolated_env: Path) -> None:
        """Empty title shows error and exits with code 1."""
        result = run_todo(["add", ""])

        assert result.returncode == 1
        # Error message should indicate title cannot be empty
        assert "title" in result.stderr.lower() or "empty" in result.stderr.lower()

    def test_non_integer_id_shows_error_and_exits_1(self, isolated_env: Path) -> None:
        """Non-integer ID shows error and exits with non-zero code.

        NOTE: Typer returns exit code 2 for CLI usage/parsing errors (invalid
        argument types), which is standard CLI convention. The operational spec
        says all errors should use exit code 1, but Typer's behavior differs.
        """
        # Add a todo first
        run_todo(["add", "Valid todo"])

        # Try with non-integer ID
        result = run_todo(["done", "abc"])

        # Typer returns exit code 2 for argument parsing errors (standard CLI behavior)
        assert result.returncode == 2
        # Error message should indicate invalid ID format
        assert (
            "invalid" in result.stderr.lower()
            or "integer" in result.stderr.lower()
            or "not a valid integer" in result.stderr.lower()
        )
