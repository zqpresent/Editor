"""
Spell checker interface (Adapter pattern).
Defines the abstract interface for spell checking services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SpellCheckResult:
    """Result of spell checking a word."""
    word: str
    suggestions: List[str]
    line: Optional[int] = None
    col: Optional[int] = None
    element_id: Optional[str] = None


class ISpellChecker(ABC):
    """
    Abstract interface for spell checking services.
    Different spell checking libraries can be adapted to this interface.
    """
    
    @abstractmethod
    def check_word(self, word: str) -> Optional[SpellCheckResult]:
        """
        Check if a word is spelled correctly.
        
        Args:
            word: The word to check
            
        Returns:
            SpellCheckResult if word is misspelled, None otherwise
        """
        pass
    
    @abstractmethod
    def check_text(self, text: str) -> List[SpellCheckResult]:
        """
        Check all words in a text.
        
        Args:
            text: The text to check
            
        Returns:
            List of SpellCheckResult for misspelled words
        """
        pass

