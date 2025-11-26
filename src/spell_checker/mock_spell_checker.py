"""
Mock spell checker for testing without external dependencies.
"""

from typing import List, Optional
from .spell_checker_interface import ISpellChecker, SpellCheckResult


class MockSpellChecker(ISpellChecker):
    """
    Mock spell checker that uses a simple dictionary.
    Useful for testing without pyspellchecker dependency.
    """
    
    def __init__(self):
        # Simple dictionary of common misspellings
        self.known_errors = {
            'recieve': ['receive'],
            'occured': ['occurred'],
            'seperate': ['separate'],
            'definately': ['definitely'],
            'itallian': ['Italian'],
            'rowlling': ['Rowling'],
        }
    
    def check_word(self, word: str) -> Optional[SpellCheckResult]:
        """Check a single word."""
        word_lower = word.lower()
        
        if word_lower in self.known_errors:
            return SpellCheckResult(
                word=word,
                suggestions=self.known_errors[word_lower]
            )
        
        return None
    
    def check_text(self, text: str) -> List[SpellCheckResult]:
        """Check all words in text."""
        import re
        
        results = []
        words = re.findall(r'\b[A-Za-z]+\b', text)
        
        checked = set()
        for word in words:
            word_lower = word.lower()
            if word_lower not in checked:
                checked.add(word_lower)
                result = self.check_word(word)
                if result:
                    results.append(result)
        
        return results

