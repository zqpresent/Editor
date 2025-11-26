"""Spell checker module using Adapter pattern."""

from .spell_checker_interface import ISpellChecker, SpellCheckResult
from .pyspellchecker_adapter import PySpellCheckerAdapter
from .mock_spell_checker import MockSpellChecker

__all__ = ['ISpellChecker', 'SpellCheckResult', 'PySpellCheckerAdapter', 'MockSpellChecker']

