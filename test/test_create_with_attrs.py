#!/usr/bin/env python3
"""
测试创建元素时直接添加属性的功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workspace import Workspace
from src.spell_checker import MockSpellChecker

# Set mock spell checker
Workspace.set_spell_checker(MockSpellChecker())


def test_append_child_with_attributes():
    """测试append-child带属性"""
    print("=== 测试 append-child 带属性 ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create element with attributes
    editor.append_child('book', 'book1', 'root', 'My Book', {'category': 'FICTION', 'year': '2005'})
    
    # Verify
    assert 'book1' in editor.id_map
    assert editor.id_map['book1'].attributes['category'] == 'FICTION'
    assert editor.id_map['book1'].attributes['year'] == '2005'
    assert editor.id_map['book1'].text == 'My Book'
    print("✓ append-child创建时添加属性成功")
    
    # Test with multiple attributes
    editor.append_child('title', 'title1', 'book1', 'Harry Potter', 
                       {'lang': 'en', 'edition': '1st', 'style': 'bold'})
    assert editor.id_map['title1'].attributes['lang'] == 'en'
    assert editor.id_map['title1'].attributes['edition'] == '1st'
    assert editor.id_map['title1'].attributes['style'] == 'bold'
    print("✓ 多个属性添加成功")
    
    # Test undo
    editor.undo()
    assert 'title1' not in editor.id_map
    print("✓ undo删除整个元素（包括属性）")
    
    # Test redo
    editor.redo()
    assert 'title1' in editor.id_map
    assert editor.id_map['title1'].attributes['lang'] == 'en'
    print("✓ redo恢复整个元素（包括属性）")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("append-child 带属性测试通过！\n")


def test_insert_before_with_attributes():
    """测试insert-before带属性"""
    print("=== 测试 insert-before 带属性 ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create two elements
    editor.append_child('book', 'book1', 'root', '')
    editor.append_child('book', 'book2', 'root', '')
    
    # Insert before with attributes
    editor.insert_before('book', 'book0', 'book1', 'First Book', 
                        {'category': 'CHILDREN', 'featured': 'true'})
    
    # Verify
    assert 'book0' in editor.id_map
    assert editor.root.children[0].id == 'book0'
    assert editor.id_map['book0'].attributes['category'] == 'CHILDREN'
    assert editor.id_map['book0'].attributes['featured'] == 'true'
    print("✓ insert-before创建时添加属性成功")
    
    # Test undo/redo
    editor.undo()
    assert 'book0' not in editor.id_map
    editor.redo()
    assert 'book0' in editor.id_map
    assert editor.id_map['book0'].attributes['category'] == 'CHILDREN'
    print("✓ undo/redo正常工作")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("insert-before 带属性测试通过！\n")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("=== 测试向后兼容性 ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Test without attributes (old way)
    editor.append_child('book', 'book1', 'root', '')
    assert 'book1' in editor.id_map
    assert len(editor.id_map['book1'].attributes) == 1  # Only 'id'
    print("✓ 不带属性的旧用法仍然有效")
    
    editor.append_child('title', 'title1', 'book1', 'Some Title')
    assert editor.id_map['title1'].text == 'Some Title'
    assert len(editor.id_map['title1'].attributes) == 1  # Only 'id'
    print("✓ 带文本不带属性的用法正常")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("向后兼容性测试通过！\n")


def test_save_and_load_with_attrs():
    """测试保存和加载带属性的元素"""
    print("=== 测试保存和加载 ===")
    
    workspace = Workspace()
    workspace.init_file("books.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create structure with attributes at creation time
    editor.append_child('book', 'book1', 'root', '', {'category': 'COOKING', 'year': '2005'})
    editor.append_child('title', 'title1', 'book1', 'Everyday Italian', {'lang': 'en', 'edition': '2nd'})
    editor.append_child('author', 'author1', 'book1', 'Giada De Laurentiis', {'country': 'USA'})
    
    # Save
    workspace.save_file()
    print("✓ 保存成功")
    
    # Close and reload
    workspace.close_file(force=True)
    workspace.load_file("books.xml")
    editor = workspace.active_editor
    
    # Verify all attributes
    assert editor.id_map['book1'].attributes['category'] == 'COOKING'
    assert editor.id_map['book1'].attributes['year'] == '2005'
    assert editor.id_map['title1'].attributes['lang'] == 'en'
    assert editor.id_map['title1'].attributes['edition'] == '2nd'
    assert editor.id_map['author1'].attributes['country'] == 'USA'
    print("✓ 所有属性正确加载")
    
    # Check xml-tree
    tree = editor.show_tree()
    assert 'category="COOKING"' in tree
    assert 'lang="en"' in tree
    assert 'country="USA"' in tree
    print("✓ xml-tree正确显示")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("books.xml"):
        os.remove("books.xml")
    
    print("保存和加载测试通过！\n")


def test_id_protection():
    """测试id属性保护"""
    print("=== 测试 id 属性保护 ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Try to set 'id' attribute (should be ignored)
    editor.append_child('book', 'book1', 'root', '', {'id': 'wrong_id', 'category': 'FICTION'})
    
    # Verify id is not changed
    assert editor.id_map['book1'].id == 'book1'
    assert editor.id_map['book1'].attributes['id'] == 'book1'
    assert editor.id_map['book1'].attributes['category'] == 'FICTION'
    print("✓ id属性保护正常（id不被覆盖）")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("id保护测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("测试创建元素时直接添加属性功能")
    print("=" * 50)
    print()
    
    try:
        test_append_child_with_attributes()
        test_insert_before_with_attributes()
        test_backward_compatibility()
        test_save_and_load_with_attrs()
        test_id_protection()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Clean up
    print("\n清理测试文件...")
    for f in ["test.xml", "books.xml", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

