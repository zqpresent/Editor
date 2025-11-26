#!/usr/bin/env python3
"""
测试XML属性管理功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workspace import Workspace
from src.spell_checker import MockSpellChecker

# Set mock spell checker
Workspace.set_spell_checker(MockSpellChecker())


def test_set_attribute():
    """测试设置属性"""
    print("=== 测试 set-attr ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create element
    editor.append_child('book', 'book1', 'root', 'My Book')
    
    # Set attribute
    editor.set_attribute('book1', 'lang', 'en')
    assert editor.id_map['book1'].attributes['lang'] == 'en'
    print("✓ 设置新属性成功")
    
    # Modify attribute
    editor.set_attribute('book1', 'lang', 'zh')
    assert editor.id_map['book1'].attributes['lang'] == 'zh'
    print("✓ 修改属性成功")
    
    # Test undo
    editor.undo()
    assert editor.id_map['book1'].attributes['lang'] == 'en'
    print("✓ undo后恢复旧值")
    
    # Test redo
    editor.redo()
    assert editor.id_map['book1'].attributes['lang'] == 'zh'
    print("✓ redo后恢复新值")
    
    # Set multiple attributes
    editor.set_attribute('book1', 'category', 'FICTION')
    editor.set_attribute('book1', 'edition', '2nd')
    assert len(editor.id_map['book1'].attributes) == 4  # id, lang, category, edition
    print("✓ 设置多个属性成功")
    
    # Test id protection
    try:
        editor.set_attribute('book1', 'id', 'newid')
        assert False, "应该抛出异常"
    except Exception as e:
        assert 'id属性' in str(e)
        print("✓ id属性保护正常")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("set-attr 测试通过！\n")


def test_remove_attribute():
    """测试删除属性"""
    print("=== 测试 remove-attr ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create element with attributes
    editor.append_child('book', 'book1', 'root', '')
    editor.set_attribute('book1', 'lang', 'en')
    editor.set_attribute('book1', 'category', 'FICTION')
    
    # Remove attribute
    editor.remove_attribute('book1', 'lang')
    assert 'lang' not in editor.id_map['book1'].attributes
    assert 'category' in editor.id_map['book1'].attributes
    print("✓ 删除属性成功")
    
    # Test undo
    editor.undo()
    assert 'lang' in editor.id_map['book1'].attributes
    assert editor.id_map['book1'].attributes['lang'] == 'en'
    print("✓ undo后恢复属性")
    
    # Test redo
    editor.redo()
    assert 'lang' not in editor.id_map['book1'].attributes
    print("✓ redo后再次删除")
    
    # Test id protection
    try:
        editor.remove_attribute('book1', 'id')
        assert False, "应该抛出异常"
    except Exception as e:
        assert 'id属性' in str(e)
        print("✓ id属性删除保护正常")
    
    # Test non-existent attribute
    try:
        editor.remove_attribute('book1', 'nonexistent')
        assert False, "应该抛出异常"
    except Exception as e:
        assert '属性不存在' in str(e)
        print("✓ 不存在属性检测正常")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("remove-attr 测试通过！\n")


def test_save_and_load_with_attributes():
    """测试带属性的保存和加载"""
    print("=== 测试属性保存和加载 ===")
    
    workspace = Workspace()
    workspace.init_file("book.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create structure with attributes
    editor.append_child('book', 'book1', 'root', '')
    editor.set_attribute('book1', 'category', 'COOKING')
    editor.append_child('title', 'title1', 'book1', 'Everyday Italian')
    editor.set_attribute('title1', 'lang', 'en')
    editor.set_attribute('title1', 'edition', '2nd')
    
    # Save
    workspace.save_file()
    print("✓ 保存成功")
    
    # Close and reload
    workspace.close_file(force=True)
    workspace.load_file("book.xml")
    editor = workspace.active_editor
    
    # Verify attributes
    assert editor.id_map['book1'].attributes['category'] == 'COOKING'
    assert editor.id_map['title1'].attributes['lang'] == 'en'
    assert editor.id_map['title1'].attributes['edition'] == '2nd'
    print("✓ 属性加载正确")
    
    # Check xml-tree display
    tree = editor.show_tree()
    assert 'category="COOKING"' in tree
    assert 'lang="en"' in tree
    assert 'edition="2nd"' in tree
    print("✓ xml-tree正确显示属性")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("book.xml"):
        os.remove("book.xml")
    
    print("属性保存和加载测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试 XML 属性管理功能")
    print("=" * 50)
    print()
    
    try:
        test_set_attribute()
        test_remove_attribute()
        test_save_and_load_with_attributes()
        
        print("=" * 50)
        print("✅ 所有属性管理测试通过！")
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
    for f in ["test.xml", "book.xml", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

