# Quickstart Guide

Get started with Trivial Todo App in 5 minutes.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

Check your Python version:
```bash
python --version  # or python3 --version
```

## Installation

1. Clone and navigate to the repository:
```bash
git clone https://github.com/johnnyrootio/trivial-todo-app.git
cd trivial-todo-app
```

2. Install the application:
```bash
pip install .
```

That's it! The `todo` command is now available.

## Your First Todos

Try these commands to get started:

```bash
# See your (empty) todo list
todo list

# Add your first todo
todo add "Buy groceries"

# Add a few more
todo add "Walk the dog"
todo add "Read a book"

# See all your todos
todo list

# Mark one as done
todo done 1

# See your progress
todo list
```

**Expected output:**
```
$ todo list
[ ] #1: Buy groceries
[ ] #2: Walk the dog
[ ] #3: Read a book

$ todo done 1
Marked todo #1 as done: "Buy groceries"

$ todo list
[✓] #1: Buy groceries
[ ] #2: Walk the dog
[ ] #3: Read a book
```

## Common Commands

| Command | What it does |
|---------|-------------|
| `todo add "text"` | Create a new todo |
| `todo list` | Show all todos |
| `todo done <id>` | Mark todo as complete |
| `todo --help` | Show help |

## If Something Goes Wrong

**Command not found?**
- Make sure pip installed correctly: `pip show trivial-todo-app`
- Try using `pip3` instead of `pip`
- Check that your Python scripts directory is in PATH

**"Todo #X not found"?**
- Run `todo list` to see available IDs
- Make sure you're using the correct number

**"Permission denied"?**
- Check you have write access to your current directory
- The app stores todos in `todos.json` in your working directory

**Need to start fresh?**
- Delete `todos.json` in your current directory (your todos will be lost)
- Run `todo list` to create a new empty list

## Where Todos Are Stored

Todos are saved in a `todos.json` file in your current working directory. Each directory has its own separate todo list.

## Learn More

- **Full documentation**: See [README.md](../README.md) for complete usage examples and troubleshooting
- **Technical details**: See [operational-specification.md](operational-specification.md) for the complete system specification
- **For developers**: The README includes sections on testing, development workflow, and architecture

## Quick Tips

- Always use quotes around your todo text: `todo add "My task"`
- Run `todo list` frequently to see what needs to be done
- Todo IDs are permanent - they don't change or get reused
- There's no undo for marking todos done (keep it simple!)

---

**Ready to be productive?** Start adding your todos and get things done! 🚀
