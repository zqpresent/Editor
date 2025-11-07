# 用户使用手册

本手册提供文本编辑器的详细使用说明和实用场景示例。

## 目录
- [快速入门](#快速入门)
- [命令详解](#命令详解)
  - [工作区命令](#工作区命令)
  - [文本编辑命令](#文本编辑命令)
  - [日志命令](#日志命令)
- [使用场景](#使用场景)
- [常见问题](#常见问题)

## 快速入门

### 第一次使用

```bash
$ cd Editor
$ python main.py

欢迎使用文本编辑器！
输入 'help' 查看可用命令

> help                      # 查看帮助
> load my_first_file.txt    # 创建并打开文件
> append "Hello World"      # 添加第一行
> show                      # 查看内容
> save                      # 保存文件
> exit                      # 退出
```

### 基本编辑流程

1. **打开/创建文件**：`load filename.txt`
2. **编辑内容**：使用 `append`, `insert`, `delete`, `replace`
3. **查看内容**：`show`
4. **保存文件**：`save`

## 命令详解

### 工作区命令

#### `load <file>` - 加载文件

**功能**：加载现有文件或创建新文件

**示例**：
```bash
> load essay.txt
Loaded: essay.txt           # 文件存在

> load new_file.txt
文件不存在，已创建新缓冲区: new_file.txt  # 文件不存在
```

**说明**：
- 加载的文件自动成为当前活动文件
- 如果文件不存在，会创建一个空白缓冲区
- 如果首行是 `# log`，会自动启用日志记录

---

#### `save [file|all]` - 保存文件

**功能**：保存当前文件、指定文件或所有文件

**示例**：
```bash
> save                      # 保存当前活动文件
Saved: essay.txt

> save report.txt          # 保存指定文件
Saved: report.txt

> save all                 # 保存所有打开的文件
Saved: essay.txt
Saved: report.txt
```

---

#### `init <file> [with-log]` - 创建新缓冲区

**功能**：创建一个新的文件缓冲区

**示例**：
```bash
> init todo.txt
已创建新缓冲区: todo.txt

> init diary.txt with-log
已创建新缓冲区: diary.txt (日志已启用)
```

**说明**：
- `with-log` 选项会在文件首行自动添加 `# log` 并启用日志
- 新创建的文件需要 `save` 才会写入磁盘

---

#### `close [file]` - 关闭文件

**功能**：关闭当前文件或指定文件

**示例**：
```bash
> close                    # 关闭当前活动文件
文件已修改: essay.txt
是否保存? (y/n): y
Saved: essay.txt
Closed: essay.txt

> close report.txt         # 关闭指定文件
Closed: report.txt
```

**说明**：
- 如果文件有未保存的修改，会提示是否保存
- 关闭当前活动文件后，会自动切换到其他已打开的文件

---

#### `edit <file>` - 切换活动文件

**功能**：切换到另一个已打开的文件

**示例**：
```bash
> load file1.txt
> load file2.txt
> edit file1.txt           # 切换回 file1.txt
已切换到: file1.txt
```

**说明**：
- 文件必须已经通过 `load` 或 `init` 打开
- 切换后，所有编辑命令对新的活动文件生效

---

#### `editor-list` - 显示文件列表

**功能**：显示所有打开的文件及其状态

**示例**：
```bash
> editor-list
> file1.txt*               # > 表示当前活动文件，* 表示已修改
  file2.txt
  file3.txt*
```

**说明**：
- `>` 前缀：当前活动文件
- `*` 后缀：文件有未保存的修改

---

#### `dir-tree [path]` - 显示目录树

**功能**：以树形结构显示目录内容

**示例**：
```bash
> dir-tree
Editor
├── main.py
├── requirements.txt
├── README.md
└── src
    ├── main.py
    ├── workspace.py
    ├── command
    │   ├── command.py
    │   └── edit_commands.py
    └── editor
        ├── editor.py
        └── text_editor.py

> dir-tree src/command     # 显示指定目录
command
├── command.py
└── edit_commands.py
```

---

#### `undo` / `redo` - 撤销/重做

**功能**：撤销或重做编辑操作

**示例**：
```bash
> append "Line 1"
OK
> append "Line 2"
OK
> undo
Undo: append "Line 2"
> undo
Undo: append "Line 1"
> redo
Redo: append "Line 1"
```

**说明**：
- 只有编辑命令（`append`, `insert`, `delete`, `replace`）可以撤销
- 每个文件有独立的 undo/redo 栈
- 查看命令（`show`, `editor-list` 等）不会进入撤销栈

---

#### `exit` - 退出程序

**功能**：退出编辑器

**示例**：
```bash
> exit
以下文件有未保存的更改:
  essay.txt
保存 essay.txt? (y/n): y
Saved: essay.txt
工作区状态已保存。再见！
```

**说明**：
- 会检查所有未保存的文件并逐个询问
- 自动保存工作区状态到 `.workspace.json`
- 下次启动会自动恢复工作区

---

### 文本编辑命令

#### `append "text"` - 追加文本

**功能**：在文件末尾追加一行

**示例**：
```bash
> show
1: Hello

> append "World"
OK

> show
1: Hello
2: World
```

---

#### `insert <line:col> "text"` - 插入文本

**功能**：在指定位置插入文本

**格式说明**：
- `line:col` - 行号:列号（从1开始）
- 列号表示插入到第几个字符**之前**

**示例**：
```bash
> show
1: Hello World

> insert 1:7 "Beautiful "
OK

> show
1: Hello Beautiful World

> insert 1:1 "Say: "
OK

> show
1: Say: Hello Beautiful World
```

**多行插入**：
```bash
> insert 1:1 "Line1\nLine2\nLine3"
OK

> show
1: Line1
2: Line2
3: Line3
```

**错误处理**：
```bash
> insert 10:1 "text"
Error: 行号越界: 10

> insert 1:100 "text"
Error: 列号越界: 100
```

---

#### `delete <line:col> <len>` - 删除字符

**功能**：从指定位置删除指定数量的字符

**示例**：
```bash
> show
1: Hello World

> delete 1:7 6
OK

> show
1: Hello 

> delete 1:1 5
OK

> show
1:  
```

**说明**：
- 删除操作**不能跨行**
- 删除长度不能超过该行剩余字符数

**错误处理**：
```bash
> delete 1:1 100
Error: 删除长度超出行尾: 剩余5个字符，尝试删除100个
```

---

#### `replace <line:col> <len> "text"` - 替换文本

**功能**：删除指定长度的字符，然后插入新文本

**示例**：
```bash
> show
1: Hello World

> replace 1:1 5 "Hi"
OK

> show
1: Hi World

> replace 1:4 5 "Everyone"
OK

> show
1: Hi Everyone
```

**说明**：
- 等同于先 `delete` 再 `insert`
- 新文本长度可以与删除长度不同
- 替换文本可以为空字符串（效果等同于删除）

---

#### `show [start:end]` - 显示内容

**功能**：显示文件内容

**示例**：
```bash
> show                     # 显示全部内容
1: Line 1
2: Line 2
3: Line 3
4: Line 4
5: Line 5

> show 2:4                 # 显示第2-4行
2: Line 2
3: Line 3
4: Line 4
```

---

### 日志命令

#### `log-on [file]` - 启用日志

**功能**：为文件启用日志记录

**示例**：
```bash
> log-on                   # 为当前文件启用日志
已启用日志: essay.txt

> log-on report.txt        # 为指定文件启用日志
已启用日志: report.txt
```

**说明**：
- 启用后，所有操作会记录到 `.filename.log` 文件
- 日志文件在同目录下，以 `.` 开头（隐藏文件）

---

#### `log-off [file]` - 关闭日志

**功能**：关闭日志记录

**示例**：
```bash
> log-off
已关闭日志: essay.txt
```

**说明**：
- 关闭日志不会删除已有的日志文件

---

#### `log-show [file]` - 显示日志

**功能**：查看日志内容

**示例**：
```bash
> log-show
session start at 20251107 14:30:25
20251107 14:30:30 load essay.txt
20251107 14:30:45 append "Introduction"
20251107 14:31:00 insert 1:1 "Chapter 1: "
20251107 14:31:20 save
```

---

## 使用场景

### 场景1：编写文章

```bash
> init article.txt with-log
> append "# My Article"
> append ""
> append "## Introduction"
> append "This is the introduction."
> show
1: # My Article
2: 
3: ## Introduction
4: This is the introduction.
> save
> exit
```

### 场景2：多文件项目

```bash
# 编辑多个相关文件
> load main.py
> load utils.py
> load config.py

# 在不同文件间切换
> edit main.py
> append "import utils"
> edit utils.py
> append "def helper():"
> append "    pass"

# 查看所有打开的文件
> editor-list
> main.py*
  utils.py*
  config.py

# 保存所有文件
> save all
```

### 场景3：代码重构

```bash
> load code.py
> show
1: def old_function_name():
2:     return "result"

> replace 1:5 17 "new_function_name"
OK

> show
1: def new_function_name():
2:     return "result"

# 如果改错了，可以撤销
> undo
Undo: replace 1:5 17 "new_function_name"

> show
1: def old_function_name():
2:     return "result"
```

### 场景4：待办事项管理

```bash
> init todo.txt with-log
> append "# TODO List"
> append "- [ ] Task 1"
> append "- [ ] Task 2"
> append "- [ ] Task 3"

# 标记完成
> replace 2:3 3 "[x]"
OK

> show
1: # TODO List
2: - [x] Task 1
3: - [ ] Task 2
4: - [ ] Task 3

> save
> log-show                 # 查看所有操作历史
```

## 常见问题

### Q: 如何处理包含空格的文本？
A: 使用双引号包裹文本：
```bash
> append "This is a text with    multiple   spaces"
```

### Q: 如何插入换行符？
A: 在文本中使用 `\n`：
```bash
> insert 1:1 "Line 1\nLine 2\nLine 3"
```

### Q: 行号和列号从0还是1开始？
A: 从 **1** 开始。例如第一行第一个字符是 `1:1`。

### Q: 删除命令可以跨行吗？
A: 不可以。删除操作只能在单行内进行。

### Q: 如何恢复误删的内容？
A: 使用 `undo` 命令立即撤销：
```bash
> delete 1:1 100
Error: 删除长度超出行尾...
> delete 1:1 10
OK
> undo                     # 恢复删除
```

### Q: 日志文件保存在哪里？
A: 保存在与源文件相同的目录，文件名为 `.filename.log`（隐藏文件）。

### Q: 如何查看隐藏的日志文件？
A: 在终端使用 `ls -la` 命令，或在编辑器中使用 `log-show` 命令。

### Q: 工作区状态保存在哪里？
A: 保存在当前目录的 `.workspace.json` 文件中。

### Q: 可以同时打开多少个文件？
A: 理论上无限制，取决于系统内存。

### Q: 如何查看项目目录结构？
A: 使用 `dir-tree` 命令：
```bash
> dir-tree .
> dir-tree src
```

### Q: 编辑器支持哪些文件类型？
A: 目前支持纯文本文件（`.txt`）。Lab2 将添加 XML 编辑器。

### Q: 文件编码是什么？
A: 统一使用 UTF-8 编码，支持中文和特殊字符。

---

## 快捷技巧

1. **快速创建带日志的文件**：
   ```bash
   > init myfile.txt with-log
   ```

2. **批量保存**：
   ```bash
   > save all
   ```

3. **查看当前状态**：
   ```bash
   > editor-list
   ```

4. **快速撤销多步操作**：
   ```bash
   > undo
   > undo
   > undo
   ```

5. **从历史恢复工作**：
   ```bash
   # 只需启动程序，工作区自动恢复
   $ python main.py
   ```

---

如有其他问题，请参考 [README.md](README.md) 或 [DESIGN.md](DESIGN.md)。

