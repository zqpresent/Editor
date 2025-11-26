#!/usr/bin/env python3
"""
Lab2 功能测试脚本
测试XML编辑器、统计模块、拼写检查等新功能
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workspace import Workspace
from src.editor.xml_editor import XMLEditor
from src.spell_checker import MockSpellChecker

# Set mock spell checker for testing
Workspace.set_spell_checker(MockSpellChecker())


def test_xml_editor():
    """测试XML编辑器基本功能"""
    print("\n=== 测试 XMLEditor ===")
    
    # Create XML editor
    workspace = Workspace()
    result = workspace.init_file("test.xml", "xml", with_log=False)
    print(f"✓ 创建XML文件: {result}")
    
    editor = workspace.active_editor
    assert isinstance(editor, XMLEditor)
    assert editor.root.id == 'root'
    print("✓ XML结构初始化正常")
    
    # Test append-child
    editor.append_child('book', 'book1', 'root', 'The Book')
    assert 'book1' in editor.id_map
    print("✓ append-child 功能正常")
    
    # Test insert-before
    editor.append_child('book', 'book2', 'root', '')
    editor.insert_before('book', 'book0', 'book1', 'First Book')
    assert 'book0' in editor.id_map
    assert editor.root.children[0].id == 'book0'
    print("✓ insert-before 功能正常")
    
    # Test edit-text
    editor.edit_text('book1', 'Updated Book')
    assert editor.id_map['book1'].text == 'Updated Book'
    print("✓ edit-text 功能正常")
    
    # Test edit-id
    editor.edit_id('book2', 'book3')
    assert 'book3' in editor.id_map
    assert 'book2' not in editor.id_map
    print("✓ edit-id 功能正常")
    
    # Test delete
    editor.delete_element('book0')
    assert 'book0' not in editor.id_map
    print("✓ delete 功能正常")
    
    # Test undo/redo
    editor.undo()
    assert 'book0' in editor.id_map
    print("✓ undo 功能正常")
    
    editor.redo()
    assert 'book0' not in editor.id_map
    print("✓ redo 功能正常")
    
    # Test xml-tree
    tree = editor.show_tree()
    assert 'root' in tree
    assert 'book1' in tree
    print("✓ xml-tree 显示正常")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("XMLEditor 测试通过！\n")


def test_statistics():
    """测试统计模块"""
    print("=== 测试 Statistics ===")
    
    workspace = Workspace()
    
    # Load first file
    workspace.init_file("file1.txt", "text", False)
    time.sleep(0.5)
    
    # Load second file
    workspace.init_file("file2.txt", "text", False)
    time.sleep(0.5)
    
    # Switch back to first
    workspace.edit_file("file1.txt")
    time.sleep(0.5)
    
    # Check statistics
    time1 = workspace.statistics.get_time("file1.txt")
    time2 = workspace.statistics.get_time("file2.txt")
    
    assert time1 > 0.5
    assert time2 > 0
    print(f"✓ 时长统计正常: file1={time1:.2f}s, file2={time2:.2f}s")
    
    # Check formatting
    formatted = workspace.statistics.format_time("file1.txt")
    assert "秒" in formatted or "分钟" in formatted
    print(f"✓ 时长格式化正常: {formatted}")
    
    # Test editor-list with time
    editor_list = workspace.get_editor_list()
    assert "秒" in editor_list or "分钟" in editor_list
    print("✓ editor-list显示时长正常")
    
    # Clean up
    workspace.close_file("file1.txt", force=True)
    workspace.close_file("file2.txt", force=True)
    for f in ["file1.txt", "file2.txt"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("Statistics 测试通过！\n")


def test_spell_checker():
    """测试拼写检查"""
    print("=== 测试 Spell Checker ===")
    
    workspace = Workspace()
    
    # Test text file
    workspace.init_file("test.txt", "text", False)
    workspace.execute_on_active('append', 'I recieve your message')
    workspace.execute_on_active('append', 'It occured yesterday')
    
    result = workspace.spell_check()
    assert 'recieve' in result or 'occured' in result
    print("✓ 文本文件拼写检查正常")
    
    workspace.close_file(force=True)
    
    # Test XML file
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    editor.append_child('title', 'title1', 'root', 'Itallian Food')
    
    result = workspace.spell_check()
    assert 'Itallian' in result or 'itallian' in result
    print("✓ XML文件拼写检查正常")
    
    # Clean up
    workspace.close_file(force=True)
    for f in ["test.txt", "test.xml"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("Spell Checker 测试通过！\n")


def test_log_filtering():
    """测试日志过滤"""
    print("=== 测试 Log Filtering ===")
    
    workspace = Workspace()
    
    # Create file with log filtering
    workspace.init_file("test.txt", "text", with_log=False)
    editor = workspace.active_editor
    editor.content = ["# log -e append -e delete"]
    editor.has_log_line = True
    editor.save_to_file()
    
    # Reload to test parsing
    workspace.close_file(force=True)
    workspace.load_file("test.txt")
    
    log_enabled, exclude_cmds = workspace.active_editor.parse_log_config()
    assert log_enabled
    assert 'append' in exclude_cmds
    assert 'delete' in exclude_cmds
    print("✓ 日志过滤配置解析正常")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.txt"):
        os.remove("test.txt")
    if os.path.exists(".test.txt.log"):
        os.remove(".test.txt.log")
    
    print("Log Filtering 测试通过！\n")


def test_save_and_load():
    """测试XML保存和加载"""
    print("=== 测试 XML Save/Load ===")
    
    workspace = Workspace()
    
    # Create and edit XML
    workspace.init_file("books.xml", "xml", False)
    editor = workspace.active_editor
    editor.append_child('book', 'book1', 'root', '')
    editor.append_child('title', 'title1', 'book1', 'Harry Potter')
    editor.append_child('author', 'author1', 'book1', 'J.K. Rowling')
    
    # Save
    workspace.save_file()
    assert os.path.exists("books.xml")
    print("✓ XML保存成功")
    
    # Close and reload
    workspace.close_file(force=True)
    workspace.load_file("books.xml")
    
    # Verify structure
    editor = workspace.active_editor
    assert isinstance(editor, XMLEditor)
    assert 'book1' in editor.id_map
    assert 'title1' in editor.id_map
    assert editor.id_map['title1'].text == 'Harry Potter'
    print("✓ XML加载成功，结构正确")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("books.xml"):
        os.remove("books.xml")
    
    print("XML Save/Load 测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试 Lab2 新功能")
    print("=" * 50)
    
    try:
        test_xml_editor()
        test_statistics()
        test_spell_checker()
        test_log_filtering()
        test_save_and_load()
        
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
    
    # Clean up any remaining files
    print("\n清理测试文件...")
    for f in ["test.txt", "test.xml", "file1.txt", "file2.txt", "books.xml",
              ".test.txt.log", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

