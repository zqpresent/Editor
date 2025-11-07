"""
Main entry point for the text editor.
Handles command-line interface and user interaction.
"""

import sys
from typing import Optional
from .workspace import Workspace
from .utils.parser import CommandParser
from .storage.file_manager import FileManager
from .utils.exceptions import EditorException


class TextEditorCLI:
    """Command-line interface for the text editor."""
    
    def __init__(self):
        self.workspace = Workspace()
        self.parser = CommandParser()
        self.running = True
    
    def start(self) -> None:
        """Start the editor CLI."""
        print("欢迎使用文本编辑器！")
        print("输入 'help' 查看可用命令")
        print()
        
        # Try to restore previous session
        restore_msg = self.workspace.restore_state()
        if restore_msg:
            print(restore_msg)
            print()
        
        # Main command loop
        while self.running:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n使用 'exit' 命令退出")
            except EOFError:
                self.running = False
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
    
    def process_command(self, input_str: str) -> None:
        """Process a single command."""
        command, args = self.parser.parse(input_str)
        
        if not command:
            return
        
        # Route to appropriate handler
        try:
            if command == 'help':
                self.cmd_help()
            elif command == 'load':
                self.cmd_load(args)
            elif command == 'save':
                self.cmd_save(args)
            elif command == 'init':
                self.cmd_init(args)
            elif command == 'close':
                self.cmd_close(args)
            elif command == 'edit':
                self.cmd_edit(args)
            elif command == 'editor-list':
                self.cmd_editor_list()
            elif command == 'dir-tree':
                self.cmd_dir_tree(args)
            elif command == 'undo':
                self.cmd_undo()
            elif command == 'redo':
                self.cmd_redo()
            elif command == 'append':
                self.cmd_append(args)
            elif command == 'insert':
                self.cmd_insert(args)
            elif command == 'delete':
                self.cmd_delete(args)
            elif command == 'replace':
                self.cmd_replace(args)
            elif command == 'show':
                self.cmd_show(args)
            elif command == 'log-on':
                self.cmd_log_on(args)
            elif command == 'log-off':
                self.cmd_log_off(args)
            elif command == 'log-show':
                self.cmd_log_show(args)
            elif command == 'exit':
                self.cmd_exit()
            else:
                print(f"未知命令: {command}")
                print("输入 'help' 查看可用命令")
        
        except EditorException as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Command Handlers - Workspace Commands
    
    def cmd_help(self) -> None:
        """Display help information."""
        help_text = """
可用命令:

工作区命令:
  load <file>              - 加载文件
  save [file|all]          - 保存文件
  init <file> [with-log]   - 创建新缓冲区
  close [file]             - 关闭文件
  edit <file>              - 切换活动文件
  editor-list              - 显示文件列表
  dir-tree [path]          - 显示目录树
  undo                     - 撤销
  redo                     - 重做
  exit                     - 退出程序

文本编辑命令:
  append "text"            - 追加文本
  insert <line:col> "text" - 插入文本
  delete <line:col> <len>  - 删除字符
  replace <line:col> <len> "text" - 替换文本
  show [start:end]         - 显示内容

日志命令:
  log-on [file]            - 启用日志
  log-off [file]           - 关闭日志
  log-show [file]          - 显示日志
"""
        print(help_text)
    
    def cmd_load(self, args: list) -> None:
        """Load a file."""
        if not args:
            print("Error: 缺少文件路径")
            print("用法: load <file>")
            return
        
        filepath = args[0]
        result = self.workspace.load_file(filepath)
        print(result)
        
        # Log the command
        self.workspace.log_command(f"load {filepath}")
    
    def cmd_save(self, args: list) -> None:
        """Save file(s)."""
        target = args[0] if args else None
        result = self.workspace.save_file(target)
        print(result)
        
        # Log the command
        cmd_str = f"save {target}" if target else "save"
        self.workspace.log_command(cmd_str)
    
    def cmd_init(self, args: list) -> None:
        """Initialize a new file."""
        if not args:
            print("Error: 缺少文件路径")
            print("用法: init <file> [with-log]")
            return
        
        filepath = args[0]
        with_log = len(args) > 1 and args[1] == 'with-log'
        
        result = self.workspace.init_file(filepath, with_log)
        print(result)
        
        # Log the command
        cmd_str = f"init {filepath} with-log" if with_log else f"init {filepath}"
        self.workspace.log_command(cmd_str)
    
    def cmd_close(self, args: list) -> None:
        """Close a file."""
        filepath = args[0] if args else None
        result, needs_prompt = self.workspace.close_file(filepath)
        
        if needs_prompt:
            # File is modified, ask for confirmation
            response = input(f"文件已修改: {result}\n是否保存? (y/n): ").strip().lower()
            if response == 'y':
                self.workspace.save_file(result)
                print(f"Saved: {result}")
            
            # Close without saving
            final_result, _ = self.workspace.close_file(result, force=True)
            print(final_result)
        else:
            print(result)
        
        # Log the command
        cmd_str = f"close {filepath}" if filepath else "close"
        self.workspace.log_command(cmd_str)
    
    def cmd_edit(self, args: list) -> None:
        """Switch active file."""
        if not args:
            print("Error: 缺少文件路径")
            print("用法: edit <file>")
            return
        
        filepath = args[0]
        result = self.workspace.edit_file(filepath)
        print(result)
        
        # Log the command
        self.workspace.log_command(f"edit {filepath}")
    
    def cmd_editor_list(self) -> None:
        """Display list of open files."""
        result = self.workspace.get_editor_list()
        print(result)
    
    def cmd_dir_tree(self, args: list) -> None:
        """Display directory tree."""
        path = args[0] if args else '.'
        result = FileManager.display_tree(path)
        print(result)
    
    def cmd_undo(self) -> None:
        """Undo last operation."""
        result = self.workspace.undo()
        print(result)
    
    def cmd_redo(self) -> None:
        """Redo last undone operation."""
        result = self.workspace.redo()
        print(result)
    
    def cmd_exit(self) -> None:
        """Exit the editor."""
        # Check for unsaved files
        modified = self.workspace.get_modified_files()
        
        if modified:
            print("以下文件有未保存的更改:")
            for filepath in modified:
                print(f"  {filepath}")
            
            for filepath in modified:
                response = input(f"保存 {filepath}? (y/n): ").strip().lower()
                if response == 'y':
                    self.workspace.save_file(filepath)
                    print(f"Saved: {filepath}")
        
        # Save workspace state
        self.workspace.save_state()
        print("工作区状态已保存。再见！")
        self.running = False
    
    # Command Handlers - Text Editing Commands
    
    def cmd_append(self, args: list) -> None:
        """Append text to the end of file."""
        if not args:
            print("Error: 缺少文本参数")
            print("用法: append \"text\"")
            return
        
        text = self.parser.unescape_string(args[0])
        
        try:
            self.workspace.execute_on_active('append', text)
            print("OK")
            
            # Log the command
            self.workspace.log_command(f'append "{args[0]}"')
        except EditorException as e:
            print(f"Error: {str(e)}")
    
    def cmd_insert(self, args: list) -> None:
        """Insert text at position."""
        if len(args) < 2:
            print("Error: 参数不足")
            print("用法: insert <line:col> \"text\"")
            return
        
        pos = self.parser.parse_position(args[0])
        if not pos:
            print(f"Error: 无效的位置格式: {args[0]}")
            return
        
        line, col = pos
        text = self.parser.unescape_string(args[1])
        
        try:
            self.workspace.execute_on_active('insert', line, col, text)
            print("OK")
            
            # Log the command
            self.workspace.log_command(f'insert {args[0]} "{args[1]}"')
        except EditorException as e:
            print(f"Error: {str(e)}")
    
    def cmd_delete(self, args: list) -> None:
        """Delete characters."""
        if len(args) < 2:
            print("Error: 参数不足")
            print("用法: delete <line:col> <len>")
            return
        
        pos = self.parser.parse_position(args[0])
        if not pos:
            print(f"Error: 无效的位置格式: {args[0]}")
            return
        
        try:
            length = int(args[1])
        except ValueError:
            print(f"Error: 无效的长度: {args[1]}")
            return
        
        line, col = pos
        
        try:
            self.workspace.execute_on_active('delete', line, col, length)
            print("OK")
            
            # Log the command
            self.workspace.log_command(f'delete {args[0]} {args[1]}')
        except EditorException as e:
            print(f"Error: {str(e)}")
    
    def cmd_replace(self, args: list) -> None:
        """Replace characters."""
        if len(args) < 3:
            print("Error: 参数不足")
            print("用法: replace <line:col> <len> \"text\"")
            return
        
        pos = self.parser.parse_position(args[0])
        if not pos:
            print(f"Error: 无效的位置格式: {args[0]}")
            return
        
        try:
            length = int(args[1])
        except ValueError:
            print(f"Error: 无效的长度: {args[1]}")
            return
        
        line, col = pos
        text = self.parser.unescape_string(args[2])
        
        try:
            self.workspace.execute_on_active('replace', line, col, length, text)
            print("OK")
            
            # Log the command
            self.workspace.log_command(f'replace {args[0]} {args[1]} "{args[2]}"')
        except EditorException as e:
            print(f"Error: {str(e)}")
    
    def cmd_show(self, args: list) -> None:
        """Show file content."""
        start_line = None
        end_line = None
        
        if args:
            range_val = self.parser.parse_range(args[0])
            if range_val:
                start_line, end_line = range_val
            else:
                print(f"Error: 无效的范围格式: {args[0]}")
                return
        
        try:
            result = self.workspace.execute_on_active('show', start_line, end_line)
            if result:
                print(result)
            else:
                print("(空文件)")
        except EditorException as e:
            print(f"Error: {str(e)}")
    
    # Command Handlers - Logging Commands
    
    def cmd_log_on(self, args: list) -> None:
        """Enable logging."""
        filepath = args[0] if args else None
        result = self.workspace.enable_log(filepath)
        print(result)
        
        # Log the command
        cmd_str = f"log-on {filepath}" if filepath else "log-on"
        self.workspace.log_command(cmd_str)
    
    def cmd_log_off(self, args: list) -> None:
        """Disable logging."""
        filepath = args[0] if args else None
        result = self.workspace.disable_log(filepath)
        print(result)
        
        # Log the command
        cmd_str = f"log-off {filepath}" if filepath else "log-off"
        self.workspace.log_command(cmd_str)
    
    def cmd_log_show(self, args: list) -> None:
        """Show log content."""
        filepath = args[0] if args else None
        result = self.workspace.show_log(filepath)
        print(result)


def main():
    """Main entry point."""
    cli = TextEditorCLI()
    cli.start()


if __name__ == '__main__':
    main()

