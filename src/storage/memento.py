"""
Memento Pattern implementation for workspace state persistence.
Saves and restores workspace state to/from JSON.
"""

import json
import os
from typing import List, Set, Optional


class WorkspaceMemento:
    """
    Memento that stores workspace state.
    State includes: open files, active file, modified files, log-enabled files.
    """
    
    def __init__(self):
        self.open_files: List[str] = []
        self.active_file: Optional[str] = None
        self.modified_files: Set[str] = set()
        self.log_enabled_files: Set[str] = set()
    
    def to_dict(self) -> dict:
        """Convert memento to dictionary for JSON serialization."""
        return {
            'open_files': self.open_files,
            'active_file': self.active_file,
            'modified_files': list(self.modified_files),
            'log_enabled_files': list(self.log_enabled_files)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkspaceMemento':
        """Create memento from dictionary."""
        memento = cls()
        memento.open_files = data.get('open_files', [])
        memento.active_file = data.get('active_file')
        memento.modified_files = set(data.get('modified_files', []))
        memento.log_enabled_files = set(data.get('log_enabled_files', []))
        return memento
    
    def save_to_file(self, filepath: str) -> None:
        """Save memento to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: 无法保存工作区状态: {str(e)}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['WorkspaceMemento']:
        """Load memento from JSON file."""
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Warning: 无法加载工作区状态: {str(e)}")
            return None

