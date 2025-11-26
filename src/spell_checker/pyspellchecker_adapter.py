"""
Adapter for pyspellchecker library.
Isolates the third-party dependency.
"""

import re
from typing import List, Optional
from .spell_checker_interface import ISpellChecker, SpellCheckResult


class PySpellCheckerAdapter(ISpellChecker):
    """
    Adapter for pyspellchecker library.
    Handles the case where the library might not be installed.
    """
    
    def __init__(self):
        try:
            from spellchecker import SpellChecker
            self.checker = SpellChecker()
            self.available = True
        except ImportError:
            self.available = False
            print("Warning: pyspellchecker库未安装，拼写检查功能将不可用")
            print("安装方法: pip install pyspellchecker")
    
    def check_word(self, word: str) -> Optional[SpellCheckResult]:
        """Check a single word."""
        if not self.available:
            return None
        
        # Clean word (remove punctuation)
        clean_word = word.strip('.,!?;:()[]{}"\'-')
        if not clean_word or not clean_word.isalpha():
            return None
        
        # Check if misspelled
        if self.checker.unknown([clean_word]):
            suggestions = list(self.checker.candidates(clean_word) or [])[:3]
            return SpellCheckResult(word=clean_word, suggestions=suggestions)
        
        return None
    
    def check_text(self, text: str) -> List[SpellCheckResult]:
        """Check all words in text."""
        if not self.available:
            return []
        
        results = []
        
        # Split text into words
        words = re.findall(r'\b[A-Za-z]+\b', text)
        
        # Check each unique word
        checked = set()
        for word in words:
            word_lower = word.lower()
            if word_lower not in checked:
                checked.add(word_lower)
                result = self.check_word(word)
                if result:
                    results.append(result)
        
        return results

