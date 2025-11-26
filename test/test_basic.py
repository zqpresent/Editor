#!/usr/bin/env python3
"""
基本功能测试脚本
用于验证编辑器核心功能是否正常工作
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.editor.text_editor import TextEditor
from src.workspace import Workspace
from src.utils.parser import CommandParser


def test_text_editor():
    """测试文本编辑器基本功能"""
    print("测试 TextEditor...")
    
    editor = TextEditor("test.txt")
    
    # Test append
    editor.append("Line 1")
    editor.append("Line 2")
    assert len(editor.content) == 2
    assert editor.content[0] == "Line 1"
    print("✓ append 功能正常")
    
    # Test insert
    editor.insert(1, 1, "Start: ")
    assert editor.content[0] == "Start: Line 1"
    print("✓ insert 功能正常")
    
    # Test undo
    editor.undo()
    assert editor.content[0] == "Line 1"
    print("✓ undo 功能正常")
    
    # Test redo
    editor.redo()
    assert editor.content[0] == "Start: Line 1"
    print("✓ redo 功能正常")
    
    # Test show
    result = editor.show()
    assert "1: Start: Line 1" in result
    assert "2: Line 2" in result
    print("✓ show 功能正常")
    
    print("TextEditor 测试通过！\n")


def test_workspace():
    """测试工作区功能"""
    print("测试 Workspace...")
    
    # Clean up previous test files
    if os.path.exists(".workspace.json"):
        os.remove(".workspace.json")
    
    workspace = Workspace()
    
    # Test load
    workspace.load_file("test1.txt")
    assert "test1.txt" in workspace.editors
    print("✓ load 功能正常")
    
    # Test active editor
    assert workspace.active_editor is not None
    assert workspace.active_editor.filepath == "test1.txt"
    print("✓ active_editor 设置正常")
    
    # Test execute on active
    workspace.execute_on_active('append', 'Test line')
    assert workspace.active_editor.content == ['Test line']
    print("✓ execute_on_active 功能正常")
    
    # Test multiple files
    workspace.load_file("test2.txt")
    assert len(workspace.editors) == 2
    assert workspace.active_editor.filepath == "test2.txt"
    print("✓ 多文件管理正常")
    
    # Test editor list
    editor_list = workspace.get_editor_list()
    assert "test1.txt" in editor_list or "test2.txt" in editor_list
    print("✓ editor_list 功能正常")
    
    # Clean up
    for filepath in list(workspace.editors.keys()):
        workspace.close_file(filepath, force=True)
    
    print("Workspace 测试通过！\n")


def test_command_parser():
    """测试命令解析器"""
    print("测试 CommandParser...")
    
    parser = CommandParser()
    
    # Test basic command
    cmd, args = parser.parse("load file.txt")
    assert cmd == "load"
    assert args == ["file.txt"]
    print("✓ 基本命令解析正常")
    
    # Test quoted string
    cmd, args = parser.parse('append "hello world"')
    assert cmd == "append"
    assert args == ["hello world"]
    print("✓ 引号字符串解析正常")
    
    # Test position parsing
    pos = parser.parse_position("1:5")
    assert pos == (1, 5)
    print("✓ 位置解析正常")
    
    # Test unescape
    text = parser.unescape_string("line1\\nline2")
    assert text == "line1\nline2"
    print("✓ 转义字符处理正常")
    
    print("CommandParser 测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试文本编辑器核心功能")
    print("=" * 50)
    print()
    
    try:
        test_text_editor()
        test_command_parser()
        test_workspace()
        
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
    
    # Clean up test files
    print("\n清理测试文件...")
    for f in ["test.txt", "test1.txt", "test2.txt", ".workspace.json"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  删除 {f}")


if __name__ == '__main__':
    main()

