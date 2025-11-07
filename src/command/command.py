"""
Command Pattern - Base classes and interfaces.
Implements the Command pattern for undoable operations.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..editor.editor import Editor


class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """Redo the command (usually same as execute)."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of the command for logging."""
        pass


class EditCommand(Command):
    """
    Base class for commands that modify editor content.
    These commands support undo/redo functionality.
    """
    
    def __init__(self, editor: 'Editor'):
        self.editor = editor
    
    def redo(self) -> None:
        """Default redo behavior is to execute again."""
        self.execute()

