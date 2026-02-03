# Testing Strategy

**Project**: Trivial Todo App
**Version**: 1.0
**Last Updated**: 2026-02-02

## Overview

This document defines the comprehensive testing strategy for the Trivial Todo App. The strategy employs a four-layer testing approach designed to ensure correctness, reliability, and maintainability while supporting test-driven development (TDD) workflows.

### Testing Philosophy

- **Test-First Development**: Tests are written before implementation code
- **Comprehensive Coverage**: 90%+ coverage required for each component
- **Fast Feedback**: Unit tests run in milliseconds, full suite in seconds
- **Clear Ownership**: Test authors are separate from implementers
- **Arbitrated Quality**: Independent test arbitration for disputed tests

## Four-Layer Testing Approach

The testing strategy consists of four complementary layers, each serving a distinct purpose:

```
┌─────────────────────────────────────────────┐
│  Layer 4: Black Box Tests                  │
│  (End-to-end operational validation)       │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 3: Integration Tests                │
│  (Component interaction testing)           │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 2: Unit Tests (TDD)                 │
│  (Individual component testing)            │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 1: Interface Contract Tests         │
│  (CLI behavior specification)              │
└─────────────────────────────────────────────┘
```

### Layer 1: Interface Contract Tests

**Purpose**: Define and validate the external CLI interface contract.

**Scope**:
- Command syntax and arguments
- Help text and documentation
- Error messages and exit codes
- User-facing behavior

**Location**: `tests/contracts/`

**Technology**: pytest with subprocess execution

**Example Tests**:
```python
def test_add_command_syntax():
    """Verify 'todo add' accepts title argument."""
    result = subprocess.run(["todo", "add", "Test"], capture_output=True)
    assert result.returncode == 0

def test_help_displays_all_commands():
    """Verify --help shows add, list, and done commands."""
    result = subprocess.run(["todo", "--help"], capture_output=True)
    output = result.stdout.decode()
    assert "add" in output
    assert "list" in output
    assert "done" in output
```

**Coverage Requirement**: 100% of CLI commands and error paths

**Ownership**: Written by test authors, not implementers

### Layer 2: Unit Tests (TDD)

**Purpose**: Drive implementation through test-first development and validate individual components.

**Scope**:
- Individual functions and methods
- Data model behavior
- Storage operations
- CLI command handlers

**Location**: `tests/unit/`

**Structure**:
```
tests/unit/
├── test_todo.py         # Todo model tests
├── test_storage.py      # TodoStorage tests
└── test_cli.py          # CLI command tests
```

**Technology**: pytest with appropriate fixtures

**Example Tests**:
```python
# tests/unit/test_todo.py
def test_todo_creation():
    """Todo is created with correct attributes."""
    todo = Todo(id=1, title="Test", done=False)
    assert todo.id == 1
    assert todo.title == "Test"
    assert todo.done is False

# tests/unit/test_storage.py
def test_save_creates_file(tmp_path):
    """Save creates JSON file with correct format."""
    storage = TodoStorage(tmp_path / "todos.json")
    todos = [Todo(id=1, title="Test", done=False)]
    storage.save(todos)

    assert storage.storage_path.exists()
    data = json.loads(storage.storage_path.read_text())
    assert len(data) == 1
    assert data[0]["id"] == 1

# tests/unit/test_cli.py
def test_add_command_success(tmp_storage):
    """Add command creates todo and displays confirmation."""
    # Test implementation here
    pass
```

**Coverage Requirement**: 90%+ per module

**TDD Workflow**:
1. Test author writes failing test
2. Implementer runs test (it fails)
3. Implementer writes minimal code to pass
4. Implementer runs test (it passes)
5. Implementer refactors if needed
6. Repeat

**Ownership**: Written by test authors, implementers make them pass

### Layer 3: Integration Tests

**Purpose**: Validate interactions between components and end-to-end workflows.

**Scope**:
- CLI → Domain → Storage workflows
- File persistence and retrieval
- Error propagation across layers
- Multi-operation sequences

**Location**: `tests/integration/`

**Structure**:
```
tests/integration/
├── test_add_workflow.py      # Add command full workflow
├── test_list_workflow.py     # List command full workflow
├── test_done_workflow.py     # Done command full workflow
└── test_persistence.py       # Data persistence workflows
```

**Technology**: pytest with temporary file fixtures

**Example Tests**:
```python
def test_add_and_list_workflow(tmp_path):
    """Adding a todo makes it appear in list."""
    storage_file = tmp_path / "todos.json"

    # Add a todo
    add_todo("Buy groceries", storage_file)

    # List todos
    todos = list_todos(storage_file)

    assert len(todos) == 1
    assert todos[0].title == "Buy groceries"
    assert todos[0].done is False

def test_persistence_across_operations(tmp_path):
    """Todos persist across multiple operations."""
    storage_file = tmp_path / "todos.json"

    # Add two todos
    add_todo("Task 1", storage_file)
    add_todo("Task 2", storage_file)

    # Mark one done
    mark_done(1, storage_file)

    # Verify both persist with correct status
    todos = list_todos(storage_file)
    assert len(todos) == 2
    assert todos[0].done is True
    assert todos[1].done is False
```

**Coverage Requirement**: All major workflows covered

**Ownership**: Written by test authors or senior implementers

### Layer 4: Black Box Tests

**Purpose**: End-to-end validation from user's perspective with no knowledge of internals.

**Scope**:
- Complete user workflows
- CLI execution via subprocess
- Actual file system interaction
- Real-world usage scenarios

**Location**: `tests/blackbox/`

**Technology**: pytest with subprocess and temporary directories

**Example Tests**:
```python
def test_complete_todo_lifecycle(tmp_path):
    """User can add, list, and complete a todo."""
    os.chdir(tmp_path)

    # Add todo
    result = subprocess.run(
        ["todo", "add", "Buy groceries"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Added todo #1" in result.stdout

    # List todos
    result = subprocess.run(
        ["todo", "list"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "[ ] #1: Buy groceries" in result.stdout

    # Mark done
    result = subprocess.run(
        ["todo", "done", "1"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Marked todo #1 as done" in result.stdout

    # Verify completion
    result = subprocess.run(
        ["todo", "list"],
        capture_output=True,
        text=True
    )
    assert "[✓] #1: Buy groceries" in result.stdout

def test_error_handling_invalid_id(tmp_path):
    """User receives clear error for invalid todo ID."""
    os.chdir(tmp_path)

    result = subprocess.run(
        ["todo", "done", "999"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "Todo #999 not found" in result.stderr
```

**Coverage Requirement**: All user workflows from operational spec

**Ownership**: Written by test authors with user perspective

## Test Organization and Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                # Shared pytest fixtures
├── contracts/                 # Layer 1: Interface contracts
│   ├── __init__.py
│   └── test_cli_interface.py
├── unit/                      # Layer 2: Unit tests (TDD)
│   ├── __init__.py
│   ├── test_todo.py
│   ├── test_storage.py
│   └── test_cli.py
├── integration/               # Layer 3: Integration tests
│   ├── __init__.py
│   ├── test_add_workflow.py
│   ├── test_list_workflow.py
│   ├── test_done_workflow.py
│   └── test_persistence.py
└── blackbox/                  # Layer 4: Black box tests
    ├── __init__.py
    ├── test_user_workflows.py
    └── test_error_scenarios.py
```

### Shared Fixtures

Located in `tests/conftest.py`:

```python
import pytest
from pathlib import Path
from trivial_todo_app.storage import TodoStorage

@pytest.fixture
def tmp_storage(tmp_path):
    """Provide temporary storage for testing."""
    storage_file = tmp_path / "todos.json"
    return TodoStorage(storage_file)

@pytest.fixture
def sample_todos():
    """Provide sample todo data for testing."""
    return [
        Todo(id=1, title="Buy groceries", done=False),
        Todo(id=2, title="Walk dog", done=True),
        Todo(id=3, title="Read book", done=False),
    ]

@pytest.fixture
def clean_env(tmp_path, monkeypatch):
    """Provide clean environment for black box tests."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
```

### Naming Conventions

**Test Files**: `test_<component>.py`

**Test Functions**: `test_<behavior_being_tested>`

**Examples**:
- `test_add_creates_todo()`
- `test_list_shows_all_todos()`
- `test_done_marks_complete()`
- `test_storage_handles_missing_file()`

**Descriptive Names**: Test names should clearly describe what is being tested

## Coverage Requirements

### Overall Target

- **Minimum**: 90% code coverage across all modules
- **Goal**: 95%+ code coverage
- **Measurement**: pytest-cov

### Per-Component Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| cli.py | 90% | 95% |
| todo.py | 95% | 100% |
| storage.py | 90% | 95% |

### Coverage Exclusions

Acceptable exclusions from coverage:
- Defensive code for "impossible" states
- Debug logging statements
- Type checking blocks (`if TYPE_CHECKING:`)

### Coverage Validation

```bash
# Run tests with coverage report
pytest tests/ --cov=src/trivial_todo_app --cov-report=term-missing

# Fail if coverage below threshold
pytest tests/ --cov=src/trivial_todo_app --cov-fail-under=90
```

## Test-Driven Development Workflow

### TDD Cycle

The TDD workflow follows the Red-Green-Refactor cycle:

```
┌─────────────────────────────────────────┐
│  1. RED: Write failing test            │
│     Test author creates test            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  2. Implementer runs test (fails)       │
│     Verify test actually fails          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  3. GREEN: Write minimal code           │
│     Make test pass, nothing more        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  4. Run test (passes)                   │
│     Verify implementation works         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  5. REFACTOR: Improve code              │
│     Clean up while keeping tests green  │
└──────────────┬──────────────────────────┘
               │
               └──────> Repeat for next test
```

### TDD Best Practices

**1. One Test at a Time**
- Implement one test before writing the next
- Don't write multiple failing tests

**2. Minimal Implementation**
- Write only enough code to pass the current test
- Resist the urge to implement features not yet tested

**3. Refactor with Confidence**
- Green tests provide safety net for refactoring
- Improve code structure without changing behavior

**4. Test Behaviors, Not Implementation**
- Tests should verify what code does, not how
- Allow implementation flexibility

### Example TDD Session

```python
# 1. Test author writes: tests/unit/test_storage.py
def test_load_returns_empty_list_for_new_file(tmp_path):
    """Load returns empty list when file doesn't exist."""
    storage = TodoStorage(tmp_path / "todos.json")
    todos = storage.load()
    assert todos == []

# 2. Implementer runs test → FAILS (not implemented)

# 3. Implementer writes minimal code in storage.py
def load(self) -> list[Todo]:
    if not self.storage_path.exists():
        return []
    # Will add JSON loading later

# 4. Implementer runs test → PASSES

# 5. Next test by test author
def test_load_parses_json_file(tmp_path):
    """Load parses todos from JSON file."""
    storage_path = tmp_path / "todos.json"
    storage_path.write_text('[{"id":1,"title":"Test","done":false}]')

    storage = TodoStorage(storage_path)
    todos = storage.load()

    assert len(todos) == 1
    assert todos[0].id == 1
    assert todos[0].title == "Test"

# 6. Implementer adds JSON parsing...
```

## Test Arbitration Process

When implementers believe a test is incorrect or poorly written, an arbitration process ensures quality.

### When to Request Arbitration

Implementers may request arbitration when:
- Test requirements contradict specification
- Test is testing implementation details, not behavior
- Test is flaky or non-deterministic
- Test has incorrect assertions
- Test is impossible to satisfy

### Arbitration Workflow

```
1. Implementer identifies issue with test
   ↓
2. Implementer documents concern:
   - Which test is problematic
   - Why it's incorrect
   - Proposed fix (if applicable)
   ↓
3. Test author reviews concern
   ↓
4. Discussion and resolution:
   - Author fixes test (if implementer is correct)
   - Author explains test (if implementer misunderstood)
   - Escalate to senior developer (if disagreement)
   ↓
5. Final decision implemented
```

### Arbitration Documentation

Document arbitration decisions in `docs/test-arbitration.md`:

```markdown
## Arbitration #1 - test_add_validates_title

**Date**: 2026-02-02
**Test**: tests/unit/test_cli.py::test_add_validates_title
**Issue**: Test required exception, spec says error message
**Resolution**: Modified test to check error message on stderr
**Author**: test-author-name
**Implementer**: implementer-name
```

### Escalation Path

1. **Level 1**: Implementer ↔ Test Author (direct discussion)
2. **Level 2**: Senior Developer review (if no agreement)
3. **Level 3**: Technical Lead decision (final authority)

## Access Restrictions

### Test Code Visibility

**Implementers cannot view test implementation code** while working on features.

**Allowed Access**:
- Test failure messages and output
- Test names and descriptions
- Fixture documentation
- This testing strategy document

**Restricted Access**:
- Test source code (`tests/` directory)
- Test implementation details
- Expected values in assertions

### Rationale

- Ensures tests truly validate behavior, not just implementation
- Prevents "teaching to the test"
- Simulates real-world TDD where tests come first
- Forces implementers to think about design, not just passing tests

### Enforcement

- Tests written in separate branch/repository
- Implementers work from test reports, not source
- Code review ensures no test peeking occurred

### Exception Cases

**Integration and Black Box tests**: May be visible to implementers after unit tests pass, to aid in understanding full workflows.

**Contract tests**: Visible to all, as they define the public interface.

## Running Tests

### Run All Tests

```bash
# Via quality gate script (recommended)
./scripts/check.sh

# Direct pytest
pytest tests/
```

### Run Specific Test Layer

```bash
# Layer 1: Interface contracts
pytest tests/contracts/

# Layer 2: Unit tests
pytest tests/unit/

# Layer 3: Integration tests
pytest tests/integration/

# Layer 4: Black box tests
pytest tests/blackbox/
```

### Run with Coverage

```bash
# Coverage report
pytest tests/ --cov=src/trivial_todo_app --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=src/trivial_todo_app --cov-report=html

# Fail if coverage below 90%
pytest tests/ --cov=src/trivial_todo_app --cov-fail-under=90
```

### Run Specific Test

```bash
# By name
pytest tests/unit/test_todo.py::test_todo_creation

# By pattern
pytest tests/ -k "test_add"

# Verbose output
pytest tests/ -v
```

### Watch Mode (Development)

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw tests/ src/
```

## Continuous Integration

### Local CI (Pre-commit)

Developers run before committing:

```bash
./scripts/check.sh
```

This ensures:
- All tests pass
- Code coverage meets threshold
- Type checking passes
- Linting passes
- Formatting is correct

### No Remote CI

This project uses **local-only CI**:
- No GitHub Actions
- No Travis CI
- No CircleCI

**Rationale**: Simplicity for demonstration project

**Enforcement**: Trust and code review

## Test Maintenance

### When to Update Tests

Tests should be updated when:
- Specification changes (update contract tests first)
- Bugs found (add regression test)
- Refactoring reveals test gaps
- Coverage drops below threshold

### Test Code Quality

Tests must meet same quality standards as production code:
- Clear, descriptive names
- Well-organized and DRY
- Properly documented
- Type-hinted
- Linted and formatted

### Test Performance

- Unit tests: < 10ms per test
- Integration tests: < 100ms per test
- Black box tests: < 500ms per test
- Full suite: < 5 seconds

Slow tests should be optimized or moved to appropriate layer.

## Testing Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```python
# BAD: Testing internal structure
def test_storage_uses_dict_internally():
    storage = TodoStorage()
    assert isinstance(storage._todos_cache, dict)

# GOOD: Testing behavior
def test_storage_persists_todos():
    storage.save([Todo(1, "Test", False)])
    loaded = storage.load()
    assert len(loaded) == 1
```

### ❌ Overly Specific Mocking

```python
# BAD: Mocking everything
def test_add_command(mocker):
    mocker.patch('storage.load', return_value=[])
    mocker.patch('storage.save')
    mocker.patch('typer.echo')
    add("Test")
    # What are we actually testing?

# GOOD: Test real behavior
def test_add_command(tmp_storage):
    add("Test", storage=tmp_storage)
    todos = tmp_storage.load()
    assert len(todos) == 1
```

### ❌ Test Interdependence

```python
# BAD: Tests depend on execution order
def test_1_add_todo():
    add("Test")

def test_2_list_shows_todo():
    todos = list_todos()
    assert len(todos) == 1  # Depends on test_1!

# GOOD: Independent tests
def test_list_shows_added_todo():
    add("Test")
    todos = list_todos()
    assert len(todos) == 1
```

### ❌ Unclear Test Names

```python
# BAD: Vague names
def test_add():
    ...

def test_list_1():
    ...

# GOOD: Descriptive names
def test_add_creates_todo_with_next_id():
    ...

def test_list_shows_todos_sorted_by_id():
    ...
```

## Summary

This testing strategy ensures the Trivial Todo App is:
- **Correct**: Comprehensive test coverage catches bugs
- **Reliable**: Four-layer approach validates all aspects
- **Maintainable**: TDD workflow ensures clean design
- **Specified**: Contract tests define exact behavior

**Key Principles**:
1. Test-first development (TDD)
2. Four complementary test layers
3. 90%+ coverage requirement
4. Clear test ownership and arbitration
5. Access restrictions for integrity
6. Fast feedback loops

By following this strategy, implementers can confidently build features knowing that comprehensive tests will validate correctness at every level.
