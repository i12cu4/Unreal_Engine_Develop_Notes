import os
import re
import ast
import tokenize
from io import StringIO
from pathlib import Path
from collections import defaultdict

# ========== 配置区域 ==========
# 要处理的文件夹路径
FOLDER_PATH = Path(__file__).resolve().parent.joinpath("Task")

# 命名规范选择 (0: 大驼峰, 1: 下划线)
NAMING_STYLE = 0  # 0 或 1

# =============================

class ScopeAnalyzer(ast.NodeVisitor):
    """分析作用域，构建作用域树"""
    
    def __init__(self):
        self.scopes = []
        self.current_scope = None
        self.scope_stack = []
    
    def visit_Module(self, node):
        """模块作用域"""
        self.enter_scope('module', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_FunctionDef(self, node):
        """函数作用域"""
        self.enter_scope('function', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_AsyncFunctionDef(self, node):
        """异步函数作用域"""
        self.enter_scope('function', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_ClassDef(self, node):
        """类作用域"""
        self.enter_scope('class', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_ListComp(self, node):
        """列表推导式作用域"""
        self.enter_scope('comprehension', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_SetComp(self, node):
        """集合推导式作用域"""
        self.enter_scope('comprehension', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_DictComp(self, node):
        """字典推导式作用域"""
        self.enter_scope('comprehension', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def visit_GeneratorExp(self, node):
        """生成器表达式作用域"""
        self.enter_scope('comprehension', node)
        self.generic_visit(node)
        self.exit_scope()
    
    def enter_scope(self, scope_type, node):
        """进入作用域"""
        scope = {
            'type': scope_type,
            'node': node,
            'parent': self.current_scope,
            'names': set(),
            'global_names': set(),
            'nonlocal_names': set()
        }
        
        if self.current_scope:
            self.scope_stack.append(self.current_scope)
        
        self.current_scope = scope
        self.scopes.append(scope)
    
    def exit_scope(self):
        """退出作用域"""
        if self.scope_stack:
            self.current_scope = self.scope_stack.pop()
        else:
            self.current_scope = None
    
    def add_name(self, name):
        """向当前作用域添加名称"""
        if self.current_scope:
            self.current_scope['names'].add(name)
    
    def add_global(self, name):
        """添加全局声明"""
        if self.current_scope:
            self.current_scope['global_names'].add(name)
    
    def add_nonlocal(self, name):
        """添加nonlocal声明"""
        if self.current_scope:
            self.current_scope['nonlocal_names'].add(name)

class CodeRenamer(ast.NodeTransformer):
    def __init__(self, naming_style):
        self.naming_style = naming_style  # 0: 大驼峰, 1: 下划线
        self.renames = {}
        self.scope_analyzer = ScopeAnalyzer()
        self.current_scope = None
        self.scope_stack = []
        
    def _to_pascal_case(self, name):
        """转换为大驼峰命名 (每个单词首字母大写)"""
        if '_' in name:
            # 下划线转大驼峰
            parts = name.split('_')
            return ''.join(part.capitalize() for part in parts if part)
        elif name.isupper():
            # 全大写常量处理
            parts = name.lower().split('_')
            return ''.join(part.capitalize() for part in parts if part)
        else:
            # 尝试从驼峰识别单词
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
            parts = name.split('_')
            return ''.join(part.capitalize() for part in parts if part)
    
    def _to_snake_case(self, name):
        """转换为下划线命名"""
        # 处理全大写常量
        if name.isupper():
            return name.lower()
        
        # 驼峰转下划线
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    def _normalize_name(self, name):
        """根据选择的命名规范规范化名称"""
        if name.startswith('__') and name.endswith('__'):
            return name  # 不处理魔术方法
        
        # 不处理单个字符的变量名（通常是循环变量）
        if len(name) <= 1:
            return name
            
        if self.naming_style == 0:  # 大驼峰
            return self._to_pascal_case(name)
        else:  # 下划线
            return self._to_snake_case(name)
    
    def _get_scope_for_node(self, node):
        """找到节点所属的作用域"""
        for scope in reversed(self.scope_analyzer.scopes):
            if scope['node'] == node:
                return scope
        return None
    
    def _is_name_in_scope(self, name, scope):
        """检查名称是否在指定作用域或其父作用域中"""
        current = scope
        while current:
            if name in current['names']:
                return True
            current = current['parent']
        return False
    
    def _rename_in_scope(self, old_name, new_name, scope):
        """在特定作用域中重命名"""
        # 检查新名称是否在作用域中已存在
        if self._is_name_in_scope(new_name, scope):
            # 处理冲突
            if self.naming_style == 0:  # 大驼峰
                base_name = new_name
                suffix = 1
                while self._is_name_in_scope(f"{base_name}{suffix}", scope):
                    suffix += 1
                new_name = f"{base_name}{suffix}"
            else:  # 下划线
                base_name = new_name
                suffix = 1
                while self._is_name_in_scope(f"{base_name}_{suffix}", scope):
                    suffix += 1
                new_name = f"{base_name}_{suffix}"
        
        # 记录重命名
        scope_key = (id(scope['node']), old_name)
        self.renames[scope_key] = new_name
        
        # 更新作用域中的名称
        scope['names'].discard(old_name)
        scope['names'].add(new_name)
        
        return new_name
    
    def visit_FunctionDef(self, node):
        """重命名函数"""
        scope = self._get_scope_for_node(node)
        if scope:
            new_name = self._normalize_name(node.name)
            node.name = self._rename_in_scope(node.name, new_name, scope)
        return self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """重命名异步函数"""
        scope = self._get_scope_for_node(node)
        if scope:
            new_name = self._normalize_name(node.name)
            node.name = self._rename_in_scope(node.name, new_name, scope)
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """重命名类"""
        scope = self._get_scope_for_node(node)
        if scope:
            new_name = self._normalize_name(node.name)
            node.name = self._rename_in_scope(node.name, new_name, scope)
        return self.generic_visit(node)
    
    def visit_Assign(self, node):
        """处理变量赋值"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # 找到变量定义的作用域
                scope = None
                for s in reversed(self.scope_analyzer.scopes):
                    if id(s['node']) in [id(n) for n in ast.walk(node) if hasattr(n, 'id')]:
                        scope = s
                        break
                
                if scope:
                    new_name = self._normalize_name(target.id)
                    target.id = self._rename_in_scope(target.id, new_name, scope)
        return self.generic_visit(node)
    
    def visit_AnnAssign(self, node):
        """处理带类型注解的变量赋值"""
        if isinstance(node.target, ast.Name):
            # 找到变量定义的作用域
            scope = None
            for s in reversed(self.scope_analyzer.scopes):
                if id(s['node']) in [id(n) for n in ast.walk(node) if hasattr(n, 'id')]:
                    scope = s
                    break
            
            if scope:
                new_name = self._normalize_name(node.target.id)
                node.target.id = self._rename_in_scope(node.target.id, new_name, scope)
        return self.generic_visit(node)
    
    def visit_For(self, node):
        """处理for循环中的变量"""
        if isinstance(node.target, ast.Name):
            # 找到循环变量定义的作用域
            scope = None
            for s in reversed(self.scope_analyzer.scopes):
                if id(s['node']) in [id(n) for n in ast.walk(node) if hasattr(n, 'id')]:
                    scope = s
                    break
            
            if scope:
                new_name = self._normalize_name(node.target.id)
                node.target.id = self._rename_in_scope(node.target.id, new_name, scope)
        return self.generic_visit(node)
    
    def visit_With(self, node):
        """处理with语句中的变量"""
        for item in node.items:
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                # 找到变量定义的作用域
                scope = None
                for s in reversed(self.scope_analyzer.scopes):
                    if id(s['node']) in [id(n) for n in ast.walk(node) if hasattr(n, 'id')]:
                        scope = s
                        break
                
                if scope:
                    new_name = self._normalize_name(item.optional_vars.id)
                    item.optional_vars.id = self._rename_in_scope(item.optional_vars.id, new_name, scope)
        return self.generic_visit(node)
    
    def visit_Arg(self, node):
        """处理函数参数"""
        # 找到函数作用域
        scope = None
        for s in self.scope_analyzer.scopes:
            if s['type'] == 'function' and hasattr(s['node'], 'args'):
                # 检查这个参数是否属于该函数
                if node in s['node'].args.args or node in getattr(s['node'].args, 'posonlyargs', []) or node in getattr(s['node'].args, 'kwonlyargs', []):
                    scope = s
                    break
        
        if scope:
            new_name = self._normalize_name(node.arg)
            node.arg = self._rename_in_scope(node.arg, new_name, scope)
        return self.generic_visit(node)
    
    def visit_Global(self, node):
        """处理global语句"""
        for name in node.names:
            # 找到模块作用域
            module_scope = None
            for s in self.scope_analyzer.scopes:
                if s['type'] == 'module':
                    module_scope = s
                    break
            
            if module_scope:
                # 在模块作用域中重命名全局变量
                new_name = self._normalize_name(name)
                scope_key = (id(module_scope['node']), name)
                if scope_key not in self.renames:
                    self.renames[scope_key] = new_name
                    module_scope['names'].discard(name)
                    module_scope['names'].add(new_name)
        return self.generic_visit(node)
    
    def visit_Nonlocal(self, node):
        """处理nonlocal语句"""
        # nonlocal语句引用的名称不应该被重命名，因为它们引用外部作用域的变量
        # 我们只需要确保外部作用域中的相应变量被正确重命名
        return self.generic_visit(node)

def rename_in_file_content(content, renames):
    """在文件内容中重命名所有出现的标识符，保留原始格式"""
    # 首先，我们需要构建一个从旧名称到新名称的映射
    name_mapping = {}
    for (scope_id, old_name), new_name in renames.items():
        name_mapping[old_name] = new_name
    
    # 使用tokenize来精确替换标识符，避免替换字符串和注释
    tokens = []
    try:
        for token in tokenize.generate_tokens(StringIO(content).readline):
            if token.type == tokenize.NAME and token.string in name_mapping:
                tokens.append((tokenize.NAME, name_mapping[token.string], token.start, token.end, token.line))
            else:
                tokens.append(token)
        
        # 重新构建代码
        result = tokenize.untokenize(tokens)
        return result
    except:
        # 如果tokenize失败，回退到正则表达式方法
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            for old_name, new_name in name_mapping.items():
                # 使用单词边界确保只替换完整的标识符
                pattern = r'\b' + re.escape(old_name) + r'\b'
                line = re.sub(pattern, new_name, line)
            new_lines.append(line)
        
        return '\n'.join(new_lines)

def process_python_file(file_path, naming_style):
    """处理单个Python文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"警告: 文件 {file_path} 有语法错误，跳过")
            return
        
        # 分析作用域
        scope_analyzer = ScopeAnalyzer()
        scope_analyzer.visit(tree)
        
        # 收集所有标识符到各自的作用域
        class IdentifierCollector(ast.NodeVisitor):
            def __init__(self, scope_analyzer):
                self.scope_analyzer = scope_analyzer
                self.current_scope = None
                self.scope_stack = []
            
            def visit_Module(self, node):
                self.enter_scope(self._get_scope_for_node(node))
                self.generic_visit(node)
                self.exit_scope()
            
            def visit_FunctionDef(self, node):
                scope = self._get_scope_for_node(node)
                self.enter_scope(scope)
                scope['names'].add(node.name)
                self.generic_visit(node)
                self.exit_scope()
            
            def visit_AsyncFunctionDef(self, node):
                scope = self._get_scope_for_node(node)
                self.enter_scope(scope)
                scope['names'].add(node.name)
                self.generic_visit(node)
                self.exit_scope()
            
            def visit_ClassDef(self, node):
                scope = self._get_scope_for_node(node)
                self.enter_scope(scope)
                scope['names'].add(node.name)
                self.generic_visit(node)
                self.exit_scope()
            
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if self.current_scope:
                            self.current_scope['names'].add(target.id)
                self.generic_visit(node)
            
            def visit_AnnAssign(self, node):
                if isinstance(node.target, ast.Name):
                    if self.current_scope:
                        self.current_scope['names'].add(node.target.id)
                self.generic_visit(node)
            
            def visit_For(self, node):
                if isinstance(node.target, ast.Name):
                    if self.current_scope:
                        self.current_scope['names'].add(node.target.id)
                self.generic_visit(node)
            
            def visit_With(self, node):
                for item in node.items:
                    if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                        if self.current_scope:
                            self.current_scope['names'].add(item.optional_vars.id)
                self.generic_visit(node)
            
            def visit_Arg(self, node):
                if self.current_scope:
                    self.current_scope['names'].add(node.arg)
                self.generic_visit(node)
            
            def visit_Global(self, node):
                for name in node.names:
                    if self.current_scope:
                        self.current_scope['global_names'].add(name)
                self.generic_visit(node)
            
            def visit_Nonlocal(self, node):
                for name in node.names:
                    if self.current_scope:
                        self.current_scope['nonlocal_names'].add(name)
                self.generic_visit(node)
            
            def _get_scope_for_node(self, node):
                for scope in self.scope_analyzer.scopes:
                    if scope['node'] == node:
                        return scope
                return None
            
            def enter_scope(self, scope):
                if scope:
                    if self.current_scope:
                        self.scope_stack.append(self.current_scope)
                    self.current_scope = scope
            
            def exit_scope(self):
                if self.scope_stack:
                    self.current_scope = self.scope_stack.pop()
                else:
                    self.current_scope = None
        
        collector = IdentifierCollector(scope_analyzer)
        collector.visit(tree)
        
        # 创建重命名器
        renamer = CodeRenamer(naming_style)
        renamer.scope_analyzer = scope_analyzer
        new_tree = renamer.visit(tree)
        
        # 如果有重命名，更新文件内容
        if renamer.renames:
            new_content = rename_in_file_content(content, renamer.renames)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"已处理: {file_path}, 重命名了 {len(renamer.renames)} 个标识符")
            for (scope_id, old), new in renamer.renames.items():
                print(f"  {old} -> {new}")
        else:
            print(f"无需处理: {file_path}")
            
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def find_python_files(directory):
    """递归查找目录下的所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    folder_path = FOLDER_PATH
    naming_style = NAMING_STYLE
    
    if not os.path.exists(folder_path):
        print("文件夹不存在!")
        return
    
    # 查找所有Python文件
    python_files = find_python_files(folder_path)
    
    if not python_files:
        print("在指定文件夹中未找到Python文件!")
        return
    
    print(f"找到 {len(python_files)} 个Python文件")
    print(f"命名规范: {'大驼峰 (PascalCase)' if naming_style == 0 else '下划线 (snake_case)'}")
    print("按回车键开始处理...")
    input()  # 等待用户按回车
    
    # 处理每个文件
    for file_path in python_files:
        process_python_file(file_path, naming_style)
    
    print("\n处理完成!")

if __name__ == "__main__":
    main()