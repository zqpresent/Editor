"""Custom exceptions for the text editor."""


class EditorException(Exception):
    """Base exception for all editor errors."""
    pass


class FileNotOpenedException(EditorException):
    """Raised when trying to operate on a file that is not opened."""
    pass


class LineOutOfRangeException(EditorException):
    """Raised when line number is out of valid range."""
    pass


class ColumnOutOfRangeException(EditorException):
    """Raised when column number is out of valid range."""
    pass


class DeleteLengthExceedsLineException(EditorException):
    """Raised when delete length exceeds remaining characters in line."""
    pass


class NoActiveEditorException(EditorException):
    """Raised when no editor is currently active."""
    pass


class EmptyFileInsertException(EditorException):
    """Raised when trying to insert at non-1:1 position in empty file."""
    pass


class CommandException(EditorException):
    """Raised when command execution fails."""
    pass

