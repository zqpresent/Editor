"""
XML Edit Commands - Concrete commands for XML editing operations.
All these commands support undo/redo through the Command pattern.
"""

from typing import TYPE_CHECKING, Optional, Dict
from .command import EditCommand
from ..utils.exceptions import EditorException

if TYPE_CHECKING:
    from ..editor.xml_editor import XMLEditor, XMLElement


class InsertBeforeCommand(EditCommand):
    """Command to insert an element before a target element."""
    
    def __init__(self, editor: 'XMLEditor', tag: str, new_id: str, 
                 target_id: str, text: str = "", attributes: Dict[str, str] = None):
        super().__init__(editor)
        self.tag = tag
        self.new_id = new_id
        self.target_id = target_id
        self.text = text
        self.attributes = attributes or {}
        self.new_element: Optional['XMLElement'] = None
        self.parent: Optional['XMLElement'] = None
        self.insert_index: int = 0
    
    def execute(self) -> None:
        """Insert element before target."""
        from ..editor.xml_editor import XMLElement
        
        # Validate IDs
        if self.new_id in self.editor.id_map:
            raise EditorException(f"元素ID已存在: {self.new_id}")
        
        target = self.editor.get_element(self.target_id)
        if not target:
            raise EditorException(f"目标元素不存在: {self.target_id}")
        
        if not target.parent:
            raise EditorException("不能在根元素前插入元素")
        
        # Create new element
        self.new_element = XMLElement(self.tag, self.new_id, self.text)
        
        # Set additional attributes (skip 'id' as it's already set)
        for key, value in self.attributes.items():
            if key != 'id':
                self.new_element.attributes[key] = value
        
        # Insert before target
        self.parent = target.parent
        self.insert_index = self.parent.get_child_index(target)
        self.parent.insert_child(self.insert_index, self.new_element)
        
        # Update id map
        self.editor.id_map[self.new_id] = self.new_element
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Remove the inserted element."""
        if self.new_element and self.parent:
            self.parent.remove_child(self.new_element)
            del self.editor.id_map[self.new_id]
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        text_part = f' "{self.text}"' if self.text else ' ""'
        attr_part = ' '.join(f'{k}={v}' for k, v in self.attributes.items())
        if attr_part:
            return f'insert-before {self.tag} {self.new_id} {self.target_id}{text_part} {attr_part}'
        return f'insert-before {self.tag} {self.new_id} {self.target_id}{text_part}'


class AppendChildCommand(EditCommand):
    """Command to append a child element."""
    
    def __init__(self, editor: 'XMLEditor', tag: str, new_id: str,
                 parent_id: str, text: str = "", attributes: Dict[str, str] = None):
        super().__init__(editor)
        self.tag = tag
        self.new_id = new_id
        self.parent_id = parent_id
        self.text = text
        self.attributes = attributes or {}
        self.new_element: Optional['XMLElement'] = None
        self.parent: Optional['XMLElement'] = None
    
    def execute(self) -> None:
        """Append child to parent element."""
        from ..editor.xml_editor import XMLElement
        
        # Validate IDs
        if self.new_id in self.editor.id_map:
            raise EditorException(f"元素ID已存在: {self.new_id}")
        
        self.parent = self.editor.get_element(self.parent_id)
        if not self.parent:
            raise EditorException(f"父元素不存在: {self.parent_id}")
        
        # Create and append new element
        self.new_element = XMLElement(self.tag, self.new_id, self.text)
        
        # Set additional attributes (skip 'id' as it's already set)
        for key, value in self.attributes.items():
            if key != 'id':
                self.new_element.attributes[key] = value
        
        self.parent.add_child(self.new_element)
        
        # Update id map
        self.editor.id_map[self.new_id] = self.new_element
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Remove the appended child."""
        if self.new_element and self.parent:
            self.parent.remove_child(self.new_element)
            del self.editor.id_map[self.new_id]
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        text_part = f' "{self.text}"' if self.text else ' ""'
        attr_part = ' '.join(f'{k}={v}' for k, v in self.attributes.items())
        if attr_part:
            return f'append-child {self.tag} {self.new_id} {self.parent_id}{text_part} {attr_part}'
        return f'append-child {self.tag} {self.new_id} {self.parent_id}{text_part}'


class EditIdCommand(EditCommand):
    """Command to edit an element's ID."""
    
    def __init__(self, editor: 'XMLEditor', old_id: str, new_id: str):
        super().__init__(editor)
        self.old_id = old_id
        self.new_id = new_id
        self.element: Optional['XMLElement'] = None
    
    def execute(self) -> None:
        """Change element ID."""
        # Validate
        self.element = self.editor.get_element(self.old_id)
        if not self.element:
            raise EditorException(f"元素不存在: {self.old_id}")
        
        if self.new_id in self.editor.id_map:
            raise EditorException(f"目标ID已存在: {self.new_id}")
        
        if self.element == self.editor.root:
            # Allow but warn
            pass
        
        # Update ID
        self.element.id = self.new_id
        self.element.attributes['id'] = self.new_id
        
        # Update id map
        del self.editor.id_map[self.old_id]
        self.editor.id_map[self.new_id] = self.element
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Restore old ID."""
        if self.element:
            self.element.id = self.old_id
            self.element.attributes['id'] = self.old_id
            
            # Update id map
            del self.editor.id_map[self.new_id]
            self.editor.id_map[self.old_id] = self.element
            
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'edit-id {self.old_id} {self.new_id}'


class EditTextCommand(EditCommand):
    """Command to edit an element's text content."""
    
    def __init__(self, editor: 'XMLEditor', element_id: str, new_text: str):
        super().__init__(editor)
        self.element_id = element_id
        self.new_text = new_text
        self.old_text: str = ""
        self.element: Optional['XMLElement'] = None
    
    def execute(self) -> None:
        """Change element text."""
        self.element = self.editor.get_element(self.element_id)
        if not self.element:
            raise EditorException(f"元素不存在: {self.element_id}")
        
        # Save old text and set new
        self.old_text = self.element.text
        self.element.text = self.new_text
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Restore old text."""
        if self.element:
            self.element.text = self.old_text
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'edit-text {self.element_id} "{self.new_text}"'


class DeleteElementCommand(EditCommand):
    """Command to delete an element."""
    
    def __init__(self, editor: 'XMLEditor', element_id: str):
        super().__init__(editor)
        self.element_id = element_id
        self.element: Optional['XMLElement'] = None
        self.parent: Optional['XMLElement'] = None
        self.index: int = 0
        self.deleted_ids: Dict[str, 'XMLElement'] = {}
    
    def execute(self) -> None:
        """Delete element and all its children."""
        self.element = self.editor.get_element(self.element_id)
        if not self.element:
            raise EditorException(f"元素不存在: {self.element_id}")
        
        if self.element == self.editor.root:
            raise EditorException("不能删除根元素")
        
        if not self.element.parent:
            raise EditorException("不能删除没有父元素的元素")
        
        # Save state for undo
        self.parent = self.element.parent
        self.index = self.parent.get_child_index(self.element)
        
        # Collect all IDs to delete (element and descendants)
        self._collect_ids(self.element)
        
        # Remove from parent
        self.parent.remove_child(self.element)
        
        # Remove from id map
        for elem_id in self.deleted_ids.keys():
            del self.editor.id_map[elem_id]
        
        self.editor.mark_modified()
    
    def _collect_ids(self, element: 'XMLElement') -> None:
        """Recursively collect element and descendants' IDs."""
        self.deleted_ids[element.id] = element
        for child in element.children:
            self._collect_ids(child)
    
    def undo(self) -> None:
        """Restore deleted element."""
        if self.element and self.parent is not None:
            # Re-insert element
            self.parent.insert_child(self.index, self.element)
            
            # Restore id map
            for elem_id, elem in self.deleted_ids.items():
                self.editor.id_map[elem_id] = elem
            
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'delete {self.element_id}'


class SetAttributeCommand(EditCommand):
    """Command to set/modify an element's attribute."""
    
    def __init__(self, editor: 'XMLEditor', element_id: str, attr_name: str, attr_value: str):
        super().__init__(editor)
        self.element_id = element_id
        self.attr_name = attr_name
        self.attr_value = attr_value
        self.old_value: Optional[str] = None
        self.element: Optional['XMLElement'] = None
    
    def execute(self) -> None:
        """Set attribute value."""
        # Validate
        self.element = self.editor.get_element(self.element_id)
        if not self.element:
            raise EditorException(f"元素不存在: {self.element_id}")
        
        # Prevent modifying id through this command
        if self.attr_name == 'id':
            raise EditorException("不能通过set-attr修改id属性，请使用edit-id命令")
        
        # Save old value for undo
        self.old_value = self.element.attributes.get(self.attr_name)
        
        # Set new value
        self.element.attributes[self.attr_name] = self.attr_value
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Restore old attribute value."""
        if self.element:
            if self.old_value is None:
                # Attribute didn't exist, remove it
                if self.attr_name in self.element.attributes:
                    del self.element.attributes[self.attr_name]
            else:
                # Restore old value
                self.element.attributes[self.attr_name] = self.old_value
            
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'set-attr {self.element_id} {self.attr_name} {self.attr_value}'


class RemoveAttributeCommand(EditCommand):
    """Command to remove an element's attribute."""
    
    def __init__(self, editor: 'XMLEditor', element_id: str, attr_name: str):
        super().__init__(editor)
        self.element_id = element_id
        self.attr_name = attr_name
        self.old_value: Optional[str] = None
        self.element: Optional['XMLElement'] = None
    
    def execute(self) -> None:
        """Remove attribute."""
        # Validate
        self.element = self.editor.get_element(self.element_id)
        if not self.element:
            raise EditorException(f"元素不存在: {self.element_id}")
        
        # Prevent removing id attribute
        if self.attr_name == 'id':
            raise EditorException("不能删除id属性")
        
        # Check if attribute exists
        if self.attr_name not in self.element.attributes:
            raise EditorException(f"属性不存在: {self.attr_name}")
        
        # Save old value for undo
        self.old_value = self.element.attributes[self.attr_name]
        
        # Remove attribute
        del self.element.attributes[self.attr_name]
        
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Restore removed attribute."""
        if self.element and self.old_value is not None:
            self.element.attributes[self.attr_name] = self.old_value
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        return f'remove-attr {self.element_id} {self.attr_name}'


class AppendRootCommand(EditCommand):
    """Command to create or replace root element."""
    
    def __init__(self, editor: 'XMLEditor', tag: str, new_id: str, 
                 text: str = "", attributes: Dict[str, str] = None):
        super().__init__(editor)
        self.tag = tag
        self.new_id = new_id
        self.text = text
        self.attributes = attributes or {}
        self.old_root: Optional['XMLElement'] = None
        self.old_id_map: Dict[str, 'XMLElement'] = {}
    
    def execute(self) -> None:
        """Create or replace root element."""
        from ..editor.xml_editor import XMLElement
        
        # Check if we can create/replace root
        if self.editor.root:
            # If root has children, it's being used - reject
            if len(self.editor.root.children) > 0:
                raise EditorException("XML文档已有根元素（含子元素），不能创建新的根元素")
            
            # If root is not default, reject
            if self.editor.root.tag != 'root' or self.editor.root.id != 'root':
                raise EditorException("XML文档已有自定义根元素，不能替换")
        
        # Check if new ID already exists (shouldn't happen with empty root, but be safe)
        if self.new_id in self.editor.id_map and self.new_id != 'root':
            raise EditorException(f"元素ID已存在: {self.new_id}")
        
        # Save old state for undo
        self.old_root = self.editor.root
        self.old_id_map = self.editor.id_map.copy()
        
        # Create new root element
        new_root = XMLElement(self.tag, self.new_id, self.text)
        
        # Set additional attributes
        for key, value in self.attributes.items():
            if key != 'id':
                new_root.attributes[key] = value
        
        # Replace root
        self.editor.root = new_root
        self.editor.id_map = {self.new_id: new_root}
        self.editor.mark_modified()
    
    def undo(self) -> None:
        """Restore old root."""
        if self.old_root:
            self.editor.root = self.old_root
            self.editor.id_map = self.old_id_map
            self.editor.mark_modified()
    
    def get_description(self) -> str:
        text_part = f' "{self.text}"' if self.text else ' ""'
        attr_part = ' '.join(f'{k}={v}' for k, v in self.attributes.items())
        if attr_part:
            return f'append-root {self.tag} {self.new_id}{text_part} {attr_part}'
        return f'append-root {self.tag} {self.new_id}{text_part}'

