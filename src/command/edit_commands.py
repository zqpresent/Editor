"""
Edit Commands - Concrete commands for text editing operations.
All these commands support undo/redo through the Command pattern.
"""

from typing import TYPE_CHECKING
from .command import EditCommand
from ..utils.exceptions import (
    LineOutOfRangeException,
    ColumnOutOfRangeException,
    DeleteLengthExceedsLineException,
    EmptyFileInsertException
)

if TYPE_CHECKING:
    from ..editor.text_editor import TextEditor


class AppendCommand(EditCommand):
    """Command to append a line at the end of the file."""
    
    def __init__(self, editor: 'TextEditor', text: str):
        super().__init__(editor)
        self.text = text
        self.line_number = None  # Will be set during execute
    
    def execute(self) -> None:
        """Append text to the end of the file."""
        self.editor.content.append(self.text)
        self.line_number = len(self.editor.content)
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Remove the appended line."""
        if self.line_number and len(self.editor.content) >= self.line_number:
            self.editor.content.pop()
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'append "{self.text}"'


class InsertCommand(EditCommand):
    """Command to insert text at a specific position."""
    
    def __init__(self, editor: 'TextEditor', line: int, col: int, text: str):
        super().__init__(editor)
        self.line = line  # 1-based
        self.col = col    # 1-based
        self.text = text
        self.old_lines = []  # Store original lines for undo
        self.affected_line_count = 0
    
    def execute(self) -> None:
        """Insert text at the specified position."""
        # Validate position
        if not self.editor.content:
            # Empty file - can only insert at 1:1
            if self.line != 1 or self.col != 1:
                raise EmptyFileInsertException("空文件只能在1:1位置插入")
            self.editor.content.append("")
        
        if self.line < 1 or self.line > len(self.editor.content):
            raise LineOutOfRangeException(f"行号越界: {self.line}")
        
        line_idx = self.line - 1
        current_line = self.editor.content[line_idx]
        
        if self.col < 1 or self.col > len(current_line) + 1:
            raise ColumnOutOfRangeException(f"列号越界: {self.col}")
        
        col_idx = self.col - 1
        
        # Handle multi-line insertion
        if '\n' in self.text:
            lines_to_insert = self.text.split('\n')
            
            # Store old lines for undo
            self.old_lines = [current_line]
            
            # First line: insert before col_idx, append first part of insert
            new_first_line = current_line[:col_idx] + lines_to_insert[0]
            
            # Middle lines: full lines from the split
            middle_lines = lines_to_insert[1:-1]
            
            # Last line: append last part of insert, then rest of original line
            new_last_line = lines_to_insert[-1] + current_line[col_idx:]
            
            # Replace the current line and insert new lines
            self.editor.content[line_idx] = new_first_line
            for i, line in enumerate(middle_lines + [new_last_line], start=1):
                self.editor.content.insert(line_idx + i, line)
            
            self.affected_line_count = len(lines_to_insert)
        else:
            # Single line insertion
            self.old_lines = [current_line]
            new_line = current_line[:col_idx] + self.text + current_line[col_idx:]
            self.editor.content[line_idx] = new_line
            self.affected_line_count = 1
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Undo the insertion."""
        if not self.old_lines:
            return
        
        line_idx = self.line - 1
        
        if '\n' in self.text:
            # Remove inserted lines
            lines_inserted = len(self.text.split('\n'))
            for _ in range(lines_inserted - 1):
                if line_idx + 1 < len(self.editor.content):
                    self.editor.content.pop(line_idx + 1)
        
        # Restore original line
        if line_idx < len(self.editor.content):
            self.editor.content[line_idx] = self.old_lines[0]
        
        self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'insert {self.line}:{self.col} "{self.text}"'


class DeleteCommand(EditCommand):
    """Command to delete characters from a specific position."""
    
    def __init__(self, editor: 'TextEditor', line: int, col: int, length: int):
        super().__init__(editor)
        self.line = line
        self.col = col
        self.length = length
        self.deleted_text = ""
    
    def execute(self) -> None:
        """Delete characters starting from the specified position."""
        if self.line < 1 or self.line > len(self.editor.content):
            raise LineOutOfRangeException(f"行号越界: {self.line}")
        
        line_idx = self.line - 1
        current_line = self.editor.content[line_idx]
        
        if self.col < 1 or self.col > len(current_line):
            raise ColumnOutOfRangeException(f"列号越界: {self.col}")
        
        col_idx = self.col - 1
        
        # Check if deletion length is valid
        remaining = len(current_line) - col_idx
        if self.length > remaining:
            raise DeleteLengthExceedsLineException(f"删除长度超出行尾: 剩余{remaining}个字符，尝试删除{self.length}个")
        
        # Perform deletion
        self.deleted_text = current_line[col_idx:col_idx + self.length]
        new_line = current_line[:col_idx] + current_line[col_idx + self.length:]
        self.editor.content[line_idx] = new_line
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Undo the deletion by inserting back the deleted text."""
        if not self.deleted_text:
            return
        
        line_idx = self.line - 1
        col_idx = self.col - 1
        
        if line_idx < len(self.editor.content):
            current_line = self.editor.content[line_idx]
            new_line = current_line[:col_idx] + self.deleted_text + current_line[col_idx:]
            self.editor.content[line_idx] = new_line
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'delete {self.line}:{self.col} {self.length}'


class ReplaceCommand(EditCommand):
    """Command to replace characters with new text."""
    
    def __init__(self, editor: 'TextEditor', line: int, col: int, length: int, text: str):
        super().__init__(editor)
        self.line = line
        self.col = col
        self.length = length
        self.text = text
        self.old_text = ""
    
    def execute(self) -> None:
        """Replace characters at the specified position."""
        if self.line < 1 or self.line > len(self.editor.content):
            raise LineOutOfRangeException(f"行号越界: {self.line}")
        
        line_idx = self.line - 1
        current_line = self.editor.content[line_idx]
        
        if self.col < 1 or self.col > len(current_line):
            raise ColumnOutOfRangeException(f"列号越界: {self.col}")
        
        col_idx = self.col - 1
        
        # Check if replacement length is valid
        remaining = len(current_line) - col_idx
        if self.length > remaining:
            raise DeleteLengthExceedsLineException(f"替换长度超出行尾: 剩余{remaining}个字符，尝试替换{self.length}个")
        
        # Perform replacement
        self.old_text = current_line[col_idx:col_idx + self.length]
        new_line = current_line[:col_idx] + self.text + current_line[col_idx + self.length:]
        self.editor.content[line_idx] = new_line
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Undo the replacement."""
        if self.old_text is None:
            return
        
        line_idx = self.line - 1
        col_idx = self.col - 1
        
        if line_idx < len(self.editor.content):
            current_line = self.editor.content[line_idx]
            # Remove the inserted text and restore old text
            text_end = col_idx + len(self.text)
            new_line = current_line[:col_idx] + self.old_text + current_line[text_end:]
            self.editor.content[line_idx] = new_line
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'replace {self.line}:{self.col} {self.length} "{self.text}"'

