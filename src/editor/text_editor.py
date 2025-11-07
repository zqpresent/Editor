"""
Text Editor implementation.
Stores content as a list of lines and provides text editing operations.
"""

import os
from typing import List, Optional
from .editor import Editor
from ..command.edit_commands import AppendCommand, InsertCommand, DeleteCommand, ReplaceCommand
from ..utils.exceptions import LineOutOfRangeException


class TextEditor(Editor):
    """
    Text editor that stores content as a list of lines.
    Each line is a string, and lines are joined with newlines when saving.
    """
    
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.content: List[str] = []
    
    def load_from_file(self, filepath: str) -> None:
        """Load content from a text file."""
        self.filepath = filepath
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        # Split by newlines, preserving empty lines
                        self.content = content.splitlines()
                    else:
                        self.content = []
                self.modified = False
            except Exception as e:
                raise IOError(f"无法读取文件 {filepath}: {str(e)}")
        else:
            # File doesn't exist, create empty buffer
            self.content = []
            self.modified = True
    
    def save_to_file(self, filepath: Optional[str] = None) -> None:
        """Save content to a text file."""
        target_path = filepath if filepath else self.filepath
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(target_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.content))
            
            self.filepath = target_path
            self.modified = False
        except Exception as e:
            raise IOError(f"无法保存文件 {target_path}: {str(e)}")
    
    def get_content_string(self) -> str:
        """Get the entire content as a string."""
        return '\n'.join(self.content)
    
    # Text editing operations using Command pattern
    
    def append(self, text: str) -> None:
        """Append a line at the end."""
        command = AppendCommand(self, text)
        self.execute_command(command)
    
    def insert(self, line: int, col: int, text: str) -> None:
        """Insert text at the specified position."""
        command = InsertCommand(self, line, col, text)
        self.execute_command(command)
    
    def delete(self, line: int, col: int, length: int) -> None:
        """Delete characters starting from the specified position."""
        command = DeleteCommand(self, line, col, length)
        self.execute_command(command)
    
    def replace(self, line: int, col: int, length: int, text: str) -> None:
        """Replace characters with new text."""
        command = ReplaceCommand(self, line, col, length, text)
        self.execute_command(command)
    
    def show(self, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """
        Display content within the specified line range.
        Returns formatted string with line numbers.
        """
        if not self.content:
            return ""
        
        # Default to show all lines
        if start_line is None:
            start_line = 1
        if end_line is None:
            end_line = len(self.content)
        
        # Validate range
        if start_line < 1 or start_line > len(self.content):
            raise LineOutOfRangeException(f"起始行号越界: {start_line}")
        if end_line < 1 or end_line > len(self.content):
            raise LineOutOfRangeException(f"结束行号越界: {end_line}")
        if start_line > end_line:
            raise LineOutOfRangeException(f"起始行号不能大于结束行号")
        
        # Build output
        result = []
        for i in range(start_line - 1, end_line):
            result.append(f"{i + 1}: {self.content[i]}")
        
        return '\n'.join(result)
    
    def check_log_enabled(self) -> bool:
        """Check if the first line is '# log' to enable logging."""
        return len(self.content) > 0 and self.content[0].strip() == "# log"

