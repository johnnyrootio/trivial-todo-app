# Trivial Todo App

A minimal todo application demonstrating the Overlord greenfield workflow. Supports add, list, and mark-done operations with simple JSON file persistence.

## Features

- ✅ **Add todos** - Create new todo items with a title
- ✅ **List todos** - View all todos with their status
- ✅ **Mark done** - Mark todos as completed

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/johnnyrootio/trivial-todo-app.git
cd trivial-todo-app
```

2. Install in development mode with dev dependencies:
```bash
pip install -e .[dev]
```

### Usage

Add a new todo:
```bash
todo add "Buy groceries"
```

List all todos:
```bash
todo list
```

Mark a todo as done:
```bash
todo done 1
```

Get help:
```bash
todo --help
```

### Running Quality Checks

The project uses a single quality gate script that runs all checks:

```bash
./scripts/check.sh
```

This runs:
- **Format check** - ruff format verification
- **Lint** - ruff linting
- **Type check** - mypy static type checking
- **Tests** - pytest with coverage

## Development

### Project Structure

```
trivial-todo-app/
├── src/
│   └── trivial_todo_app/
│       ├── __init__.py      # Package initialization
│       ├── cli.py           # CLI entry point (typer)
│       ├── todo.py          # Todo data model
│       └── storage.py       # JSON file storage
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── blackbox/            # End-to-end CLI tests
├── scripts/
│   └── check.sh             # Quality gate script
├── specs/                   # Phase 1 specifications
├── contracts/               # Interface contracts
├── docs/                    # Documentation
│   └── plans/               # Design documents
└── pyproject.toml           # Package configuration
```

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=src/trivial_todo_app --cov-report=term-missing
```

Run specific test categories:
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/blackbox/       # Black box tests only
```

### Type Checking

```bash
mypy src/
```

### Linting and Formatting

Check formatting:
```bash
ruff format --check src/ tests/
```

Auto-format code:
```bash
ruff format src/ tests/
```

Run linter:
```bash
ruff check src/ tests/
```

Auto-fix linting issues:
```bash
ruff check --fix src/ tests/
```

## Architecture

The application follows a simple layered architecture:

- **CLI Layer** (`cli.py`) - Typer-based command-line interface
- **Domain Layer** (`todo.py`) - Core Todo data model
- **Storage Layer** (`storage.py`) - JSON file persistence

Data flows: CLI → Domain Model → Storage → JSON File

Testing follows a four-layer strategy:
1. **Interface Contract Tests** - CLI interface behavior
2. **Unit Tests** - Individual component testing
3. **Integration Tests** - Component interaction testing
4. **Black Box Tests** - End-to-end operational testing

## License

MIT