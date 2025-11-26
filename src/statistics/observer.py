"""
Statistics Observer for tracking file editing time.
Uses Observer pattern to listen to file activation events.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..logger.observer import Observer


class StatisticsObserver(Observer):
    """
    Observer that tracks editing time for each file in current session.
    Time tracking starts when a file becomes active and stops when switching or closing.
    """
    
    def __init__(self):
        self.file_times: Dict[str, float] = {}  # filepath -> cumulative seconds
        self.active_file: Optional[str] = None
        self.start_time: Optional[datetime] = None
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle events from workspace.
        
        Events:
        - file_activated: Start timing for new active file
        - file_closed: Stop timing and reset time
        - workspace_exit: Stop timing for all files
        """
        try:
            if event_type == 'file_activated':
                filepath = data.get('filepath')
                if filepath:
                    self._stop_current_timing()
                    self._start_timing(filepath)
            
            elif event_type == 'file_closed':
                filepath = data.get('filepath')
                if filepath:
                    self._stop_current_timing()
                    # Reset time for closed file
                    if filepath in self.file_times:
                        del self.file_times[filepath]
            
            elif event_type == 'workspace_exit':
                self._stop_current_timing()
        
        except Exception as e:
            # Statistics failure should not break the program
            print(f"Warning: 统计模块错误: {str(e)}")
    
    def _start_timing(self, filepath: str) -> None:
        """Start timing for a file."""
        self.active_file = filepath
        self.start_time = datetime.now()
        
        # Initialize time if not exists
        if filepath not in self.file_times:
            self.file_times[filepath] = 0.0
    
    def _stop_current_timing(self) -> None:
        """Stop timing for current active file."""
        if self.active_file and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.file_times[self.active_file] += elapsed
            
            self.active_file = None
            self.start_time = None
    
    def get_time(self, filepath: str) -> float:
        """Get cumulative editing time for a file in seconds."""
        # Include current session if this is the active file
        time = self.file_times.get(filepath, 0.0)
        
        if filepath == self.active_file and self.start_time:
            time += (datetime.now() - self.start_time).total_seconds()
        
        return time
    
    def format_time(self, filepath: str) -> str:
        """Format editing time as human-readable string."""
        seconds = int(self.get_time(filepath))
        
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}小时{minutes}分钟"
            return f"{hours}小时"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            if hours > 0:
                return f"{days}天{hours}小时"
            return f"{days}天"

