"""Interface contract tests for data schema specification.

Tests verify that the Todo data model and JSON serialization format
comply with the schema defined in contracts/data-schema.json.
"""

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

from trivial_todo_app.todo import Todo

# Load the JSON schema once for all tests
SCHEMA_PATH = Path(__file__).parent.parent.parent / "contracts" / "data-schema.json"
with open(SCHEMA_PATH) as f:
    DATA_SCHEMA = json.load(f)


def todo_to_dict(todo: Todo) -> dict:
    """Convert a Todo object to a dictionary matching the schema format."""
    return {
        "id": todo.id,
        "title": todo.title,
        "done": todo.done,
    }


def todos_to_json_data(todos: list[Todo]) -> list[dict]:
    """Convert a list of Todo objects to JSON-serializable data."""
    return [todo_to_dict(todo) for todo in todos]


class TestDataSchemaContract:
    """Test suite for data schema interface contract."""

    def test_empty_list_validates(self) -> None:
        """Empty todo list should validate against schema."""
        data = []
        validate(instance=data, schema=DATA_SCHEMA)

    def test_single_todo_validates(self) -> None:
        """Single todo item should validate against schema."""
        todo = Todo(id=1, title="Buy groceries", done=False)
        data = todos_to_json_data([todo])
        validate(instance=data, schema=DATA_SCHEMA)

    def test_multiple_todos_validate(self) -> None:
        """Multiple todo items should validate against schema."""
        todos = [
            Todo(id=1, title="Buy groceries", done=False),
            Todo(id=2, title="Walk the dog", done=True),
            Todo(id=3, title="Read a book", done=False),
        ]
        data = todos_to_json_data(todos)
        validate(instance=data, schema=DATA_SCHEMA)

    def test_all_required_fields_present(self) -> None:
        """Todo must have all required fields: id, title, done."""
        todo = Todo(id=1, title="Test todo", done=False)
        data = todo_to_dict(todo)

        # Verify all required fields are present
        assert "id" in data
        assert "title" in data
        assert "done" in data

    def test_field_types_correct(self) -> None:
        """Todo fields must have correct types."""
        todo = Todo(id=42, title="Test todo", done=True)
        data = todo_to_dict(todo)

        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["done"], bool)

    def test_id_minimum_constraint(self) -> None:
        """ID must be >= 1 according to schema."""
        todo = Todo(id=1, title="Valid ID", done=False)
        data = todos_to_json_data([todo])
        validate(instance=data, schema=DATA_SCHEMA)

    def test_invalid_id_zero_fails(self) -> None:
        """ID of 0 should fail validation (minimum is 1)."""
        data = [{"id": 0, "title": "Invalid", "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_invalid_id_negative_fails(self) -> None:
        """Negative ID should fail validation."""
        data = [{"id": -1, "title": "Invalid", "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_title_non_empty(self) -> None:
        """Title must not be empty."""
        data = [{"id": 1, "title": "", "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_title_not_whitespace_only(self) -> None:
        """Title must not be whitespace-only (pattern: .*\\S.*)."""
        data = [{"id": 1, "title": "   ", "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_title_with_content_validates(self) -> None:
        """Title with actual content should validate."""
        todo = Todo(id=1, title="Buy groceries", done=False)
        data = todos_to_json_data([todo])
        validate(instance=data, schema=DATA_SCHEMA)

    def test_missing_id_fails(self) -> None:
        """Missing required 'id' field should fail validation."""
        data = [{"title": "No ID", "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_missing_title_fails(self) -> None:
        """Missing required 'title' field should fail validation."""
        data = [{"id": 1, "done": False}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_missing_done_fails(self) -> None:
        """Missing required 'done' field should fail validation."""
        data = [{"id": 1, "title": "No done field"}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_additional_properties_not_allowed(self) -> None:
        """Additional properties beyond id, title, done should fail validation."""
        data = [{"id": 1, "title": "Test", "done": False, "extra": "field"}]
        with pytest.raises(ValidationError):
            validate(instance=data, schema=DATA_SCHEMA)

    def test_done_default_false(self) -> None:
        """Default value for done should be false."""
        todo = Todo(id=1, title="Test", done=False)
        data = todo_to_dict(todo)
        assert data["done"] is False

    def test_done_can_be_true(self) -> None:
        """Done field can be set to true."""
        todo = Todo(id=1, title="Completed task", done=True)
        data = todos_to_json_data([todo])
        validate(instance=data, schema=DATA_SCHEMA)

    def test_schema_examples_validate(self) -> None:
        """Schema examples should all validate against the schema."""
        for example in DATA_SCHEMA.get("examples", []):
            validate(instance=example, schema=DATA_SCHEMA)
