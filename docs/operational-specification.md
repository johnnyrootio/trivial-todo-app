# Operational Specification

**Project**: Trivial Todo App
**Version**: 1.0
**Last Updated**: 2026-02-02

## System Overview

The Trivial Todo App is a minimal command-line application for managing todo items. It provides three core operations: adding todos, listing todos, and marking todos as done. The application uses simple JSON file persistence and follows a clean layered architecture.

### Design Principles

- **Simplicity**: Minimal feature set with no unnecessary complexity
- **Clarity**: Clear separation of concerns across layers
- **Reliability**: Robust error handling and data persistence
- **Testability**: Designed for comprehensive automated testing

### Architecture

The application follows a three-layer architecture:

```
┌─────────────────────────────────────┐
│         CLI Layer (cli.py)          │
│   Typer-based command interface     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│      Domain Layer (todo.py)         │
│    Core Todo data model             │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Storage Layer (storage.py)       │
│    JSON file persistence            │
└─────────────────────────────────────┘
```

**Data Flow**: User Input → CLI → Domain Model → Storage → JSON File

## Command Specifications

### `todo add <title>`

Adds a new todo item with the specified title.

**Syntax**:
```bash
todo add "<title>"
```

**Parameters**:
- `title` (string, required): The title of the todo item

**Behavior**:
1. Load existing todos from storage
2. Generate next sequential ID (max existing ID + 1, or 1 if empty)
3. Create new Todo object with generated ID, provided title, and done=False
4. Append new todo to the list
5. Save updated list to storage
6. Display confirmation message with the new todo's ID

**Success Output**:
```
Added todo #<id>: "<title>"
```

**Error Conditions**:
- Empty title: Display error "Title cannot be empty"
- Storage write failure: Display error "Failed to save todo: <reason>"

**Example**:
```bash
$ todo add "Buy groceries"
Added todo #1: "Buy groceries"
```

### `todo list`

Lists all todo items with their status.

**Syntax**:
```bash
todo list
```

**Parameters**: None

**Behavior**:
1. Load todos from storage
2. If empty, display "No todos found"
3. Otherwise, display each todo with ID, status, and title
4. Sort by ID ascending

**Output Format**:
```
[<status>] #<id>: <title>
```

Where `<status>` is:
- `✓` for completed todos (done=True)
- ` ` (space) for incomplete todos (done=False)

**Success Output** (with todos):
```
[ ] #1: Buy groceries
[✓] #2: Walk the dog
[ ] #3: Read a book
```

**Success Output** (empty):
```
No todos found
```

**Error Conditions**:
- Storage read failure: Display error "Failed to load todos: <reason>"

**Example**:
```bash
$ todo list
[ ] #1: Buy groceries
[ ] #2: Walk the dog
```

### `todo done <id>`

Marks a todo item as completed.

**Syntax**:
```bash
todo done <id>
```

**Parameters**:
- `id` (integer, required): The ID of the todo to mark as done

**Behavior**:
1. Load existing todos from storage
2. Find todo with matching ID
3. If not found, display error
4. If already done, display informational message
5. Set done=True for the todo
6. Save updated list to storage
7. Display confirmation message

**Success Output**:
```
Marked todo #<id> as done: "<title>"
```

**Already Done Output**:
```
Todo #<id> is already done
```

**Error Conditions**:
- Invalid ID format: Display error "Invalid todo ID: must be a positive integer"
- Todo not found: Display error "Todo #<id> not found"
- Storage write failure: Display error "Failed to save todo: <reason>"

**Example**:
```bash
$ todo done 1
Marked todo #1 as done: "Buy groceries"
```

### Common CLI Behavior

**Help Command**:
```bash
todo --help
```

Shows usage information for all commands.

**Exit Codes**:
- 0: Success
- 1: Error (invalid input, storage failure, etc.)

## Data Model

### Todo Object

The core domain entity representing a single todo item.

**Structure**:
```python
@dataclass
class Todo:
    id: int           # Unique identifier (positive integer)
    title: str        # Todo description
    done: bool        # Completion status (default: False)
```

**Constraints**:
- `id`: Must be unique, positive integer, auto-generated sequentially
- `title`: Non-empty string
- `done`: Boolean value (True = completed, False = pending)

**Invariants**:
- Once created, a todo's ID never changes
- Title cannot be modified (future enhancement)
- Done status can only transition from False → True (no uncomplete operation)

## Storage Specification

### File Format

Todos are persisted in a JSON file with the following structure:

**File**: `todos.json` (default location: current working directory)

**Format**:
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

**Schema**:
- Root: Array of todo objects
- Each object contains: `id` (number), `title` (string), `done` (boolean)
- Empty state: `[]` (empty array)

### Storage Behavior

**Initialization**:
- If `todos.json` doesn't exist, create it with empty array `[]` on first write
- If file exists but is empty or invalid, treat as empty array

**Concurrency**:
- Single-user, single-process only (no concurrent access handling)
- Last write wins (no file locking)

**Persistence**:
- Atomic writes (write to temp file, then rename)
- Full list replacement on every save (no partial updates)

**Error Handling**:
- Read failures: Propagate error to CLI layer
- Write failures: Propagate error to CLI layer
- Invalid JSON: Treat as empty array, log warning

## CLI Interface Specification

### Framework

Uses [Typer](https://typer.tiangolo.com/) for CLI construction.

**Entry Point**: `todo` command (installed via pip)

**Command Registration**:
- `add`: `@app.command()` decorated function
- `list`: `@app.command()` decorated function
- `done`: `@app.command()` decorated function

### User Experience

**Output Style**:
- Success messages: Plain text to stdout
- Error messages: Plain text to stderr
- No color output (simple terminal compatibility)
- No progress indicators (operations are fast)

**Input Validation**:
- Performed at CLI layer before calling domain logic
- Clear error messages for invalid input
- Fail fast on validation errors

## User Workflows

### Workflow 1: Add and Complete a Todo

```bash
# Start with empty list
$ todo list
No todos found

# Add a todo
$ todo add "Buy groceries"
Added todo #1: "Buy groceries"

# Verify it was added
$ todo list
[ ] #1: Buy groceries

# Mark it done
$ todo done 1
Marked todo #1 as done: "Buy groceries"

# Verify completion
$ todo list
[✓] #1: Buy groceries
```

### Workflow 2: Managing Multiple Todos

```bash
# Add several todos
$ todo add "Buy groceries"
Added todo #1: "Buy groceries"

$ todo add "Walk the dog"
Added todo #2: "Walk the dog"

$ todo add "Read a book"
Added todo #3: "Read a book"

# View all
$ todo list
[ ] #1: Buy groceries
[ ] #2: Walk the dog
[ ] #3: Read a book

# Complete some
$ todo done 1
Marked todo #1 as done: "Buy groceries"

$ todo done 3
Marked todo #3 as done: "Read a book"

# View updated list
$ todo list
[✓] #1: Buy groceries
[ ] #2: Walk the dog
[✓] #3: Read a book
```

### Workflow 3: Error Handling

```bash
# Try to complete non-existent todo
$ todo done 999
Todo #999 not found

# Try to complete already-done todo
$ todo done 1
Todo #1 is already done

# Try invalid ID
$ todo done abc
Invalid todo ID: must be a positive integer
```

## Error Handling Specifications

### Error Categories

**1. User Input Errors**
- Invalid command syntax
- Invalid todo ID (non-integer, negative, zero)
- Empty title
- Non-existent todo ID

**Response**: Display clear error message, exit code 1

**2. Storage Errors**
- File read permission denied
- File write permission denied
- Disk full
- Invalid JSON format

**Response**: Display error with specific reason, exit code 1

**3. System Errors**
- Unexpected exceptions
- Programming errors (should not occur in production)

**Response**: Display generic error message, exit code 1

### Error Message Format

All error messages follow this structure:

```
Error: <brief description>
```

Examples:
```
Error: Title cannot be empty
Error: Todo #5 not found
Error: Failed to save todo: Permission denied
```

### Error Recovery

**Graceful Degradation**:
- Storage read failure: Cannot proceed, inform user
- Storage write failure: Data loss, inform user immediately
- Invalid JSON: Treat as empty, warn user

**No Automatic Recovery**:
- Do not attempt to fix corrupted data
- Do not create backups automatically
- User must resolve file permission issues

### Validation Rules

**Title Validation**:
- Must not be empty string
- Must not be only whitespace
- No maximum length (practical limit: terminal width)

**ID Validation**:
- Must be positive integer
- Must exist in current todo list

**File Validation**:
- Must be valid JSON
- Must be array at root level
- Each element must have id, title, done fields
- Invalid data: treat as empty list

## Non-Functional Requirements

### Performance

- All operations complete in < 100ms for lists up to 1000 items
- No network dependencies
- No database dependencies
- Minimal memory footprint (< 10MB)

### Reliability

- Data persistence guaranteed on successful save
- Atomic file writes (no partial writes)
- Clear error messages for all failure modes

### Usability

- Commands follow standard CLI conventions
- Help text accessible via --help
- Minimal learning curve (< 5 minutes)

### Maintainability

- Clean separation of concerns
- Type hints throughout
- Comprehensive test coverage (90%+)
- Clear code structure

## Future Considerations

Items explicitly out of scope for v1.0:

- Edit/update todo titles
- Delete todos
- Uncomplete todos (mark as not done)
- Todo priorities or categories
- Due dates
- Multi-user support
- Cloud sync
- Web interface
- Mobile app

These may be considered for future versions but are not part of the current specification.
