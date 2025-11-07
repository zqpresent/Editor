"""
Abstract Editor base class.
This can be extended for different types of editors (Text, XML, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Editor(ABC):
    """
    Abstract base class for all editor types.
    Each editor manages its own content and undo/redo stacks.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.modified = False
        self.undo_stack: List = []
        self.redo_stack: List = []
    
    @abstractmethod
    def load_from_file(self, filepath: str) -> None:
        """Load content from a file."""
        pass
    
    @abstractmethod
    def save_to_file(self, filepath: Optional[str] = None) -> None:
        """Save content to a file."""
        pass
    
    @abstractmethod
    def get_content_string(self) -> str:
        """Get the entire content as a string."""
        pass
    
    def mark_modified(self) -> None:
        """Mark the editor as modified."""
        self.modified = True
    
    def clear_modified(self) -> None:
        """Clear the modified flag."""
        self.modified = False
    
    def is_modified(self) -> bool:
        """Check if the editor has unsaved changes."""
        return self.modified
    
    def execute_command(self, command) -> None:
        """
        Execute a command and add it to the undo stack.
        Clears the redo stack.
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
    
    def undo(self) -> Optional[str]:
        """
        Undo the last command.
        Returns the description of the undone command or None.
        """
        if not self.undo_stack:
            return None
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return command.get_description()
    
    def redo(self) -> Optional[str]:
        """
        Redo the last undone command.
        Returns the description of the redone command or None.
        """
        if not self.redo_stack:
            return None
        
        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        return command.get_description()

