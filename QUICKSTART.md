# 快速开始指南

## 5分钟上手文本编辑器

### 步骤 1：运行程序

```bash
cd Editor
python main.py
```

你会看到：
```
欢迎使用文本编辑器！
输入 'help' 查看可用命令

>
```

### 步骤 2：创建第一个文件

```bash
> load hello.txt
文件不存在，已创建新缓冲区: hello.txt
```

### 步骤 3：添加内容

```bash
> append "Hello, World!"
OK

> append "This is my first file."
OK

> append "Using the text editor is easy!"
OK
```

### 步骤 4：查看内容

```bash
> show
1: Hello, World!
2: This is my first file.
3: Using the text editor is easy!
```

### 步骤 5：编辑文本

```bash
> insert 1:1 "Title: "
OK

> show
1: Title: Hello, World!
2: This is my first file.
3: Using the text editor is easy!
```

### 步骤 6：保存文件

```bash
> save
Saved: hello.txt
```

### 步骤 7：尝试撤销和重做

```bash
> delete 1:1 7
OK

> show
1: Hello, World!
2: This is my first file.
3: Using the text editor is easy!

> undo
Undo: delete 1:1 7

> show
1: Title: Hello, World!
2: This is my first file.
3: Using the text editor is easy!
```

### 步骤 8：退出程序

```bash
> exit
工作区状态已保存。再见！
```

## 下次启动

当你再次运行程序时：

```bash
python main.py
```

你会看到：
```
欢迎使用文本编辑器！
输入 'help' 查看可用命令

恢复工作区状态: 1 个文件
活动文件: hello.txt

>
```

你的文件和工作状态会自动恢复！

## 常用场景

### 场景1：编写文档

```bash
> init document.txt with-log    # 创建带日志的文件
> append "# My Document"
> append ""
> append "## Chapter 1"
> append "Content goes here..."
> save
```

### 场景2：管理多个文件

```bash
> load file1.txt
> append "Content for file 1"
> load file2.txt               # 切换到新文件
> append "Content for file 2"
> editor-list                  # 查看所有文件
> file1.txt*
  file2.txt*
> save all                     # 保存所有文件
```

### 场景3：代码编辑

```bash
> load script.py
> append "def hello():"
> append "    print('Hello!')"
> insert 2:5 "name"            # 修改函数名
> show
1: def hello():
2:     name('Hello!')
> undo                         # 撤销修改
```

## 进阶功能

### 启用日志记录

```bash
> log-on                       # 启用当前文件的日志
> append "tracked change"
> log-show                     # 查看日志
session start at 20251107 15:30:00
20251107 15:30:05 log-on
20251107 15:30:10 append "tracked change"
```

### 查看目录结构

```bash
> dir-tree
Editor
├── main.py
├── src
│   ├── main.py
│   ├── workspace.py
│   └── ...
└── README.md

> dir-tree src                 # 查看特定目录
```

## 下一步

- 阅读 [用户手册](USER_GUIDE.md) 了解所有命令
- 查看 [设计文档](DESIGN.md) 了解架构
- 探索更多功能！

## 小贴士

1. **文本中包含空格**：使用引号
   ```bash
   > append "text with    spaces"
   ```

2. **多行插入**：使用 `\n`
   ```bash
   > insert 1:1 "Line 1\nLine 2\nLine 3"
   ```

3. **位置计数**：行号和列号都从 **1** 开始
   ```bash
   > insert 1:1 "text"    # 第1行第1列
   ```

4. **快速撤销**：连续 undo
   ```bash
   > undo
   > undo
   > undo
   ```

5. **批量保存**：
   ```bash
   > save all
   ```

现在开始使用吧！🚀

