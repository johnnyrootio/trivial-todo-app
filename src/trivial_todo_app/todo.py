"""Todo data model."""

from dataclasses import dataclass


@dataclass
class Todo:
    """A todo item with title and done status."""

    id: int
    title: str
    done: bool = False
