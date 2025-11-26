#!/usr/bin/env python3
"""
测试 append-root 命令
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.workspace import Workspace
from src.spell_checker import MockSpellChecker
from src.utils.exceptions import EditorException

# Set mock spell checker
Workspace.set_spell_checker(MockSpellChecker())


def test_replace_default_root():
    """测试替换默认root"""
    print("=== 测试替换默认root ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Check default root
    assert editor.root.tag == 'root'
    assert editor.root.id == 'root'
    print("✓ 默认root创建成功")
    
    # Replace with custom root
    editor.append_root('bookstore', 'store1', '', {'location': 'Beijing', 'type': 'online'})
    
    # Verify
    assert editor.root.tag == 'bookstore'
    assert editor.root.id == 'store1'
    assert editor.root.attributes['location'] == 'Beijing'
    assert editor.root.attributes['type'] == 'online'
    assert 'store1' in editor.id_map
    assert 'root' not in editor.id_map
    print("✓ 替换默认root成功")
    
    # Test undo
    editor.undo()
    assert editor.root.tag == 'root'
    assert editor.root.id == 'root'
    print("✓ undo恢复默认root")
    
    # Test redo
    editor.redo()
    assert editor.root.tag == 'bookstore'
    assert editor.root.id == 'store1'
    print("✓ redo恢复自定义root")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("替换默认root测试通过！\n")


def test_reject_with_children():
    """测试拒绝替换有子元素的root"""
    print("=== 测试拒绝替换有子元素的root ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Add child to root
    editor.append_child('book', 'book1', 'root', '')
    assert len(editor.root.children) == 1
    print("✓ root已有子元素")
    
    # Try to replace root - should fail
    try:
        editor.append_root('library', 'lib1', '')
        assert False, "应该抛出异常"
    except EditorException as e:
        assert '含子元素' in str(e)
        print(f"✓ 正确拒绝: {e}")
    
    # Verify root unchanged
    assert editor.root.tag == 'root'
    assert editor.root.id == 'root'
    assert len(editor.root.children) == 1
    print("✓ root保持不变")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("拒绝替换测试通过！\n")


def test_reject_custom_root():
    """测试拒绝替换已自定义的root"""
    print("=== 测试拒绝替换已自定义的root ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Replace with custom root first
    editor.append_root('catalog', 'cat1', '')
    print("✓ 已创建自定义root")
    
    # Try to replace again - should fail
    try:
        editor.append_root('library', 'lib1', '')
        assert False, "应该抛出异常"
    except EditorException as e:
        assert '自定义根元素' in str(e)
        print(f"✓ 正确拒绝: {e}")
    
    # Verify root unchanged
    assert editor.root.tag == 'catalog'
    assert editor.root.id == 'cat1'
    print("✓ root保持不变")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("拒绝替换自定义root测试通过！\n")


def test_save_and_load():
    """测试保存和加载自定义root"""
    print("=== 测试保存和加载 ===")
    
    workspace = Workspace()
    workspace.init_file("catalog.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create custom root with children
    editor.append_root('catalog', 'cat1', '', {'type': 'products', 'version': '1.0'})
    editor.append_child('item', 'item1', 'cat1', 'Product A', {'price': '99.99'})
    
    # Save
    workspace.save_file()
    print("✓ 保存成功")
    
    # Close and reload
    workspace.close_file(force=True)
    workspace.load_file("catalog.xml")
    editor = workspace.active_editor
    
    # Verify structure
    assert editor.root.tag == 'catalog'
    assert editor.root.id == 'cat1'
    assert editor.root.attributes['type'] == 'products'
    assert editor.root.attributes['version'] == '1.0'
    assert 'item1' in editor.id_map
    assert editor.id_map['item1'].text == 'Product A'
    print("✓ 加载正确")
    
    # Verify xml tree
    tree = editor.show_tree()
    assert 'catalog' in tree
    assert 'cat1' in tree
    assert 'type="products"' in tree
    print("✓ xml-tree显示正确")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("catalog.xml"):
        os.remove("catalog.xml")
    
    print("保存和加载测试通过！\n")


def test_workflow():
    """测试完整工作流"""
    print("=== 测试完整工作流 ===")
    
    workspace = Workspace()
    workspace.init_file("bookstore.xml", "xml", False)
    editor = workspace.active_editor
    
    # Step 1: Create custom root
    editor.append_root('bookstore', 'store1', '', {'location': 'Beijing'})
    print("✓ Step 1: 创建自定义根元素")
    
    # Step 2: Add books
    editor.append_child('book', 'book1', 'store1', '', {'category': 'FICTION'})
    editor.append_child('book', 'book2', 'store1', '', {'category': 'SCIENCE'})
    print("✓ Step 2: 添加子元素")
    
    # Step 3: Add book details
    editor.append_child('title', 'title1', 'book1', 'Harry Potter', {'lang': 'en'})
    editor.append_child('author', 'author1', 'book1', 'J.K. Rowling')
    print("✓ Step 3: 添加详细信息")
    
    # Verify structure
    assert editor.root.tag == 'bookstore'
    assert len(editor.root.children) == 2
    assert len(editor.id_map) == 5  # store1, book1, book2, title1, author1
    print("✓ 结构验证成功")
    
    # Test undo multiple times
    editor.undo()  # Remove author1
    editor.undo()  # Remove title1
    editor.undo()  # Remove book2
    assert len(editor.root.children) == 1
    print("✓ 多次undo成功")
    
    # Test redo
    editor.redo()  # Restore book2
    assert len(editor.root.children) == 2
    print("✓ redo成功")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("bookstore.xml"):
        os.remove("bookstore.xml")
    
    print("完整工作流测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("测试 append-root 命令")
    print("=" * 50)
    print()
    
    try:
        test_replace_default_root()
        test_reject_with_children()
        test_reject_custom_root()
        test_save_and_load()
        test_workflow()
        
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
    for f in ["test.xml", "catalog.xml", "bookstore.xml", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

