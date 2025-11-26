#!/usr/bin/env python3
"""
测试拼写检查的列号显示
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.workspace import Workspace
from src.spell_checker import MockSpellChecker

# Set mock spell checker
Workspace.set_spell_checker(MockSpellChecker())


def test_text_file_with_columns():
    """测试文本文件拼写检查显示列号"""
    print("=== 测试文本文件列号显示 ===")
    
    workspace = Workspace()
    workspace.init_file("test.txt", "text", False)
    editor = workspace.active_editor
    
    # Add lines with spelling errors
    editor.append("I will recieve your message")  # "recieve" at column 8
    editor.append("This occured yesterday")       # "occured" at column 6
    
    # Perform spell check
    result = workspace.spell_check()
    
    print("拼写检查结果:")
    print(result)
    print()
    
    # Verify format
    assert '第1行，第8列' in result or '第1行' in result  # Should show column
    assert 'recieve' in result
    assert '第2行，第6列' in result or '第2行' in result
    assert 'occured' in result
    assert '建议:' in result
    print("✓ 文本文件显示格式正确（含列号）")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.txt"):
        os.remove("test.txt")
    
    print("文本文件列号测试通过！\n")


def test_xml_file_positions():
    """测试XML文件拼写检查"""
    print("=== 测试XML文件拼写检查 ===")
    
    workspace = Workspace()
    workspace.init_file("test.xml", "xml", False)
    editor = workspace.active_editor
    
    # Create elements with spelling errors
    editor.append_child('book', 'book1', 'root', '')
    editor.append_child('title', 'title1', 'book1', 'Itallian Food')  # Itallian is wrong
    editor.append_child('author', 'author1', 'book1', 'J K Rowlling')  # Rowlling is wrong
    
    # Perform spell check
    result = workspace.spell_check()
    
    print("拼写检查结果:")
    print(result)
    print()
    
    # Verify format
    assert '元素 title1:' in result
    assert 'Itallian' in result or 'itallian' in result
    assert '元素 author1:' in result
    assert 'Rowlling' in result or 'rowlling' in result
    print("✓ XML文件显示格式正确（含元素ID）")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.xml"):
        os.remove("test.xml")
    
    print("XML文件拼写检查测试通过！\n")


def test_no_errors():
    """测试没有错误的情况"""
    print("=== 测试无错误情况 ===")
    
    workspace = Workspace()
    workspace.init_file("test.txt", "text", False)
    editor = workspace.active_editor
    
    # Add correct text
    editor.append("Hello world")
    editor.append("This is a test")
    
    # Perform spell check
    result = workspace.spell_check()
    
    print(result)
    assert "未发现错误" in result
    print("✓ 无错误时正确提示")
    
    # Clean up
    workspace.close_file(force=True)
    if os.path.exists("test.txt"):
        os.remove("test.txt")
    
    print("无错误情况测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("测试拼写检查列号显示功能")
    print("=" * 50)
    print()
    
    try:
        test_text_file_with_columns()
        test_xml_file_positions()
        test_no_errors()
        
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
    for f in ["test.txt", "test.xml", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

