"""
Workspace module - Core coordinator for the text editor.
Manages multiple editors, current active editor, and global state.
Implements Observer pattern (Subject) and uses Memento for persistence.
"""

import os
from typing import Dict, Optional
from .editor.editor import Editor
from .editor.text_editor import TextEditor
from .logger.observer import Subject
from .logger.logger import Logger
from .storage.memento import WorkspaceMemento
from .utils.exceptions import (
    FileNotOpenedException,
    NoActiveEditorException
)


class Workspace(Subject):
    """
    Singleton workspace that manages all editors and global state.
    Acts as the central coordinator for all operations.
    """
    
    _instance = None
    WORKSPACE_STATE_FILE = ".workspace.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.editors: Dict[str, Editor] = {}
            self.active_editor: Optional[Editor] = None
            self.logger = Logger()
            self.attach(self.logger)
            self.initialized = True
    
    # File Management
    
    def load_file(self, filepath: str) -> str:
        """
        Load a file into the workspace.
        Creates a new editor if file not already open.
        The loaded file becomes the active editor.
        
        Returns: Status message
        """
        # Normalize path
        filepath = os.path.normpath(filepath)
        
        # Check if already open
        if filepath in self.editors:
            self.active_editor = self.editors[filepath]
            return f"文件已打开，切换到: {filepath}"
        
        # Create appropriate editor (currently only TextEditor)
        editor = TextEditor(filepath)
        
        try:
            editor.load_from_file(filepath)
            self.editors[filepath] = editor
            self.active_editor = editor
            
            # Check for auto-enable logging (# log)
            if isinstance(editor, TextEditor) and editor.check_log_enabled():
                self.logger.enable_logging(filepath)
                self.notify('file_loaded', {
                    'filepath': filepath,
                    'auto_enable': True
                })
                return f"Loaded: {filepath} (日志已自动启用)"
            else:
                self.notify('file_loaded', {
                    'filepath': filepath,
                    'auto_enable': False
                })
                
                if os.path.exists(filepath):
                    return f"Loaded: {filepath}"
                else:
                    return f"文件不存在，已创建新缓冲区: {filepath}"
        except Exception as e:
            return f"Error: 无法加载文件: {str(e)}"
    
    def save_file(self, target: Optional[str] = None) -> str:
        """
        Save file(s).
        
        Args:
            target: None (save active), 'all', or specific filepath
            
        Returns: Status message
        """
        if target == 'all':
            return self._save_all_files()
        elif target:
            return self._save_specific_file(target)
        else:
            return self._save_active_file()
    
    def _save_active_file(self) -> str:
        """Save the currently active file."""
        if not self.active_editor:
            return "Error: 没有活动文件"
        
        try:
            self.active_editor.save_to_file()
            filepath = self.active_editor.filepath
            self.notify('command_executed', {
                'filepath': filepath,
                'command': 'save'
            })
            return f"Saved: {filepath}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _save_specific_file(self, filepath: str) -> str:
        """Save a specific file."""
        filepath = os.path.normpath(filepath)
        
        if filepath not in self.editors:
            return f"Error: 文件未打开: {filepath}"
        
        try:
            self.editors[filepath].save_to_file()
            self.notify('command_executed', {
                'filepath': filepath,
                'command': f'save {filepath}'
            })
            return f"Saved: {filepath}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _save_all_files(self) -> str:
        """Save all open files."""
        if not self.editors:
            return "没有打开的文件"
        
        results = []
        for filepath, editor in self.editors.items():
            try:
                editor.save_to_file()
                results.append(f"Saved: {filepath}")
            except Exception as e:
                results.append(f"Error saving {filepath}: {str(e)}")
        
        if self.active_editor:
            self.notify('command_executed', {
                'filepath': self.active_editor.filepath,
                'command': 'save all'
            })
        
        return '\n'.join(results)
    
    def close_file(self, filepath: Optional[str] = None, force: bool = False) -> tuple[str, bool]:
        """
        Close a file.
        
        Args:
            filepath: File to close (None = active file)
            force: Skip save prompt
            
        Returns: (message, needs_save_prompt)
        """
        if filepath:
            filepath = os.path.normpath(filepath)
            if filepath not in self.editors:
                return (f"Error: 文件未打开: {filepath}", False)
            editor = self.editors[filepath]
        else:
            if not self.active_editor:
                return ("Error: 没有活动文件", False)
            editor = self.active_editor
            filepath = editor.filepath
        
        # Check if modified
        if editor.is_modified() and not force:
            return (filepath, True)  # Signal that save prompt is needed
        
        # Remove from editors
        del self.editors[filepath]
        
        # Update active editor
        if self.active_editor == editor:
            if self.editors:
                # Switch to another file
                self.active_editor = list(self.editors.values())[-1]
                new_active = self.active_editor.filepath
                msg = f"Closed: {filepath}\n已切换到: {new_active}"
            else:
                self.active_editor = None
                msg = f"Closed: {filepath}"
        else:
            msg = f"Closed: {filepath}"
        
        self.notify('command_executed', {
            'filepath': filepath,
            'command': f'close {filepath}' if filepath else 'close'
        })
        
        return (msg, False)
    
    def init_file(self, filepath: str, with_log: bool = False) -> str:
        """
        Initialize a new file buffer.
        
        Args:
            filepath: File path
            with_log: Whether to add '# log' as first line
            
        Returns: Status message
        """
        filepath = os.path.normpath(filepath)
        
        if filepath in self.editors:
            return f"Error: 文件已打开: {filepath}"
        
        # Create new editor
        editor = TextEditor(filepath)
        
        if with_log:
            editor.content = ["# log"]
            editor.mark_modified()
            self.logger.enable_logging(filepath)
        
        self.editors[filepath] = editor
        self.active_editor = editor
        
        log_msg = " (日志已启用)" if with_log else ""
        return f"已创建新缓冲区: {filepath}{log_msg}"
    
    def edit_file(self, filepath: str) -> str:
        """Switch to a different open file."""
        filepath = os.path.normpath(filepath)
        
        if filepath not in self.editors:
            return f"Error: 文件未打开: {filepath}"
        
        self.active_editor = self.editors[filepath]
        return f"已切换到: {filepath}"
    
    def get_editor_list(self) -> str:
        """Get formatted list of open files."""
        if not self.editors:
            return "没有打开的文件"
        
        lines = []
        for filepath, editor in self.editors.items():
            is_active = (editor == self.active_editor)
            is_modified = editor.is_modified()
            
            prefix = "> " if is_active else "  "
            suffix = "*" if is_modified else ""
            
            lines.append(f"{prefix}{filepath}{suffix}")
        
        return '\n'.join(lines)
    
    def get_modified_files(self) -> list[str]:
        """Get list of files with unsaved changes."""
        return [fp for fp, ed in self.editors.items() if ed.is_modified()]
    
    # Active Editor Operations
    
    def get_active_editor(self) -> Editor:
        """Get the active editor or raise exception."""
        if not self.active_editor:
            raise NoActiveEditorException("没有活动文件")
        return self.active_editor
    
    def execute_on_active(self, operation: str, *args, **kwargs):
        """Execute an operation on the active editor."""
        editor = self.get_active_editor()
        
        if not hasattr(editor, operation):
            raise AttributeError(f"编辑器不支持操作: {operation}")
        
        method = getattr(editor, operation)
        return method(*args, **kwargs)
    
    # Undo/Redo
    
    def undo(self) -> str:
        """Undo last operation on active editor."""
        if not self.active_editor:
            return "Error: 没有活动文件"
        
        result = self.active_editor.undo()
        if result:
            return f"Undo: {result}"
        else:
            return "没有可撤销的操作"
    
    def redo(self) -> str:
        """Redo last undone operation on active editor."""
        if not self.active_editor:
            return "Error: 没有活动文件"
        
        result = self.active_editor.redo()
        if result:
            return f"Redo: {result}"
        else:
            return "没有可重做的操作"
    
    # Logging Management
    
    def enable_log(self, filepath: Optional[str] = None) -> str:
        """Enable logging for a file."""
        if filepath:
            filepath = os.path.normpath(filepath)
            if filepath not in self.editors:
                return f"Error: 文件未打开: {filepath}"
        else:
            if not self.active_editor:
                return "Error: 没有活动文件"
            filepath = self.active_editor.filepath
        
        if self.logger.is_enabled(filepath):
            return f"日志已启用: {filepath}"
        
        self.logger.enable_logging(filepath)
        return f"已启用日志: {filepath}"
    
    def disable_log(self, filepath: Optional[str] = None) -> str:
        """Disable logging for a file."""
        if filepath:
            filepath = os.path.normpath(filepath)
        else:
            if not self.active_editor:
                return "Error: 没有活动文件"
            filepath = self.active_editor.filepath
        
        self.logger.disable_logging(filepath)
        return f"已关闭日志: {filepath}"
    
    def show_log(self, filepath: Optional[str] = None) -> str:
        """Show log for a file."""
        if filepath:
            filepath = os.path.normpath(filepath)
        else:
            if not self.active_editor:
                return "Error: 没有活动文件"
            filepath = self.active_editor.filepath
        
        return self.logger.show_log(filepath)
    
    # State Persistence (Memento Pattern)
    
    def save_state(self) -> None:
        """Save workspace state to disk."""
        memento = WorkspaceMemento()
        memento.open_files = list(self.editors.keys())
        memento.active_file = self.active_editor.filepath if self.active_editor else None
        memento.modified_files = set(self.get_modified_files())
        memento.log_enabled_files = self.logger.enabled_files.copy()
        
        memento.save_to_file(self.WORKSPACE_STATE_FILE)
    
    def restore_state(self) -> Optional[str]:
        """Restore workspace state from disk."""
        memento = WorkspaceMemento.load_from_file(self.WORKSPACE_STATE_FILE)
        
        if not memento or not memento.open_files:
            return None
        
        messages = []
        messages.append(f"恢复工作区状态: {len(memento.open_files)} 个文件")
        
        # Restore open files
        for filepath in memento.open_files:
            if os.path.exists(filepath):
                try:
                    self.load_file(filepath)
                except Exception as e:
                    messages.append(f"  无法加载 {filepath}: {str(e)}")
        
        # Restore active file
        if memento.active_file and memento.active_file in self.editors:
            self.active_editor = self.editors[memento.active_file]
            messages.append(f"活动文件: {memento.active_file}")
        
        # Restore logging state
        for filepath in memento.log_enabled_files:
            if filepath in self.editors:
                self.logger.enable_logging(filepath)
        
        return '\n'.join(messages)
    
    def log_command(self, command_str: str) -> None:
        """Log a command execution."""
        if self.active_editor:
            self.notify('command_executed', {
                'filepath': self.active_editor.filepath,
                'command': command_str
            })

