# 设计文档

本文档详细说明文本编辑器的架构设计、设计模式应用和技术实现。

## 目录
- [系统架构](#系统架构)
- [设计模式](#设计模式)
- [模块详解](#模块详解)
- [数据流](#数据流)
- [扩展性设计](#扩展性设计)

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────┐
│      CLI Interface (main.py)         │  ← 用户交互层
│    - 命令解析 (CommandParser)        │
│    - 用户输入/输出                    │
└──────────────┬──────────────────────┘
               │ 命令调用
┌──────────────▼──────────────────────┐
│       Workspace (核心协调器)         │  ← 业务逻辑层
│    - 管理多个 Editor                 │
│    - Subject (Observable)           │
│    - 状态持久化 (Memento)            │
└─────┬────────────────────────┬──────┘
      │                        │
      │ 管理                   │ 通知事件
      │                        │
┌─────▼─────┐          ┌──────▼───────┐
│  Editors  │          │   Observers  │
│           │          │              │
│  Editor   │          │   Logger     │
│  (抽象)   │          │  (Observer)  │
│     ↑     │          └──────────────┘
│     │     │
│ TextEditor│
│  + undo   │
│  + redo   │
└─────┬─────┘
      │ 执行命令
      │
┌─────▼──────────────────────────────┐
│    Command Pattern                 │  ← 命令层
│  - AppendCommand                   │
│  - InsertCommand                   │
│  - DeleteCommand                   │
│  - ReplaceCommand                  │
└────────────────────────────────────┘
```

### 分层说明

1. **表示层（Presentation Layer）**
   - `main.py` + `CommandParser`
   - 职责：接收用户输入，解析命令，显示输出

2. **业务逻辑层（Business Logic Layer）**
   - `Workspace` + `Editor`
   - 职责：协调各模块，管理业务规则

3. **命令层（Command Layer）**
   - Command 接口及具体命令类
   - 职责：封装操作，支持 undo/redo

4. **基础设施层（Infrastructure Layer）**
   - `FileManager`, `Logger`, `Memento`
   - 职责：文件 I/O、日志记录、状态持久化

---

## 设计模式

### 1. Command Pattern（命令模式）

#### 意图
将请求封装为对象，从而支持撤销、重做、日志记录等功能。

#### 结构
```
        Command (接口)
    ┌──────┴──────────┐
    │                 │
EditCommand      WorkspaceCommand
    │
    ├── AppendCommand
    ├── InsertCommand
    ├── DeleteCommand
    └── ReplaceCommand
```

#### 实现细节

**Command 接口**：
```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: pass
    
    @abstractmethod
    def undo(self) -> None: pass
    
    @abstractmethod
    def redo(self) -> None: pass
    
    @abstractmethod
    def get_description(self) -> str: pass
```

**具体命令示例 - AppendCommand**：
```python
class AppendCommand(EditCommand):
    def __init__(self, editor: TextEditor, text: str):
        super().__init__(editor)
        self.text = text
        self.line_number = None
    
    def execute(self) -> None:
        self.editor.content.append(self.text)
        self.line_number = len(self.editor.content)
        self.editor.mark_modified()
    
    def undo(self) -> None:
        if self.line_number:
            self.editor.content.pop()
            self.editor.mark_modified()
```

#### 优势
- ✅ 解耦命令发送者和接收者
- ✅ 支持撤销/重做功能
- ✅ 易于添加新命令
- ✅ 可以记录命令历史（用于日志）

#### 应用位置
- `src/command/command.py` - 命令接口
- `src/command/edit_commands.py` - 具体编辑命令
- `src/editor/editor.py` - 命令执行和 undo/redo 栈管理

---

### 2. Observer Pattern（观察者模式）

#### 意图
定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖者都会收到通知。

#### 结构
```
     Subject               Observer
   (Workspace)            (Logger)
        │                     ↑
        │                     │
        └─────── notify ──────┘
```

#### 实现细节

**Subject 接口**：
```python
class Subject:
    def __init__(self):
        self._observers: list[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def notify(self, event_type: str, data: Dict) -> None:
        for observer in self._observers:
            observer.update(event_type, data)
```

**Observer 接口**：
```python
class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        pass
```

**Logger 实现**：
```python
class Logger(Observer):
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == 'command_executed':
            self._log_command(data)
```

#### 事件类型
- `command_executed`: 命令执行事件
- `file_loaded`: 文件加载事件

#### 优势
- ✅ 松耦合：Subject 不需要知道 Observer 的具体实现
- ✅ 可扩展：易于添加新的观察者（如统计模块、备份模块）
- ✅ 动态订阅：运行时可以添加/删除观察者

#### 应用位置
- `src/logger/observer.py` - Observer 接口和 Subject 基类
- `src/logger/logger.py` - Logger 实现
- `src/workspace.py` - Workspace 继承 Subject

---

### 3. Memento Pattern（备忘录模式）

#### 意图
在不破坏封装性的前提下，捕获和恢复对象的内部状态。

#### 结构
```
  Workspace (Originator)
      ↓ create
  WorkspaceMemento
      ↓ save to
  .workspace.json
```

#### 实现细节

**Memento 类**：
```python
class WorkspaceMemento:
    def __init__(self):
        self.open_files: List[str] = []
        self.active_file: Optional[str] = None
        self.modified_files: Set[str] = set()
        self.log_enabled_files: Set[str] = set()
    
    def to_dict(self) -> dict:
        return {
            'open_files': self.open_files,
            'active_file': self.active_file,
            'modified_files': list(self.modified_files),
            'log_enabled_files': list(self.log_enabled_files)
        }
    
    def save_to_file(self, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
```

**Workspace 状态保存/恢复**：
```python
# 保存状态
def save_state(self) -> None:
    memento = WorkspaceMemento()
    memento.open_files = list(self.editors.keys())
    memento.active_file = self.active_editor.filepath if self.active_editor else None
    memento.save_to_file('.workspace.json')

# 恢复状态
def restore_state(self) -> None:
    memento = WorkspaceMemento.load_from_file('.workspace.json')
    if memento:
        for filepath in memento.open_files:
            self.load_file(filepath)
        if memento.active_file:
            self.active_editor = self.editors[memento.active_file]
```

#### 持久化内容
- ✅ 打开的文件列表
- ✅ 当前活动文件
- ✅ 文件修改状态
- ✅ 日志开关状态
- ❌ undo/redo 历史（不持久化）

#### 优势
- ✅ 封装性：外部不能访问内部状态
- ✅ 简化 Originator：状态管理逻辑独立
- ✅ 持久化：可以保存到磁盘

#### 应用位置
- `src/storage/memento.py` - Memento 实现
- `src/workspace.py` - save_state() / restore_state()

---

### 4. Singleton Pattern（单例模式）

#### 意图
确保一个类只有一个实例，并提供全局访问点。

#### 实现细节

```python
class Workspace(Subject):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.editors = {}
            self.active_editor = None
            self.initialized = True
```

#### 为什么使用单例
- 全局唯一的工作区状态
- 避免多个 Workspace 实例导致状态不一致
- 方便全局访问

#### 应用位置
- `src/workspace.py` - Workspace 类

---

### 5. Strategy Pattern（策略模式）- 为扩展预留

#### 意图
为 Lab2 的 XML 编辑器扩展做准备。

#### 结构（预期）
```
      Editor (抽象)
         ↑
    ┌────┴────┐
    │         │
TextEditor  XMLEditor
```

#### 当前实现
```python
# 编辑器工厂（预留）
def create_editor(filepath: str) -> Editor:
    if filepath.endswith('.txt'):
        return TextEditor(filepath)
    elif filepath.endswith('.xml'):
        return XMLEditor(filepath)  # Lab2 实现
    else:
        return TextEditor(filepath)  # 默认文本编辑器
```

---

## 模块详解

### Workspace（工作区）

**职责**：
1. 管理所有打开的 Editor 实例
2. 维护当前活动 Editor
3. 协调命令执行
4. 发布事件给观察者
5. 状态持久化

**核心数据结构**：
```python
self.editors: Dict[str, Editor] = {}       # 文件路径 -> Editor
self.active_editor: Optional[Editor] = None # 当前活动编辑器
self.logger: Logger                         # 日志观察者
```

**关键方法**：
- `load_file()` - 加载文件
- `save_file()` - 保存文件
- `execute_on_active()` - 在活动编辑器上执行操作
- `save_state()` / `restore_state()` - 状态持久化
- `notify()` - 通知观察者（继承自 Subject）

---

### Editor（编辑器）

**抽象基类**，定义所有编辑器的通用接口。

**核心功能**：
1. 文件 I/O（`load_from_file`, `save_to_file`）
2. 修改状态管理（`is_modified`）
3. 命令执行（`execute_command`）
4. Undo/Redo（`undo`, `redo`）

**Undo/Redo 实现**：
```python
def execute_command(self, command) -> None:
    command.execute()
    self.undo_stack.append(command)
    self.redo_stack.clear()  # 新操作清空 redo 栈

def undo(self) -> Optional[str]:
    if self.undo_stack:
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return command.get_description()
    return None
```

---

### TextEditor（文本编辑器）

**数据结构**：
```python
self.content: List[str] = []  # 每个元素是一行
```

**为什么使用行数组**：
1. 快速定位：通过行号直接索引
2. 便于操作：插入/删除行很高效
3. 内存效率：不需要频繁拼接大字符串

**编辑操作**：
```python
def append(self, text: str):
    command = AppendCommand(self, text)
    self.execute_command(command)

def insert(self, line: int, col: int, text: str):
    command = InsertCommand(self, line, col, text)
    self.execute_command(command)
```

**Show 操作**：
```python
def show(self, start_line: int = None, end_line: int = None) -> str:
    result = []
    for i in range(start_line - 1, end_line):
        result.append(f"{i + 1}: {self.content[i]}")
    return '\n'.join(result)
```

---

### Logger（日志记录器）

**职责**：
1. 监听 Workspace 事件
2. 记录命令执行
3. 管理日志文件

**日志文件命名**：
```
filename.txt  →  .filename.txt.log
```

**日志格式**：
```
session start at 20251107 14:30:25
20251107 14:30:30 load test.txt
20251107 14:30:45 append "line 1"
```

**启用策略**：
1. 手动启用：`log-on` 命令
2. 自动启用：文件首行是 `# log`

---

### CommandParser（命令解析器）

**职责**：解析用户输入的命令字符串

**功能**：
1. 分割命令和参数
2. 处理引号内的空格
3. 解析 `line:col` 格式
4. 转义字符处理（`\n`, `\t` 等）

**示例**：
```python
parse('append "hello world"')
→ ('append', ['hello world'])

parse('insert 1:5 "text"')
→ ('insert', ['1:5', 'text'])

parse_position('1:5')
→ (1, 5)
```

---

## 数据流

### 命令执行流程

```
1. 用户输入
   "append \"Hello\""
        ↓
2. CommandParser 解析
   command: 'append'
   args: ['Hello']
        ↓
3. CLI 路由到处理函数
   cmd_append(['Hello'])
        ↓
4. Workspace 执行
   workspace.execute_on_active('append', 'Hello')
        ↓
5. Editor 创建命令
   command = AppendCommand(self, 'Hello')
   self.execute_command(command)
        ↓
6. 命令执行
   command.execute()
   → 修改 content
   → 标记 modified
   → 加入 undo_stack
        ↓
7. 事件通知
   workspace.notify('command_executed', {...})
        ↓
8. Logger 记录
   logger.update('command_executed', {...})
   → 写入 .filename.log
        ↓
9. 返回结果
   "OK"
```

### 文件保存流程

```
1. 用户输入 "save"
        ↓
2. Workspace.save_file()
        ↓
3. Editor.save_to_file()
   → 将 List[String] 用 \n 连接
   → 写入文件 (UTF-8)
        ↓
4. 清除 modified 标记
        ↓
5. 通知观察者
        ↓
6. Logger 记录 "save"
```

### 状态恢复流程

```
1. 程序启动
        ↓
2. Workspace.restore_state()
        ↓
3. 读取 .workspace.json
        ↓
4. 解析 WorkspaceMemento
   {
     "open_files": ["file1.txt", "file2.txt"],
     "active_file": "file1.txt",
     "log_enabled_files": ["file1.txt"]
   }
        ↓
5. 依次加载文件
   for filepath in open_files:
       workspace.load_file(filepath)
        ↓
6. 恢复活动文件
   workspace.active_editor = editors[active_file]
        ↓
7. 恢复日志状态
   for filepath in log_enabled_files:
       logger.enable_logging(filepath)
```

---

## 扩展性设计

### 为 Lab2 预留的扩展点

#### 1. 新增 XMLEditor

**步骤**：
1. 创建 `XMLEditor` 类继承 `Editor`
2. 实现特定的 XML 操作命令
3. 在 Workspace 中添加编辑器类型判断

```python
class XMLEditor(Editor):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.tree = None  # XML DOM tree
    
    def insert_element(self, parent: str, tag: str, text: str):
        command = InsertElementCommand(self, parent, tag, text)
        self.execute_command(command)
```

#### 2. 扩展命令系统

添加新的命令类：
```python
class InsertElementCommand(EditCommand):
    def __init__(self, editor, parent, tag, text):
        self.editor = editor
        self.parent = parent
        self.tag = tag
        self.text = text
    
    def execute(self):
        # XML 插入逻辑
        pass
    
    def undo(self):
        # XML 删除逻辑
        pass
```

#### 3. 扩展观察者

可以添加新的观察者：
- **StatisticsObserver**: 统计编辑次数、行数变化等
- **BackupObserver**: 自动备份文件
- **NotificationObserver**: 发送通知（如文件保存成功）

示例：
```python
class StatisticsObserver(Observer):
    def __init__(self):
        self.command_count = {}
    
    def update(self, event_type: str, data: Dict):
        if event_type == 'command_executed':
            cmd = data['command'].split()[0]
            self.command_count[cmd] = self.command_count.get(cmd, 0) + 1
```

---

## 技术细节

### 行列编号转换

```python
# 用户接口：1-based
user_line = 1, user_col = 1

# 内部实现：0-based
line_idx = user_line - 1  # 0
col_idx = user_col - 1    # 0

# 示例
content = ["Hello World"]
# 用户想在 1:7 插入
line_idx = 0
col_idx = 6
content[0] = content[0][:6] + "Beautiful " + content[0][6:]
# Result: "Hello Beautiful World"
```

### 多行插入实现

```python
def insert_multiline(self, line: int, col: int, text: str):
    if '\n' in text:
        lines = text.split('\n')
        current_line = self.content[line - 1]
        
        # 第一行：原内容[:col] + 插入的第一行
        new_first = current_line[:col-1] + lines[0]
        
        # 中间行：完整的新行
        middle_lines = lines[1:-1]
        
        # 最后一行：插入的最后一行 + 原内容[col:]
        new_last = lines[-1] + current_line[col-1:]
        
        # 替换和插入
        self.content[line-1] = new_first
        for i, l in enumerate(middle_lines + [new_last], start=1):
            self.content.insert(line-1 + i, l)
```

### 错误处理策略

1. **EditorException 基类**：所有自定义异常的基类
2. **具体异常类**：细分不同的错误类型
3. **捕获和提示**：在 CLI 层捕获并友好提示

```python
try:
    editor.insert(1, 100, "text")
except ColumnOutOfRangeException as e:
    print(f"Error: {str(e)}")
```

---

## 性能考虑

### 时间复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| append | O(1) | 列表尾部追加 |
| insert (单行) | O(n) | 字符串拼接 |
| delete | O(n) | 字符串切片 |
| show | O(k) | k = 显示的行数 |
| undo/redo | O(1) | 栈操作 |
| save | O(n) | n = 总字符数 |

### 空间复杂度

- 文本存储：O(n) - n = 总字符数
- Undo 栈：O(m * k) - m = 命令数，k = 每个命令的状态大小
- 日志：O(l) - l = 日志条数

### 优化策略

1. **延迟加载**：大文件可以分块读取（当前未实现）
2. **Undo 栈限制**：可以限制 undo 栈大小（当前未实现）
3. **日志异步写入**：避免阻塞主线程（当前同步写入）

---

## 测试策略

### 单元测试

1. **Command 测试**
   ```python
   def test_append_command():
       editor = TextEditor("test.txt")
       cmd = AppendCommand(editor, "line 1")
       cmd.execute()
       assert editor.content == ["line 1"]
       cmd.undo()
       assert editor.content == []
   ```

2. **Editor 测试**
   ```python
   def test_insert_boundary():
       editor = TextEditor("test.txt")
       editor.content = ["Hello"]
       editor.insert(1, 6, " World")  # 边界情况
       assert editor.content == ["Hello World"]
   ```

3. **Observer 测试**
   ```python
   def test_logger_notification():
       workspace = Workspace()
       logger = workspace.logger
       # 模拟事件
       workspace.notify('command_executed', {...})
       # 验证日志文件
   ```

### 集成测试

测试完整的命令流程：
```python
def test_full_workflow():
    cli = TextEditorCLI()
    cli.process_command("load test.txt")
    cli.process_command('append "line 1"')
    cli.process_command("save")
    cli.process_command("exit")
    # 验证文件内容
```

---

## 总结

本项目通过合理应用设计模式，实现了一个结构清晰、易于扩展的文本编辑器：

- **Command 模式**：实现了强大的 undo/redo 功能
- **Observer 模式**：实现了灵活的日志记录机制
- **Memento 模式**：实现了状态持久化
- **Singleton 模式**：确保了工作区的唯一性

代码遵循 SOLID 原则，各模块职责清晰，为 Lab2 的扩展打下了良好基础。

