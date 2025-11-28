import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import subprocess
import sys
import re
import ast
import tempfile
import io
import contextlib
from datetime import datetime

class PythonFileBrowser:
    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)
        self.python_files = []
        self.current_file = None
        self.param_widgets = {}
        self.run_count = {}  # 记录每个文件的运行次数
        self.folder_states = {}  # 记录文件夹的展开/折叠状态
        self.folder_containers = {}  # 存储文件夹容器的引用
        self.folder_frames = {}  # 存储文件夹标题框架的引用
        self.saved_output = ""  # 保存运行输出内容
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Python文件浏览器")
        self.root.geometry("1400x800")  # 增加窗口宽度以容纳代码编辑区域
        
        # 创建分栏
        self.create_panels()
        
        # 遍历文件夹并创建文件结构
        self.find_python_files()
        self.create_file_buttons()
        
    def create_panels(self):
        """创建分栏面板"""
        # 左侧面板 - 文件列表
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 左侧标题
        left_label = ttk.Label(left_frame, text="Python文件列表", font=("Arial", 10, "bold"))
        left_label.pack(pady=(0, 10))
        
        # 创建滚动框架用于文件按钮
        self.create_scrollable_frame(left_frame)
        
        # 中间面板 - 参数和输出
        self.center_frame = ttk.Frame(self.root)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 中间初始提示
        self.initial_label = ttk.Label(self.center_frame, text="请从左侧选择一个Python文件", 
                                      font=("Arial", 12), foreground="gray")
        self.initial_label.pack(expand=True)
        
        # 右侧面板 - 代码编辑
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧初始提示
        self.right_initial_label = ttk.Label(self.right_frame, text="代码编辑区域", 
                                           font=("Arial", 12), foreground="gray")
        self.right_initial_label.pack(expand=True)
        
    def create_scrollable_frame(self, parent):
        """创建可滚动的框架"""
        # 创建画布和滚动条
        self.canvas = tk.Canvas(parent, width=300)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 绑定滚动事件
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # 创建窗口
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def find_python_files(self):
        """遍历文件夹，找到所有的Python文件"""
        if not self.root_folder.exists():
            messagebox.showerror("错误", f"文件夹不存在: {self.root_folder}")
            return
            
        print(f"正在扫描文件夹: {self.root_folder}")
        
        try:
            # 遍历所有子文件夹和文件
            for file_path in self.root_folder.rglob("*.py"):
                # 获取相对路径（相对于根文件夹）
                relative_path = file_path.relative_to(self.root_folder)
                # 获取文件名（不带路径）
                filename = file_path.name
                
                self.python_files.append({
                    'filepath': str(file_path),
                    'filename': filename,
                    'relative_path': str(relative_path),
                    'dirname': str(file_path.parent)
                })
                
            print(f"找到 {len(self.python_files)} 个Python文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描文件夹时出错: {str(e)}")
    
    def create_file_buttons(self):
        """创建文件按钮组，按文件夹层级组织"""
        # 按文件夹组织文件
        folder_structure = {}
        
        for file_info in self.python_files:
            folder_path = file_info['dirname']
            if folder_path not in folder_structure:
                folder_structure[folder_path] = []
            folder_structure[folder_path].append(file_info)
        
        # 创建标题
        title_label = ttk.Label(self.scrollable_frame, 
                               text=f"找到 {len(self.python_files)} 个Python文件:", 
                               font=("Arial", 10, "bold"))
        title_label.pack(pady=(0, 10), anchor=tk.W)
        
        # 为每个文件夹创建可折叠的按钮组
        for folder_path, files in sorted(folder_structure.items()):
            # 初始化文件夹状态
            if folder_path not in self.folder_states:
                self.folder_states[folder_path] = True  # 默认展开
                
            # 创建文件夹主框架
            folder_main_frame = ttk.Frame(self.scrollable_frame)
            folder_main_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 创建文件夹标题和切换按钮
            folder_frame = ttk.Frame(folder_main_frame)
            folder_frame.pack(fill=tk.X)
            
            # 文件夹名称（显示相对路径）
            folder_name = os.path.relpath(folder_path, self.root_folder)
            if folder_name == '.':
                folder_name = "根目录"
                
            # 创建展开/折叠按钮
            toggle_btn = ttk.Button(
                folder_frame,
                text="-" if self.folder_states[folder_path] else "+",
                width=3,
                command=lambda fp=folder_path: self.toggle_folder(fp)
            )
            toggle_btn.pack(side=tk.LEFT)
            
            # 文件夹标签
            folder_label = ttk.Label(
                folder_frame,
                text=folder_name,
                font=("Arial", 9, "bold")
            )
            folder_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # 文件数量标签
            count_label = ttk.Label(
                folder_frame,
                text=f"({len(files)})",
                foreground="gray",
                font=("Arial", 8)
            )
            count_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # 保存文件夹框架引用
            self.folder_frames[folder_path] = folder_main_frame
            
            # 创建文件按钮容器
            self.folder_containers[folder_path] = ttk.Frame(folder_main_frame)
            
            # 如果文件夹是展开状态，显示文件按钮
            if self.folder_states[folder_path]:
                self.folder_containers[folder_path].pack(fill=tk.X, padx=15, pady=2)
                self.create_files_in_folder(self.folder_containers[folder_path], files)
    
    def toggle_folder(self, folder_path):
        """切换文件夹的展开/折叠状态"""
        # 切换状态
        self.folder_states[folder_path] = not self.folder_states[folder_path]
        
        # 更新UI
        if self.folder_states[folder_path]:
            # 展开文件夹
            self.folder_containers[folder_path].pack(fill=tk.X, padx=15, pady=2)
            
            # 重新创建文件按钮
            for widget in self.folder_containers[folder_path].winfo_children():
                widget.destroy()
                
            # 获取该文件夹下的文件
            files = [f for f in self.python_files if f['dirname'] == folder_path]
            self.create_files_in_folder(self.folder_containers[folder_path], files)
        else:
            # 折叠文件夹
            self.folder_containers[folder_path].pack_forget()
        
        # 更新文件夹按钮的文本
        self.update_folder_toggle_button(folder_path)
    
    def update_folder_toggle_button(self, folder_path):
        """更新指定文件夹切换按钮的文本"""
        # 找到对应的文件夹框架
        folder_main_frame = self.folder_frames[folder_path]
        
        # 在文件夹框架中找到切换按钮
        for child in folder_main_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Button) and grandchild.winfo_width() == 3:
                        # 更新按钮文本
                        grandchild.config(text="-" if self.folder_states[folder_path] else "+")
                        break
                break
    
    def create_files_in_folder(self, parent_frame, files):
        """在文件夹中创建文件按钮"""
        for file_info in sorted(files, key=lambda x: x['filename']):
            button_frame = ttk.Frame(parent_frame)
            button_frame.pack(fill=tk.X, padx=5, pady=1)
            
            # 创建文件按钮
            button = ttk.Button(
                button_frame,
                text=file_info['filename'],
                command=lambda f=file_info: self.on_file_click(f),
                width=25
            )
            button.pack(side=tk.LEFT, padx=(0, 10))
            
            # 显示文件相对路径（相对于根文件夹）
            rel_path = file_info['relative_path']
            if os.path.dirname(rel_path) != '.':
                path_label = ttk.Label(
                    button_frame,
                    text=os.path.dirname(rel_path),
                    foreground="gray",
                    font=("Arial", 7)
                )
                path_label.pack(side=tk.LEFT)
        
    def on_file_click(self, file_info):
        """处理文件按钮点击事件"""
        self.current_file = file_info
        print(f"选择了文件: {file_info['filepath']}")
        
        # 初始化运行计数
        if file_info['filepath'] not in self.run_count:
            self.run_count[file_info['filepath']] = 0
        
        # 保存当前的运行输出内容
        self.save_output_content()
        
        # 完全清除中间和右侧面板
        self.clear_center_panel()
        self.clear_right_panel()
        
        # 解析Python文件
        self.parse_python_file(file_info)
        
        # 恢复运行输出内容
        self.restore_output_content()
        
    def save_output_content(self):
        """保存运行输出内容"""
        # 检查输出文本框是否存在
        if hasattr(self, 'output_text') and self.output_text:
            try:
                self.output_text.config(state=tk.NORMAL)
                self.saved_output = self.output_text.get(1.0, tk.END)
                self.output_text.config(state=tk.DISABLED)
            except:
                self.saved_output = ""
        else:
            self.saved_output = ""
    
    def restore_output_content(self):
        """恢复运行输出内容"""
        if hasattr(self, 'output_text') and self.output_text and self.saved_output:
            try:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, self.saved_output)
                self.output_text.see(tk.END)
                self.output_text.config(state=tk.DISABLED)
            except:
                pass
        
    def clear_center_panel(self):
        """完全清除中间面板内容"""
        for widget in self.center_frame.winfo_children():
            widget.destroy()
    
    def clear_right_panel(self):
        """完全清除右侧面板内容"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
    def parse_python_file(self, file_info):
        """解析Python文件，提取全局变量（函数定义之外的变量）"""
        try:
            with open(file_info['filepath'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST解析Python代码
            tree = ast.parse(content)
            
            # 提取全局变量（函数定义之外的变量）
            variables = {}
            
            # 获取所有函数定义的名称
            function_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_names.add(node.name)
            
            # 只提取函数定义之外的变量
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # 确保这个变量不是在函数内部定义的
                            try:
                                # 尝试获取变量的值
                                value = ast.literal_eval(node.value)
                                var_type = type(value).__name__
                                variables[target.id] = {
                                    'value': value,
                                    'type': var_type
                                }
                            except (ValueError, SyntaxError):
                                # 如果无法解析值，使用默认值
                                variables[target.id] = {
                                    'value': '',
                                    'type': 'str'
                                }
            
            # 显示文件信息面板
            self.create_parameter_panel(file_info, variables)
            
            # 创建代码编辑面板
            self.create_code_panel(file_info, content)
            
        except Exception as e:
            messagebox.showerror("错误", f"解析Python文件时出错: {str(e)}")
            # 显示错误信息
            error_label = ttk.Label(self.center_frame, text=f"解析文件出错: {str(e)}", 
                                   foreground="red")
            error_label.pack(pady=10)
    
    def create_parameter_panel(self, file_info, variables):
        """创建参数输入面板"""
        # 文件信息
        info_frame = ttk.Frame(self.center_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"文件: {file_info['filename']}", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W)
        # 显示完整路径
        ttk.Label(info_frame, text=f"完整路径: {file_info['filepath']}",
                 foreground="gray").pack(anchor=tk.W)
        
        # 分隔线
        ttk.Separator(self.center_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # 参数输入区域
        param_frame = ttk.LabelFrame(self.center_frame, text="运行参数")
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.param_widgets = {}
        
        # 显示检测到的变量
        if variables:
            for i, (var_name, var_info) in enumerate(variables.items()):
                row_frame = ttk.Frame(param_frame)
                row_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(row_frame, text=f"{var_name} ({var_info['type']}):", 
                         width=15).pack(side=tk.LEFT)
                
                # 根据变量类型选择不同的输入控件
                if var_info['type'] == 'bool':
                    # 布尔类型使用复选框
                    bool_var = tk.BooleanVar(value=var_info['value'])
                    checkbutton = ttk.Checkbutton(row_frame, variable=bool_var)
                    checkbutton.pack(side=tk.LEFT)
                    self.param_widgets[var_name] = bool_var
                else:
                    # 其他类型使用输入框
                    entry = ttk.Entry(row_frame)
                    entry.insert(0, str(var_info['value']))
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.param_widgets[var_name] = entry
        else:
            ttk.Label(param_frame, text="未检测到全局变量", 
                     foreground="gray").pack(pady=10)
        
        # 运行按钮
        run_frame = ttk.Frame(self.center_frame)
        run_frame.pack(fill=tk.X, padx=10, pady=10)
        
        run_button = ttk.Button(run_frame, text="运行程序", 
                               command=self.run_python_file)
        run_button.pack()
        
        # 创建输出面板（总是在参数面板下方）
        self.create_output_panel()
    
    def create_output_panel(self):
        """创建输出面板"""
        # 输出区域
        output_frame = ttk.LabelFrame(self.center_frame, text="运行输出")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加清空输出按钮
        clear_button_frame = ttk.Frame(output_frame)
        clear_button_frame.pack(fill=tk.X, padx=5, pady=2)
        
        clear_button = ttk.Button(clear_button_frame, text="清空输出", 
                                 command=self.clear_output)
        clear_button.pack(side=tk.RIGHT)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, 
                                                   wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)
        
        # 添加输出到文件的功能
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(output_file_frame, text="输出路径:").pack(side=tk.LEFT)
        
        self.output_path_var = tk.StringVar()
        output_path_entry = ttk.Entry(output_file_frame, textvariable=self.output_path_var)
        output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 添加输出状态标签
        self.output_status_label = ttk.Label(output_file_frame, text="", foreground="green")
        self.output_status_label.pack(side=tk.LEFT, padx=5)
        
        output_button = ttk.Button(output_file_frame, text="输出", 
                                  command=self.save_output_to_file)
        output_button.pack(side=tk.RIGHT)
    
    def create_code_panel(self, file_info, content):
        """创建代码编辑面板"""
        # 代码编辑区域
        code_frame = ttk.LabelFrame(self.right_frame, text="代码编辑")
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 代码编辑文本框
        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.code_text.insert(1.0, content)
        
        # 保存按钮和状态标签
        save_button_frame = ttk.Frame(code_frame)
        save_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加保存状态标签
        self.save_status_label = ttk.Label(save_button_frame, text="", foreground="green")
        self.save_status_label.pack(side=tk.LEFT, padx=5)
        
        save_button = ttk.Button(save_button_frame, text="保存", 
                                command=self.save_code_to_file)
        save_button.pack(side=tk.RIGHT)
    
    def save_code_to_file(self):
        """将编辑后的代码保存到文件"""
        if not self.current_file:
            return
        
        try:
            # 获取编辑后的代码内容
            edited_content = self.code_text.get(1.0, tk.END)
            
            # 写入原文件
            with open(self.current_file['filepath'], 'w', encoding='utf-8') as f:
                f.write(edited_content)
            
            # 显示保存成功消息
            self.show_save_status("保存成功")
            
        except Exception as e:
            # 显示保存失败消息
            self.show_save_status(f"保存失败: {str(e)}", is_error=True)
    
    def clear_output(self):
        """清空输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def save_output_to_file(self):
        """将输出内容保存到文件"""
        output_path = self.output_path_var.get().strip()
        
        # 如果输出路径为空，使用当前文件夹
        if not output_path:
            output_path = os.getcwd()
        
        # 处理路径中的斜杠问题
        output_path = output_path.replace('/', os.sep).replace('\\', os.sep)
        
        try:
            # 获取输出内容
            self.output_text.config(state=tk.NORMAL)
            output_content = self.output_text.get(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            
            # 如果路径是文件夹，生成一个不重名的文件名
            if os.path.isdir(output_path):
                # 确保路径以分隔符结尾
                if not output_path.endswith(os.sep):
                    output_path += os.sep
                
                # 生成基于时间戳的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output_{timestamp}.txt"
                full_path = os.path.join(output_path, filename)
            else:
                # 路径是文件，直接使用
                full_path = output_path
                # 如果文件已存在，删除它
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            # 显示输出成功消息
            self.show_output_status("输出成功")
            
        except Exception as e:
            # 显示输出失败消息
            self.show_output_status(f"输出失败: {str(e)}", is_error=True)
    
    def show_save_status(self, message, is_error=False):
        """显示保存状态消息"""
        color = "red" if is_error else "green"
        self.save_status_label.config(text=message, foreground=color)
        
        # 3秒后清除消息
        self.root.after(3000, lambda: self.save_status_label.config(text=""))
    
    def show_output_status(self, message, is_error=False):
        """显示输出状态消息"""
        color = "red" if is_error else "green"
        self.output_status_label.config(text=message, foreground=color)
        
        # 3秒后清除消息
        self.root.after(3000, lambda: self.output_status_label.config(text=""))
    
    def run_python_file(self):
        """运行Python文件"""
        if not self.current_file:
            messagebox.showwarning("警告", "请先选择一个Python文件")
            return
        
        try:
            # 获取参数值
            params = {}
            for var_name, widget in self.param_widgets.items():
                if isinstance(widget, tk.BooleanVar):
                    # 布尔类型变量
                    params[var_name] = widget.get()
                else:
                    # 其他类型变量
                    params[var_name] = widget.get()
            
            # 更新运行计数
            self.run_count[self.current_file['filepath']] += 1
            run_number = self.run_count[self.current_file['filepath']]
            
            # 在输出区域添加分隔符和新运行标记
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.output_text.insert(tk.END, f"第 {run_number} 次运行程序: {self.current_file['filename']}\n")
            self.output_text.insert(tk.END, f"参数: {params}\n")
            self.output_text.insert(tk.END, "="*50 + "\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
            self.root.update()
            
            # 读取Python文件内容
            with open(self.current_file['filepath'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割代码：找到 if __name__ == "__main__": 的位置
            lines = content.split('\n')
            main_block_start = -1
            
            for i, line in enumerate(lines):
                if 'if __name__ == "__main__":' in line:
                    main_block_start = i
                    break
            
            # 执行代码
            output_capture = io.StringIO()
            
            with contextlib.redirect_stdout(output_capture), contextlib.redirect_stderr(output_capture):
                try:
                    # 第一部分：执行 if __name__ == "__main__": 之前的代码
                    if main_block_start >= 0:
                        part1_code = '\n'.join(lines[:main_block_start])
                    else:
                        part1_code = content
                    
                    # 执行第一部分代码
                    exec(part1_code, globals())
                    
                    # 第二部分：应用用户设置的参数
                    for var_name, value in params.items():
                        # 尝试根据原始类型转换值
                        try:
                            # 检查原始值的类型
                            if var_name in globals():
                                original_value = globals()[var_name]
                                if isinstance(original_value, int):
                                    exec(f"{var_name} = {int(value)}", globals())
                                elif isinstance(original_value, float):
                                    exec(f"{var_name} = {float(value)}", globals())
                                elif isinstance(original_value, bool):
                                    exec(f"{var_name} = {value}", globals())
                                else:
                                    exec(f'{var_name} = "{value}"', globals())
                            else:
                                # 如果变量不存在，创建为字符串
                                exec(f'{var_name} = "{value}"', globals())
                        except:
                            # 如果转换失败，使用字符串
                            exec(f'{var_name} = "{value}"', globals())
                    
                    # 第三部分：执行 if __name__ == "__main__": 之后的代码
                    if main_block_start >= 0:
                        part3_code = '\n'.join(lines[main_block_start:])
                        exec(part3_code, globals())
                    
                except Exception as e:
                    print(f"执行错误: {str(e)}")
            
            # 获取输出
            output = output_capture.getvalue()
            
            # 显示输出
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"\n--- 输出 ---\n")
            self.output_text.insert(tk.END, output)
            self.output_text.insert(tk.END, f"\n--- 第 {run_number} 次运行完成 ---\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
                
        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"运行出错: {str(e)}\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    # 固定文件夹路径
    current_dir_pathlib = Path(__file__).resolve().parent.joinpath("Task")
    
    app = PythonFileBrowser(current_dir_pathlib)
    app.run()

if __name__ == "__main__":
    main()