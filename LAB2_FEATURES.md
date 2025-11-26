# Lab2 新增功能说明

本文档说明Lab2在Lab1基础上新增的功能。  
> ⚠️ **依赖说明**：为了启用拼写检查功能，请先安装 `pyspellchecker`：
> ```bash
> pip install pyspellchecker
> ```

## 新增功能概览

### 1. XML编辑器 (XMLEditor)

支持XML文件的元素级编辑，使用组合模式表示树形结构。

**新增命令：**
- `init <filepath> xml [with-log]` - 创建XML文件
- `append-root <tag> <newId> ["text"] [attr=val ...]` - 创建/替换根元素
- `insert-before <tag> <newId> <targetId> ["text"] [attr=val ...]` - 在目标元素前插入新元素
- `append-child <tag> <newId> <parentId> ["text"] [attr=val ...]` - 向父元素追加子元素
- `edit-id <oldId> <newId>` - 修改元素ID
- `edit-text <elementId> ["text"]` - 修改元素文本内容
- `delete <elementId>` - 删除元素（XML文件中）
- `set-attr <elementId> <attrName> <attrValue>` - 设置/修改元素属性
- `remove-attr <elementId> <attrName>` - 删除元素属性
- `xml-tree [file]` - 显示XML树形结构

**特性：**
- 完整的undo/redo支持
- 自动id重复检测
- 树形可视化显示
- 支持日志记录和过滤

**示例：**
```bash
> init books.xml xml
> append-root bookstore store1 "" location=Beijing
> append-child book book1 store1 "" category=FICTION year=2005
> append-child title title1 book1 "Harry Potter" lang=en edition=1st
> append-child author author1 book1 "J.K. Rowling" country=UK
> xml-tree
bookstore [id="store1", location="Beijing"]
└── book [id="book1", category="FICTION", year="2005"]
    ├── title [id="title1", lang="en", edition="1st"]
    │   └── "Harry Potter"
    └── author [id="author1", country="UK"]
        └── "J.K. Rowling"
> save
```

**属性管理（扩展功能）：**

1. **创建时添加属性**（推荐方式）：
   - 语法：`append-child <tag> <newId> <parentId> ["text"] [attr1=val1] [attr2=val2] ...`
   - 语法：`insert-before <tag> <newId> <targetId> ["text"] [attr1=val1] [attr2=val2] ...`
   - 示例：`append-child book book1 root "" category=FICTION year=2005`
   - 特点：一次性设置所有属性，简洁高效

2. **后续修改属性**：
   - `set-attr <elementId> <attrName> <attrValue>` - 设置/修改单个属性
   - `remove-attr <elementId> <attrName>` - 删除单个属性
   - 示例：`set-attr book1 featured true`

3. **属性保护**：
   - id属性受保护，不能通过set-attr修改或删除
   - 创建时提供的id属性会被忽略
   - 必须使用`edit-id`命令修改元素ID

4. **完整支持**：
   - ✅ 完整的undo/redo支持
   - ✅ 属性正确保存和加载
   - ✅ xml-tree正确显示所有属性
   - ✅ 向后兼容（不带属性的旧用法仍然有效）

### 2. 编辑时长统计 (Statistics)

自动追踪每个文件在当前会话中的编辑时长。

**特性：**
- 文件激活时自动开始计时
- 切换文件时自动停止计时
- 累计显示编辑时长
- 智能格式化（秒/分钟/小时/天）

**显示：**
```bash
> editor-list
> file1.txt (2小时15分钟)
  file2.xml* (45秒)
```

**时长格式：**
- < 1分钟：显示秒
- 1-59分钟：显示分钟
- 1-23小时：显示小时+分钟
- ≥ 24小时：显示天+小时

### 3. 拼写检查 (Spell Checking)

使用适配器模式集成拼写检查服务。

**命令：**
- `spell-check [file]` - 检查当前或指定文件

**支持文件类型：**
- 文本文件：检查所有行的文本
- XML文件：检查所有元素的文本节点

**输出示例：**

**文本文件：**
```bash
> load essay.txt
> spell-check
拼写检查结果:
第1行，第8列: "recieve" -> 建议: receive
第3行，第12列: "occured" -> 建议: occurred
```

**XML文件：**
```bash
> load books.xml
> spell-check
拼写检查结果:
元素 title1: "Itallian" -> 建议: Italian
元素 author2: "Rowlling" -> 建议: Rowling
```

**实现：**
- 接口抽象：`ISpellChecker`
- 真实适配器：`PySpellCheckerAdapter` (需要安装pyspellchecker)
- Mock适配器：`MockSpellChecker` (用于测试)

### 4. 日志过滤增强

支持通过文件首行配置排除特定命令的日志记录。

**语法：**
```
# log -e cmd1 -e cmd2
```

**示例：**
```bash
> init test.txt text
> append "# log -e append -e delete"
> save
# 之后的append和delete命令不会被记录到日志中
```

**特性：**
- 支持排除多个命令
- 对每个文件独立配置
- 对未知命令显示警告但不中断程序

### 5. 改进的init命令

创建文件时需指定文件类型。

**新语法：**
```bash
init <filepath> <text|xml> [with-log]
```

**示例：**
```bash
> init note.txt text with-log      # 创建带日志的文本文件
> init books.xml xml                # 创建XML文件
```

## 设计模式应用

### 新增设计模式：

1. **组合模式 (Composite)** - XMLElement树形结构
2. **适配器模式 (Adapter)** - SpellChecker接口适配第三方库
3. **装饰器模式 (Decorator)** - 编辑时长装饰显示

### 扩展的设计模式：

1. **命令模式** - 扩展支持XML编辑命令
2. **观察者模式** - 新增StatisticsObserver
3. **备忘录模式** - 保持原有功能

## 测试

运行完整测试：
```bash
python test_lab2.py   # Lab2新功能测试
python test_basic.py  # Lab1功能回归测试
```

所有测试通过✅

## 兼容性

- ✅ 完全向后兼容Lab1
- ✅ 所有Lab1功能正常工作
- ✅ 新功能不影响旧功能
- ✅ 最小化代码改动

## 技术亮点

1. **依赖注入** - SpellChecker通过类方法注入，支持Mock测试
2. **松耦合** - 各模块独立，Statistics和SpellChecker故障不影响核心功能
3. **可扩展** - 接口抽象设计便于添加新的编辑器类型和功能
4. **类型安全** - 使用类型注解提高代码可维护性

---

## 超出Lab2要求的扩展功能 🚀

为了提供更完善的XML编辑体验，我们额外实现了以下功能：

### 1. 根元素管理功能

#### `append-root` - 创建/替换根元素

**功能**：创建或替换XML文档的根元素，解决默认root名称的问题。

**语法**：
```bash
append-root <tag> <newId> ["text"] [attr=val ...]
```

**使用场景：**

**场景1：自定义根元素名称**
```bash
> init catalog.xml xml              # 创建默认 <root id="root">
> append-root catalog cat1 "" type=products region=CN
✓ OK
> xml-tree
catalog [id="cat1", type="products", region="CN"]
```

**场景2：防止破坏已有结构**
```bash
> init books.xml xml
> append-root bookstore store1 ""
> append-child book book1 store1 ""
> append-root library lib1 ""      # 尝试再次创建根元素
❌ Error: XML文档已有根元素（含子元素），不能创建新的根元素
```

**保护机制：**
- ✅ 只能在空的默认root时替换（tag="root", id="root", 无子元素）
- ❌ 如果root有子元素，拒绝创建
- ❌ 如果root已被自定义过，拒绝替换
- ✅ 完整的undo/redo支持

**价值：**
1. 允许用户自定义根元素名称和ID（不强制使用"root"）
2. 安全检查，防止误操作破坏XML结构
3. 解决空XML文件的处理问题
4. 更符合实际XML文档的需求

---

### 2. 属性管理功能

虽然Lab2要求每个元素必须有id属性，但并未要求实现其他属性的管理。我们额外实现了：

#### **后续修改属性**
- `set-attr <elementId> <attrName> <attrValue>` - 设置/修改任意属性
- `remove-attr <elementId> <attrName>` - 删除属性
- 完整的undo/redo支持
- id属性保护机制

**使用场景：**
```bash
> append-child title title1 book1 "Harry Potter"
> set-attr title1 lang en        # 后续添加属性
> set-attr title1 edition 1st    # 添加更多属性
> remove-attr title1 edition     # 删除属性
> undo                           # 撤销删除
```

#### **创建时直接添加属性**
- 支持在`append-child`和`insert-before`时通过键值对添加属性
- 语法：`append-child <tag> <newId> <parentId> ["text"] [attr1=val1] [attr2=val2] ...`
- 完全向后兼容

**使用场景：**
```bash
# 一次性创建带所有属性的元素
> append-child book book1 root "" category=FICTION year=2005 featured=true
> append-child title title1 book1 "Harry Potter" lang=en edition=1st style=bold

# 旧用法仍然有效
> append-child author author1 book1 "J.K. Rowling"
```

**优势：**
- ✅ 减少命令数量（一条命令完成所有设置）
- ✅ 更符合实际使用场景（元素属性通常在创建时确定）
- ✅ 提高效率（批量设置比逐个设置更快）
- ✅ 完全向后兼容（可选功能）

### 2. 实现价值

这些扩展功能使得XML编辑器：
1. **更实用** - 符合真实XML文档的需求（属性是XML的核心特性）
2. **更高效** - 减少重复命令，提升用户体验
3. **更完整** - 提供了完整的XML元素操作能力

### 3. 设计考虑

- **保护机制**：id属性不可通过set-attr修改，保证元素唯一性
- **一致性**：属性操作遵循相同的命令模式，支持undo/redo
- **灵活性**：两种方式（创建时/后续修改）满足不同场景
- **兼容性**：完全向后兼容，不影响基本功能

