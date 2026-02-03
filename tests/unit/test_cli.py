"""Unit tests for CLI error handling paths."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from trivial_todo_app.cli import add, done, list, main
from trivial_todo_app.todo import Todo


class TestAddCommandErrorHandling:
    """Tests for add command error handling paths."""

    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_add_successfully_adds_todo(
        self, mock_storage_class, mock_manager_class, mock_echo
    ):
        """Add command successfully adds a todo and displays success message."""
        # Setup: manager.add returns a new todo
        mock_manager = Mock()
        new_todo = Todo(id=1, title="Test todo", done=False)
        mock_manager.add.return_value = new_todo
        mock_manager_class.return_value = mock_manager

        # Execute
        add("Test todo")

        # Verify success message was echoed
        mock_echo.assert_called_once_with('Added todo #1: "Test todo"')

    @patch("trivial_todo_app.cli.sys.exit")
    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_add_handles_value_error_from_manager(
        self, mock_storage_class, mock_manager_class, mock_echo, mock_exit
    ):
        """Add command handles ValueError from manager and exits with code 1."""
        # Setup: manager.add raises ValueError
        mock_manager = Mock()
        mock_manager.add.side_effect = ValueError("Title cannot be empty")
        mock_manager_class.return_value = mock_manager

        # Execute
        add("")

        # Verify error was echoed to stderr and exit(1) was called
        mock_echo.assert_called_once_with("Error: Title cannot be empty", err=True)
        mock_exit.assert_called_once_with(1)

    @patch("trivial_todo_app.cli.sys.exit")
    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_add_handles_generic_exception_from_storage(
        self, mock_storage_class, mock_manager_class, mock_echo, mock_exit
    ):
        """Add command handles generic Exception from storage and exits with code 1."""
        # Setup: manager.add raises generic exception (e.g., I/O error)
        mock_manager = Mock()
        mock_manager.add.side_effect = OSError("Permission denied")
        mock_manager_class.return_value = mock_manager

        # Execute
        add("Test todo")

        # Verify error was echoed to stderr and exit(1) was called
        mock_echo.assert_called_once_with(
            "Error: Failed to save todo: Permission denied", err=True
        )
        mock_exit.assert_called_once_with(1)


class TestListCommandErrorHandling:
    """Tests for list command error handling paths."""

    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_list_displays_no_todos_message_when_empty(
        self, mock_storage_class, mock_manager_class, mock_echo
    ):
        """List command displays 'No todos found' when list is empty."""
        # Setup: manager.list_all returns empty list
        mock_manager = Mock()
        mock_manager.list_all.return_value = []
        mock_manager_class.return_value = mock_manager

        # Execute
        list()

        # Verify message was echoed
        mock_echo.assert_called_once_with("No todos found")

    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_list_displays_todos_when_present(
        self, mock_storage_class, mock_manager_class, mock_echo
    ):
        """List command displays all todos with proper formatting."""
        # Setup: manager.list_all returns todos
        mock_manager = Mock()
        todos = [
            Todo(id=1, title="First todo", done=False),
            Todo(id=2, title="Second todo", done=True),
        ]
        mock_manager.list_all.return_value = todos
        mock_manager_class.return_value = mock_manager

        # Execute
        list()

        # Verify todos were displayed
        assert mock_echo.call_count == 2
        mock_echo.assert_any_call("[ ] #1: First todo")
        mock_echo.assert_any_call("[✓] #2: Second todo")

    @patch("trivial_todo_app.cli.sys.exit")
    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_list_handles_exception_from_storage(
        self, mock_storage_class, mock_manager_class, mock_echo, mock_exit
    ):
        """List command handles Exception from storage and exits with code 1."""
        # Setup: manager.list_all raises exception (e.g., I/O error)
        mock_manager = Mock()
        mock_manager.list_all.side_effect = OSError("Failed to read file")
        mock_manager_class.return_value = mock_manager

        # Execute
        list()

        # Verify error was echoed to stderr and exit(1) was called
        mock_echo.assert_called_once_with(
            "Error: Failed to load todos: Failed to read file", err=True
        )
        mock_exit.assert_called_once_with(1)


class TestDoneCommandErrorHandling:
    """Tests for done command error handling paths."""

    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_done_successfully_marks_todo_as_done(
        self, mock_storage_class, mock_manager_class, mock_echo
    ):
        """Done command successfully marks a todo as done and displays success message."""
        # Setup: manager returns todo before and after marking done
        mock_manager = Mock()
        not_done_todo = Todo(id=1, title="Test todo", done=False)
        done_todo = Todo(id=1, title="Test todo", done=True)
        # First call returns [not_done_todo], second call returns [done_todo]
        mock_manager.list_all.side_effect = [[not_done_todo], [done_todo]]
        mock_manager_class.return_value = mock_manager

        # Execute
        done(1)

        # Verify mark_done was called and success message was echoed
        mock_manager.mark_done.assert_called_once_with(1)
        mock_echo.assert_called_once_with('Marked todo #1 as done: "Test todo"')

    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_done_handles_already_done_todo(
        self, mock_storage_class, mock_manager_class, mock_echo
    ):
        """Done command detects already-done todo and returns early."""
        # Setup: manager returns a todo that's already done
        mock_manager = Mock()
        already_done_todo = Todo(id=1, title="Test", done=True)
        mock_manager.list_all.return_value = [already_done_todo]
        mock_manager_class.return_value = mock_manager

        # Execute
        done(1)

        # Verify message was displayed and mark_done was NOT called
        mock_echo.assert_called_once_with("Todo #1 is already done")
        mock_manager.mark_done.assert_not_called()

    @patch("trivial_todo_app.cli.sys.exit")
    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_done_handles_value_error_from_manager(
        self, mock_storage_class, mock_manager_class, mock_echo, mock_exit
    ):
        """Done command handles ValueError from manager and exits with code 1."""
        # Setup: manager.mark_done raises ValueError (todo not found)
        mock_manager = Mock()
        mock_manager.list_all.return_value = []
        mock_manager.mark_done.side_effect = ValueError("Todo #999 not found")
        mock_manager_class.return_value = mock_manager

        # Execute
        done(999)

        # Verify error was echoed to stderr and exit(1) was called
        mock_echo.assert_called_once_with("Error: Todo #999 not found", err=True)
        mock_exit.assert_called_once_with(1)

    @patch("trivial_todo_app.cli.sys.exit")
    @patch("trivial_todo_app.cli.typer.echo")
    @patch("trivial_todo_app.cli.TodoManager")
    @patch("trivial_todo_app.cli.TodoStorage")
    def test_done_handles_generic_exception_from_storage(
        self, mock_storage_class, mock_manager_class, mock_echo, mock_exit
    ):
        """Done command handles generic Exception from storage and exits with code 1."""
        # Setup: manager.mark_done raises generic exception (e.g., I/O error)
        mock_manager = Mock()
        mock_manager.list_all.return_value = [
            Todo(id=1, title="Test", done=False)
        ]
        mock_manager.mark_done.side_effect = OSError("Disk full")
        mock_manager_class.return_value = mock_manager

        # Execute
        done(1)

        # Verify error was echoed to stderr and exit(1) was called
        mock_echo.assert_called_once_with(
            "Error: Failed to save todo: Disk full", err=True
        )
        mock_exit.assert_called_once_with(1)


class TestMainEntryPoint:
    """Tests for main() entry point."""

    @patch("trivial_todo_app.cli.app")
    def test_main_calls_app(self, mock_app):
        """Main function invokes the typer app."""
        # Execute
        main()

        # Verify app was called
        mock_app.assert_called_once_with()
