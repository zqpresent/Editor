"""
Command parser for the text editor.
Parses user input and extracts command and arguments.
"""

import re
from typing import Optional, Tuple, List, Dict


class CommandParser:
    """Parser for command-line commands."""
    
    @staticmethod
    def parse(input_str: str) -> Tuple[str, List[str]]:
        """
        Parse a command string into command name and arguments.
        
        Handles:
        - Quoted strings (with spaces)
        - Line:col notation
        - Multiple arguments
        
        Returns:
            (command_name, [arg1, arg2, ...])
        """
        if not input_str or not input_str.strip():
            return ('', [])
        
        # Split while preserving quoted strings
        parts = CommandParser._split_with_quotes(input_str.strip())
        
        if not parts:
            return ('', [])
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return (command, args)
    
    @staticmethod
    def _split_with_quotes(text: str) -> List[str]:
        """
        Split string while preserving quoted parts.
        Handles both single and double quotes.
        """
        # Pattern: matches quoted strings or non-space sequences
        pattern = r'"([^"]*)"|\'([^\']*)\'|(\S+)'
        matches = re.findall(pattern, text)
        
        # Extract the matched group (one of the three will be non-empty)
        result = []
        for match in matches:
            # match is a tuple of (double_quoted, single_quoted, unquoted)
            value = match[0] or match[1] or match[2]
            result.append(value)
        
        return result
    
    @staticmethod
    def parse_position(pos_str: str) -> Optional[Tuple[int, int]]:
        """
        Parse line:col notation.
        
        Args:
            pos_str: String in format "line:col"
            
        Returns:
            (line, col) tuple or None if invalid
        """
        if ':' not in pos_str:
            return None
        
        parts = pos_str.split(':')
        if len(parts) != 2:
            return None
        
        try:
            line = int(parts[0])
            col = int(parts[1])
            return (line, col)
        except ValueError:
            return None
    
    @staticmethod
    def parse_range(range_str: str) -> Optional[Tuple[int, int]]:
        """
        Parse range notation for show command.
        
        Args:
            range_str: String in format "start:end"
            
        Returns:
            (start, end) tuple or None if invalid
        """
        return CommandParser.parse_position(range_str)
    
    @staticmethod
    def unescape_string(text: str) -> str:
        """
        Unescape special characters in string.
        Handles: \\n -> newline, \\t -> tab, etc.
        """
        # Replace escape sequences
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        text = text.replace('\\r', '\r')
        text = text.replace('\\"', '"')
        text = text.replace("\\'", "'")
        text = text.replace('\\\\', '\\')
        
        return text
    
    @staticmethod
    def parse_attributes(args: List[str], start_index: int) -> Dict[str, str]:
        """
        Parse attributes from arguments starting at given index.
        Format: key=value
        
        Args:
            args: List of arguments
            start_index: Index to start parsing from
            
        Returns:
            Dictionary of attributes {key: value}
        """
        attributes = {}
        
        for i in range(start_index, len(args)):
            arg = args[i]
            if '=' in arg:
                # Split on first '=' only
                key, value = arg.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip empty keys
                if key:
                    attributes[key] = value
        
        return attributes

