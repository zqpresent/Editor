"""
XML Editor implementation.
Stores content as a tree structure and provides element-level editing operations.
Uses Composite pattern for XML tree representation.
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Set, Tuple
from .editor import Editor
from ..utils.exceptions import (
    EditorException,
    LineOutOfRangeException
)


class XMLElement:
    """
    Represents an XML element node (Composite pattern).
    Each element has a tag, attributes, text content, and children.
    """
    
    def __init__(self, tag: str, element_id: str, text: str = ""):
        self.tag = tag
        self.id = element_id
        self.attributes: Dict[str, str] = {'id': element_id}
        self.text = text.strip() if text else ""
        self.children: List['XMLElement'] = []
        self.parent: Optional['XMLElement'] = None
    
    def add_child(self, child: 'XMLElement') -> None:
        """Add a child element."""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'XMLElement') -> None:
        """Remove a child element."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def insert_child(self, index: int, child: 'XMLElement') -> None:
        """Insert a child at specific position."""
        child.parent = self
        self.children.insert(index, child)
    
    def get_child_index(self, child: 'XMLElement') -> int:
        """Get the index of a child element."""
        return self.children.index(child)


class XMLEditor(Editor):
    """
    XML editor that stores content as a tree structure.
    Provides element-level editing operations.
    """
    
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.root: Optional[XMLElement] = None
        self.id_map: Dict[str, XMLElement] = {}  # id -> element mapping
        self.has_log_line = False
        self.log_exclude_commands: Set[str] = set()
    
    def load_from_file(self, filepath: str) -> None:
        """Load and parse XML file."""
        self.filepath = filepath
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check for # log line
                content_start = 0
                if lines and lines[0].strip().startswith('# log'):
                    self.has_log_line = True
                    self._parse_log_config(lines[0])
                    content_start = 1
                
                # Parse XML content
                xml_content = ''.join(lines[content_start:])
                self._parse_xml(xml_content)
                self.modified = False
            except Exception as e:
                raise IOError(f"无法读取XML文件 {filepath}: {str(e)}")
        else:
            # Create empty XML structure
            self.root = XMLElement('root', 'root', '')
            self.id_map = {'root': self.root}
            self.modified = True
    
    def save_to_file(self, filepath: Optional[str] = None) -> None:
        """Save XML tree to file."""
        target_path = filepath if filepath else self.filepath
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(target_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                # Write # log line if exists
                if self.has_log_line:
                    log_line = '# log'
                    if self.log_exclude_commands:
                        for cmd in self.log_exclude_commands:
                            log_line += f' -e {cmd}'
                    f.write(log_line + '\n')
                
                # Write XML declaration
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                
                # Write XML tree
                if self.root:
                    f.write(self._serialize_element(self.root, 0))
            
            self.filepath = target_path
            self.modified = False
        except Exception as e:
            raise IOError(f"无法保存XML文件 {target_path}: {str(e)}")
    
    def get_content_string(self) -> str:
        """Get the entire content as a string."""
        result = []
        if self.has_log_line:
            log_line = '# log'
            if self.log_exclude_commands:
                for cmd in self.log_exclude_commands:
                    log_line += f' -e {cmd}'
            result.append(log_line)
        
        result.append('<?xml version="1.0" encoding="UTF-8"?>')
        if self.root:
            result.append(self._serialize_element(self.root, 0).rstrip())
        
        return '\n'.join(result)
    
    def _parse_log_config(self, line: str) -> None:
        """Parse # log configuration line."""
        parts = line.strip().split()
        i = 1
        while i < len(parts):
            if parts[i] == '-e' and i + 1 < len(parts):
                self.log_exclude_commands.add(parts[i + 1])
                i += 2
            else:
                i += 1
    
    def check_log_enabled(self) -> bool:
        """Check if logging is enabled."""
        return self.has_log_line
    
    def parse_log_config(self) -> Tuple[bool, Set[str]]:
        """Get log configuration."""
        return (self.has_log_line, self.log_exclude_commands)
    
    def _parse_xml(self, xml_content: str) -> None:
        """Parse XML string into tree structure."""
        try:
            tree = ET.fromstring(xml_content)
            self.root = self._build_element_tree(tree)
            self._build_id_map(self.root)
        except ET.ParseError as e:
            raise EditorException(f"XML解析错误: {str(e)}")
    
    def _build_element_tree(self, et_elem: ET.Element) -> XMLElement:
        """Convert ElementTree element to XMLElement."""
        elem_id = et_elem.get('id', '')
        if not elem_id:
            raise EditorException(f"元素 <{et_elem.tag}> 缺少id属性")
        
        element = XMLElement(et_elem.tag, elem_id, et_elem.text or "")
        
        # Copy all attributes
        for key, value in et_elem.attrib.items():
            element.attributes[key] = value
        
        # Process children
        for child in et_elem:
            child_element = self._build_element_tree(child)
            element.add_child(child_element)
        
        return element
    
    def _build_id_map(self, element: XMLElement) -> None:
        """Build id -> element mapping."""
        self.id_map = {}
        self._add_to_id_map(element)
    
    def _add_to_id_map(self, element: XMLElement) -> None:
        """Recursively add elements to id map."""
        if element.id in self.id_map:
            raise EditorException(f"重复的元素ID: {element.id}")
        self.id_map[element.id] = element
        for child in element.children:
            self._add_to_id_map(child)
    
    def _serialize_element(self, element: XMLElement, indent_level: int) -> str:
        """Serialize element to XML string."""
        indent = '    ' * indent_level
        
        # Build attributes string
        attrs = ' '.join(f'{k}="{v}"' for k, v in element.attributes.items())
        
        # Opening tag
        result = f"{indent}<{element.tag} {attrs}>"
        
        # Text content
        if element.text:
            result += element.text
        
        # Children
        if element.children:
            result += '\n'
            for child in element.children:
                result += self._serialize_element(child, indent_level + 1)
            result += indent
        
        # Closing tag
        result += f"</{element.tag}>\n"
        
        return result
    
    def show_tree(self) -> str:
        """Display XML tree structure."""
        if not self.root:
            return "(空XML)"
        
        return self._format_tree_node(self.root, "", True)
    
    def _format_tree_node(self, element: XMLElement, prefix: str, is_last: bool) -> str:
        """Format a tree node with proper tree characters."""
        result = []
        
        # Current node
        node_prefix = "└── " if is_last else "├── "
        
        # Format attributes
        attrs = ', '.join(f'{k}="{v}"' for k, v in element.attributes.items())
        result.append(f"{prefix}{node_prefix}{element.tag} [{attrs}]")
        
        # Text content
        if element.text:
            text_prefix = prefix + ("    " if is_last else "│   ")
            result.append(f'{text_prefix}└── "{element.text}"')
        
        # Children
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(element.children):
            is_last_child = (i == len(element.children) - 1)
            result.append(self._format_tree_node(child, child_prefix, is_last_child))
        
        return '\n'.join(result)
    
    def get_element(self, element_id: str) -> Optional[XMLElement]:
        """Get element by ID."""
        return self.id_map.get(element_id)
    
    def get_all_text_content(self) -> List[Tuple[str, str]]:
        """Get all text content for spell checking. Returns [(element_id, text)]."""
        result = []
        for elem_id, element in self.id_map.items():
            if element.text:
                result.append((elem_id, element.text))
        return result
    
    # XML editing operations using Command pattern
    
    def insert_before(self, tag: str, new_id: str, target_id: str, text: str = "", 
                      attributes: Dict[str, str] = None) -> None:
        """Insert an element before a target element."""
        from ..command.xml_commands import InsertBeforeCommand
        command = InsertBeforeCommand(self, tag, new_id, target_id, text, attributes)
        self.execute_command(command)
    
    def append_child(self, tag: str, new_id: str, parent_id: str, text: str = "", 
                     attributes: Dict[str, str] = None) -> None:
        """Append a child element to a parent."""
        from ..command.xml_commands import AppendChildCommand
        command = AppendChildCommand(self, tag, new_id, parent_id, text, attributes)
        self.execute_command(command)
    
    def edit_id(self, old_id: str, new_id: str) -> None:
        """Edit an element's ID."""
        from ..command.xml_commands import EditIdCommand
        command = EditIdCommand(self, old_id, new_id)
        self.execute_command(command)
    
    def edit_text(self, element_id: str, new_text: str) -> None:
        """Edit an element's text content."""
        from ..command.xml_commands import EditTextCommand
        command = EditTextCommand(self, element_id, new_text)
        self.execute_command(command)
    
    def delete_element(self, element_id: str) -> None:
        """Delete an element and all its children."""
        from ..command.xml_commands import DeleteElementCommand
        command = DeleteElementCommand(self, element_id)
        self.execute_command(command)
    
    def set_attribute(self, element_id: str, attr_name: str, attr_value: str) -> None:
        """Set/modify an element's attribute."""
        from ..command.xml_commands import SetAttributeCommand
        command = SetAttributeCommand(self, element_id, attr_name, attr_value)
        self.execute_command(command)
    
    def remove_attribute(self, element_id: str, attr_name: str) -> None:
        """Remove an element's attribute."""
        from ..command.xml_commands import RemoveAttributeCommand
        command = RemoveAttributeCommand(self, element_id, attr_name)
        self.execute_command(command)
    
    def append_root(self, tag: str, new_id: str, text: str = "", 
                    attributes: Dict[str, str] = None) -> None:
        """Create or replace root element."""
        from ..command.xml_commands import AppendRootCommand
        command = AppendRootCommand(self, tag, new_id, text, attributes)
        self.execute_command(command)

