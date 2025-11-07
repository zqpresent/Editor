"""
File management utilities.
Provides directory tree display and other file operations.
"""

import os
from typing import List, Tuple


class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def generate_tree(path: str = '.', prefix: str = '', is_last: bool = True) -> List[str]:
        """
        Generate a tree structure for a directory.
        
        Args:
            path: Directory path to generate tree for
            prefix: Prefix for current line (for nested structure)
            is_last: Whether this is the last item in current level
            
        Returns:
            List of strings representing the tree structure
        """
        lines = []
        
        # Validate path
        if not os.path.exists(path):
            return [f"路径不存在: {path}"]
        
        if not os.path.isdir(path):
            return [f"不是目录: {path}"]
        
        try:
            # Get all items in directory (excluding hidden files)
            items = []
            for item in os.listdir(path):
                if not item.startswith('.'):
                    item_path = os.path.join(path, item)
                    items.append((item, os.path.isdir(item_path)))
            
            # Sort: directories first, then files, alphabetically
            items.sort(key=lambda x: (not x[1], x[0]))
            
            for i, (item, is_dir) in enumerate(items):
                is_last_item = (i == len(items) - 1)
                item_path = os.path.join(path, item)
                
                # Determine the connector
                if is_last_item:
                    connector = "└── "
                    new_prefix = prefix + "    "
                else:
                    connector = "├── "
                    new_prefix = prefix + "│   "
                
                lines.append(f"{prefix}{connector}{item}")
                
                # Recursively process directories
                if is_dir:
                    subdir_lines = FileManager.generate_tree(
                        item_path, 
                        new_prefix, 
                        is_last_item
                    )
                    lines.extend(subdir_lines)
            
            return lines
        except PermissionError:
            return [f"{prefix}[权限被拒绝]"]
        except Exception as e:
            return [f"{prefix}[错误: {str(e)}]"]
    
    @staticmethod
    def display_tree(path: str = '.') -> str:
        """
        Display directory tree as a formatted string.
        
        Args:
            path: Directory path
            
        Returns:
            Formatted tree structure string
        """
        if not path or path == '.':
            path = os.getcwd()
        
        # Get absolute path for display
        abs_path = os.path.abspath(path)
        
        # Show root directory name
        lines = [os.path.basename(abs_path) if os.path.basename(abs_path) else abs_path]
        lines.extend(FileManager.generate_tree(path))
        
        return '\n'.join(lines)

