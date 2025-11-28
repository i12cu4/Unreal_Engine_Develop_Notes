# CodeFormatterByPython

一个用于自动重命名 Python 代码中标识符的智能工具，支持大驼峰命名法(PascalCase)和下划线命名法(snake_case)两种规范。

## 功能特性

- 🔄 **自动重命名**: 自动将代码中的变量、函数、类名转换为指定命名规范
- 🎯 **智能作用域分析**: 准确识别不同作用域中的标识符，避免命名冲突
- 📝 **保留格式**: 使用 tokenize 模块确保代码格式和注释不被破坏
- 🔍 **冲突处理**: 自动处理命名冲突，添加数字后缀
- 📁 **批量处理**: 递归处理指定文件夹中的所有 Python 文件

## 支持的命名规范

### 大驼峰命名法 (PascalCase)
- 类名、函数名、变量名都使用大驼峰格式
- 示例: `my_variable` → `MyVariable`, `user_id` → `UserId`

### 下划线命名法 (snake_case)
- 函数名、变量名使用小写下划线格式
- 示例: `myVariable` → `my_variable`, `UserName` → `user_name`

## 安装要求

- Python 3.6+
- 无需额外依赖

## 使用方法

### 1. 配置设置

在代码开头修改配置区域：

```python
# ========== 配置区域 ==========
# 要处理的文件夹路径
FOLDER_PATH = Path(__file__).resolve().parent.joinpath("Task")

# 命名规范选择 (0: 大驼峰, 1: 下划线)
NAMING_STYLE = 0  # 0 或 1
# =============================
```

### 2. 运行程序

```bash
python code_standardizer.py
```

### 3. 确认处理

程序会显示找到的 Python 文件数量，并等待用户确认：

```
找到 15 个Python文件
命名规范: 大驼峰 (PascalCase)
按回车键开始处理...
```

按回车键开始处理，按 Ctrl+C 取消。

## 处理范围

工具会重命名以下标识符：

### ✅ 会重命名的标识符
- **类名** (`class MyClass:`)
- **函数名** (`def my_function():`)
- **变量名** (`my_variable = 10`)
- **函数参数** (`def func(param1, param2):`)
- **循环变量** (`for i in range(10):`)
- **with语句变量** (`with open() as f:`)
- **全局变量** (`global my_global`)

### ❌ 不会重命名的标识符
- **魔术方法** (`__init__`, `__str__` 等)
- **单个字符变量** (`i`, `j`, `x`, `y` 等，通常是循环变量)
- **字符串内容**
- **注释内容**
- **文档字符串**

## 注意事项

### ⚠️ 重要提醒

1. **备份代码**: 工具会直接修改原文件，建议在处理前备份代码或使用版本控制
2. **语法检查**: 确保代码没有语法错误，否则解析会失败
3. **命名冲突**: 工具会自动处理命名冲突，但建议检查重命名结果
4. **外部依赖**: 如果代码依赖外部库，确保重命名不会影响 API 调用

### 处理示例

**处理前 (混合命名):**
```python
def my_function(userName, user_age):
    tempData = process_data(userName, user_age)
    class DataProcessor:
        def process_data(self):
            return self.data
```

**处理后 (大驼峰):**
```python
def MyFunction(UserName, UserAge):
    TempData = ProcessData(UserName, UserAge)
    class DataProcessor:
        def ProcessData(self):
            return self.Data
```

**处理后 (下划线):**
```python
def my_function(user_name, user_age):
    temp_data = process_data(user_name, user_age)
    class DataProcessor:
        def process_data(self):
            return self.data
```

## 故障排除

### 常见问题

1. **语法错误导致处理失败**
   - 确保所有 Python 文件语法正确
   - 检查是否有不兼容的 Python 语法

2. **编码问题**
   - 确保文件使用 UTF-8 编码
   - 检查是否有特殊字符

3. **重命名不完整**
   - 某些复杂情况可能需要手动检查
   - 确保所有标识符都在支持的重命名范围内

### 恢复方法

如果重命名结果不理想：
1. 使用版本控制回滚 (`git reset --hard`)
2. 从备份恢复文件
3. 手动修复问题标识符

## 技术细节

### 实现原理

1. **AST 解析**: 使用 Python 的 `ast` 模块解析代码结构
2. **作用域分析**: 构建作用域树，准确跟踪标识符的作用域
3. **Token 处理**: 使用 `tokenize` 模块精确替换标识符，保留格式
4. **冲突检测**: 自动检测并解决命名冲突

### 支持的 Python 语法

- 函数定义 (`def`, `async def`)
- 类定义 (`class`)
- 变量赋值 (`=`, `:=`)
- 循环语句 (`for`, `while`)
- 上下文管理器 (`with`)
- 推导式 (列表、字典、集合、生成器)
- 全局和非局部声明 (`global`, `nonlocal`)

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个工具！

## 许可证

MIT License

---

**注意**: 这是一个代码重构工具，请谨慎使用并在处理前确保代码已备份！