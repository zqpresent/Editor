"""
Observer Pattern implementation for event notifications.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Observer(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Called when an event occurs.
        
        Args:
            event_type: Type of event (e.g., 'command_executed', 'file_loaded')
            data: Event data dictionary
        """
        pass


class Subject:
    """
    Subject that maintains a list of observers and notifies them of events.
    """
    
    def __init__(self):
        self._observers: list[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                # Log failures but don't interrupt normal flow
                print(f"Warning: Observer notification failed: {str(e)}")

