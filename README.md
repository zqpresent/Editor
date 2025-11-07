# 文本编辑器 - Lab1

一个基于命令行的文本编辑器，支持多文件管理、撤销/重做、日志记录和状态持久化功能。

## ✨ 特性

- 📝 **文本编辑**：支持追加、插入、删除、替换等基本操作
- 🔄 **撤销/重做**：完整的 undo/redo 支持（基于命令模式）
- 📂 **多文件管理**：同时打开和编辑多个文件
- 📊 **日志记录**：自动记录所有操作，支持日志开关
- 💾 **状态持久化**：保存工作区状态，下次启动自动恢复
- 🌳 **目录树显示**：查看文件系统结构
- 🎨 **设计模式实践**：Command、Observer、Memento 等模式的综合应用

## 📁 项目结构

```
Editor/
├── main.py                  # 程序入口
├── requirements.txt         # 项目依赖（无外部依赖）
├── README.md               # 本文档
├── USER_GUIDE.md           # 用户使用手册
├── DESIGN.md               # 设计文档
├── requirements/           # 需求文档
└── src/                    # 源代码
    ├── main.py            # CLI 主程序
    ├── workspace.py       # 工作区管理（核心）
    ├── command/           # 命令模式实现
    │   ├── command.py     # 命令基类
    │   └── edit_commands.py  # 编辑命令
    ├── editor/            # 编辑器模块
    │   ├── editor.py      # 编辑器基类
    │   └── text_editor.py # 文本编辑器
    ├── logger/            # 日志模块（观察者模式）
    │   ├── observer.py    # 观察者接口
    │   └── logger.py      # 日志实现
    ├── storage/           # 存储模块
    │   ├── memento.py     # 状态持久化（备忘录模式）
    │   └── file_manager.py # 文件管理工具
    └── utils/             # 工具类
        ├── exceptions.py  # 自定义异常
        └── parser.py      # 命令解析器
```

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 无需额外依赖，仅使用标准库

### 安装和运行

```bash
# 克隆或下载项目
cd Editor

# 运行编辑器
python main.py
```

### 基本使用示例

```bash
# 启动后会看到提示符
> load test.txt              # 加载或创建文件
> append "Hello World"       # 追加一行文本
> append "This is line 2"    # 再追加一行
> show                       # 查看内容
> save                       # 保存文件
> exit                       # 退出（自动保存工作区状态）
```

## 📖 命令速查

### 工作区命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `load <file>` | 加载文件 | `load essay.txt` |
| `save [file\|all]` | 保存文件 | `save` / `save all` |
| `init <file> [with-log]` | 创建新文件 | `init note.txt with-log` |
| `close [file]` | 关闭文件 | `close` |
| `edit <file>` | 切换活动文件 | `edit essay.txt` |
| `editor-list` | 显示打开的文件 | `editor-list` |
| `dir-tree [path]` | 显示目录树 | `dir-tree src` |
| `undo` | 撤销操作 | `undo` |
| `redo` | 重做操作 | `redo` |
| `exit` | 退出程序 | `exit` |

### 编辑命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `append "text"` | 追加文本 | `append "new line"` |
| `insert <line:col> "text"` | 插入文本 | `insert 1:5 "word"` |
| `delete <line:col> <len>` | 删除字符 | `delete 1:1 5` |
| `replace <line:col> <len> "text"` | 替换文本 | `replace 1:1 4 "new"` |
| `show [start:end]` | 显示内容 | `show` / `show 1:10` |

### 日志命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `log-on [file]` | 启用日志 | `log-on` |
| `log-off [file]` | 关闭日志 | `log-off` |
| `log-show [file]` | 查看日志 | `log-show` |

## 🏗️ 设计模式应用

### 1. Command Pattern（命令模式）
- **位置**：`src/command/`
- **作用**：实现所有编辑操作的 undo/redo 功能
- **实现**：
  - `Command` 抽象基类定义 `execute()`, `undo()`, `redo()` 接口
  - `AppendCommand`, `InsertCommand`, `DeleteCommand`, `ReplaceCommand` 等具体命令
  - 每个 Editor 维护独立的 undo/redo 栈

### 2. Observer Pattern（观察者模式）
- **位置**：`src/logger/observer.py`, `src/workspace.py`
- **作用**：日志模块监听命令执行事件
- **实现**：
  - `Workspace` 作为 Subject，发布事件
  - `Logger` 作为 Observer，接收并记录事件
  - 事件类型：`command_executed`, `file_loaded` 等

### 3. Memento Pattern（备忘录模式）
- **位置**：`src/storage/memento.py`
- **作用**：工作区状态的保存和恢复
- **实现**：
  - `WorkspaceMemento` 保存：打开的文件列表、活动文件、修改状态、日志开关
  - 序列化为 JSON 保存到 `.workspace.json`
  - 程序启动时自动恢复上次状态

### 4. Singleton Pattern（单例模式）
- **位置**：`src/workspace.py`
- **作用**：确保全局只有一个 Workspace 实例
- **实现**：使用 `__new__` 方法实现单例

## 📝 高级特性

### 自动日志记录
如果文件第一行是 `# log`，加载时会自动启用日志记录：
```bash
> init todo.txt with-log    # 创建带日志的文件
> append "Task 1"           # 所有操作都会被记录
> log-show                  # 查看日志
```

### 多文件协作
```bash
> load file1.txt           # 打开第一个文件
> append "content 1"       # 编辑
> load file2.txt           # 打开第二个文件（成为活动文件）
> append "content 2"       # 编辑第二个文件
> edit file1.txt           # 切换回第一个文件
> editor-list              # 查看所有打开的文件
> save all                 # 保存所有文件
```

### 状态持久化
```bash
# 第一次使用
> load project.txt
> append "some work"
> exit                     # 退出，自动保存状态

# 下次启动
> python main.py           # 自动恢复 project.txt
```

## 🔧 技术细节

### 文件编码
- 所有文件使用 **UTF-8** 编码
- 支持中文和特殊字符

### 行列编号
- 行号和列号**从 1 开始**计数
- 内部存储使用 0-based 索引，对外接口自动转换

### 数据结构
- 文本内容使用 `List[String]` 存储，每个元素是一行
- 便于通过行号快速定位和操作

### 日志格式
日志保存在 `.filename.log` 文件中：
```
session start at 20251107 14:30:25
20251107 14:30:30 load test.txt
20251107 14:30:45 append "line 1"
20251107 14:31:00 save
```

## 🧪 测试

项目包含完整的模块化设计，便于单元测试。主要测试点：

1. **Command 模式**：测试每个命令的 execute/undo/redo
2. **Editor 功能**：测试插入、删除、替换等边界情况
3. **Observer 模式**：测试事件通知机制
4. **Memento 模式**：测试状态保存和恢复

## 📚 更多文档

- [用户使用手册](USER_GUIDE.md) - 详细的命令说明和使用场景
- [设计文档](DESIGN.md) - 架构设计和设计模式详解

## 🤝 贡献

这是一个课程实验项目（2025 Fall），用于学习和实践设计模式。

## 📄 许可

本项目仅用于教学目的。
