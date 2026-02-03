# Trivial Todo App

A minimal command-line todo application for managing your daily tasks. Simple, fast, and reliable - with no unnecessary complexity.

## Features

- ✅ **Add todos** - Create new todo items with a title
- ✅ **List todos** - View all todos with their completion status
- ✅ **Mark done** - Mark todos as completed
- 💾 **Simple storage** - All todos saved in a local JSON file
- 🚀 **Fast** - All operations complete in under 100ms

## Installation

### End Users

1. Clone the repository:
```bash
git clone https://github.com/johnnyrootio/trivial-todo-app.git
cd trivial-todo-app
```

2. Install the application:
```bash
pip install .
```

The `todo` command will now be available in your terminal.

### Developers

For development with all testing and quality tools:
```bash
pip install -e .[dev]
```

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## Usage

### Basic Commands

**Add a new todo:**
```bash
todo add "Buy groceries"
# Output: Added todo #1: "Buy groceries"
```

**List all todos:**
```bash
todo list
# Output:
# [ ] #1: Buy groceries
# [✓] #2: Walk the dog
```

**Mark a todo as done:**
```bash
todo done 1
# Output: Marked todo #1 as done: "Buy groceries"
```

**Get help:**
```bash
todo --help
```

### Example Workflows

**Getting started with your first todo:**
```bash
$ todo list
No todos found

$ todo add "Buy groceries"
Added todo #1: "Buy groceries"

$ todo list
[ ] #1: Buy groceries

$ todo done 1
Marked todo #1 as done: "Buy groceries"

$ todo list
[✓] #1: Buy groceries
```

**Managing multiple todos:**
```bash
$ todo add "Buy groceries"
Added todo #1: "Buy groceries"

$ todo add "Walk the dog"
Added todo #2: "Walk the dog"

$ todo add "Read a book"
Added todo #3: "Read a book"

$ todo list
[ ] #1: Buy groceries
[ ] #2: Walk the dog
[ ] #3: Read a book

$ todo done 1
Marked todo #1 as done: "Buy groceries"

$ todo done 3
Marked todo #3 as done: "Read a book"

$ todo list
[✓] #1: Buy groceries
[ ] #2: Walk the dog
[✓] #3: Read a book
```

## Troubleshooting

### Common Issues

**"Todo #X not found"**
- You're trying to mark a todo as done that doesn't exist
- Use `todo list` to see all available todo IDs
- Make sure you're using the correct ID number

**"Todo #X is already done"**
- The todo you're trying to mark as done is already completed
- This is informational only - no action needed
- Use `todo list` to see which todos are already complete (marked with ✓)

**"Invalid todo ID: must be a positive integer"**
- You entered an invalid ID (like text or a negative number)
- Todo IDs must be positive integers (1, 2, 3, etc.)
- Example: `todo done 1` ✓  `todo done abc` ✗

**"Title cannot be empty"**
- You tried to add a todo without a title
- Always provide a title in quotes: `todo add "Your task here"`

**"Failed to save todo: Permission denied"**
- The application can't write to the `todos.json` file
- Check file permissions in your current directory
- Make sure you have write access to the directory

**"Failed to load todos: ..."**
- The application can't read the `todos.json` file
- Check if the file exists and you have read permissions
- If the file is corrupted, you can delete it (data will be lost) and start fresh

### Storage Location

Todos are stored in a `todos.json` file in your current working directory. If you run `todo` commands from different directories, you'll have separate todo lists in each location.

### Data Format

The `todos.json` file uses a simple JSON format:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "done": false
  },
  {
    "id": 2,
    "title": "Walk the dog",
    "done": true
  }
]
```

If you need to manually edit or recover your todos, you can edit this file directly.

---

## For Developers

The following sections are for developers who want to contribute to or modify the application.

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

### Development Workflow

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