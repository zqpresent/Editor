"""
Logger implementation using Observer pattern.
Logs commands to .filename.log files.
"""

import os
from datetime import datetime
from typing import Dict, Any, Set
from .observer import Observer


class Logger(Observer):
    """
    Logger that observes workspace events and writes to log files.
    Each file has its own log file (.filename.log).
    """
    
    def __init__(self):
        self.enabled_files: Set[str] = set()
        self.log_files: Dict[str, str] = {}  # filepath -> log filepath
        self.session_started: Dict[str, bool] = {}  # Track if session start logged
    
    def enable_logging(self, filepath: str) -> None:
        """Enable logging for a specific file."""
        if filepath not in self.enabled_files:
            self.enabled_files.add(filepath)
            log_path = self._get_log_path(filepath)
            self.log_files[filepath] = log_path
            self._write_session_start(filepath)
    
    def disable_logging(self, filepath: str) -> None:
        """Disable logging for a specific file."""
        if filepath in self.enabled_files:
            self.enabled_files.discard(filepath)
    
    def is_enabled(self, filepath: str) -> bool:
        """Check if logging is enabled for a file."""
        return filepath in self.enabled_files
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle events from the workspace.
        
        Events:
        - command_executed: Log the command
        - file_loaded: Check for auto-enable (# log)
        """
        if event_type == 'command_executed':
            self._log_command(data)
        elif event_type == 'file_loaded':
            filepath = data.get('filepath')
            auto_enable = data.get('auto_enable', False)
            if auto_enable and filepath:
                self.enable_logging(filepath)
    
    def _get_log_path(self, filepath: str) -> str:
        """Get the log file path for a given file."""
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        log_filename = f".{filename}.log"
        return os.path.join(directory, log_filename) if directory else log_filename
    
    def _write_session_start(self, filepath: str) -> None:
        """Write session start marker to log file."""
        if filepath in self.session_started:
            return
        
        try:
            log_path = self.log_files.get(filepath)
            if not log_path:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d %H:%M:%S")
            
            # Append to existing log file
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"session start at {timestamp}\n")
            
            self.session_started[filepath] = True
        except Exception as e:
            print(f"Warning: 无法写入日志文件 {log_path}: {str(e)}")
    
    def _log_command(self, data: Dict[str, Any]) -> None:
        """Log a command execution."""
        filepath = data.get('filepath')
        command_str = data.get('command')
        
        if not filepath or not command_str:
            return
        
        if filepath not in self.enabled_files:
            return
        
        try:
            log_path = self.log_files.get(filepath)
            if not log_path:
                return
            
            # Ensure session start is written
            if filepath not in self.session_started:
                self._write_session_start(filepath)
            
            timestamp = datetime.now().strftime("%Y%m%d %H:%M:%S")
            log_entry = f"{timestamp} {command_str}\n"
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: 无法写入日志: {str(e)}")
    
    def show_log(self, filepath: str) -> str:
        """Read and return the log file content."""
        if filepath not in self.log_files:
            return f"未找到文件 {filepath} 的日志"
        
        log_path = self.log_files[filepath]
        
        if not os.path.exists(log_path):
            return f"日志文件不存在: {log_path}"
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"无法读取日志文件: {str(e)}"

