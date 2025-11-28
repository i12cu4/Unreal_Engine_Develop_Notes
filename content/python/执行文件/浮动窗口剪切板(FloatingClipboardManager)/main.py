import tkinter as tk
from tkinter import ttk
import pyperclip
import os
import json

class FloatingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("输出窗口")
        
        # 设置窗口始终置顶
        self.root.attributes('-topmost', True)
        
        # 设置窗口初始大小和位置
        self.root.geometry("400x300+100+100")
        
        # 允许窗口调整大小
        self.root.resizable(True, True)
        
        # 设置窗口的最小大小
        self.root.minsize(350, 250)
        
        # 存储所有创建的按钮对
        self.button_pairs = []
        
        # 定义保存文件路径 - 使用绝对路径确保正确
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_file = os.path.join(current_dir, "saved_strings.json")
        
        # 创建界面
        self.create_widgets()
        
        # 加载之前保存的字符串
        self.load_saved_strings()
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # 创建一个主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # 添加输入框和载入按钮的框架
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 添加输入框
        self.entry = ttk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 添加载入按钮
        load_button = ttk.Button(input_frame, text="载入", command=self.load_text)
        load_button.pack(side=tk.RIGHT)
        
        # 添加按钮容器 - 使用Canvas和Frame实现滚动
        self.canvas = tk.Canvas(main_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮到Canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # 绑定回车键到载入功能
        self.entry.bind('<Return>', lambda event: self.load_text())
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_text(self):
        # 获取输入框内容
        text = self.entry.get().strip()
        
        # 检查输入是否为空
        if not text:
            self.update_status("错误：输入不能为空")
            return
        
        # 检查是否已存在相同文本的按钮
        for pair in self.button_pairs:
            if pair["text"] == text:
                self.update_status("错误：已存在相同文本的按钮")
                return
        
        # 创建新按钮对
        self.create_button_pair(text)
        
        # 清空输入框
        self.entry.delete(0, tk.END)
        
        # 更新状态
        self.update_status(f"已载入: {text}")
        
        # 立即保存到文件
        self.save_strings()
    
    def create_button_pair(self, text):
        # 为每个按钮对创建一个容器框架
        pair_frame = ttk.Frame(self.scrollable_frame)
        pair_frame.pack(fill=tk.X, pady=2)
        
        # 创建复制按钮
        copy_button = ttk.Button(
            pair_frame, 
            text=text if len(text) <= 25 else text[:22] + "...",  # 限制按钮文本长度
            command=lambda t=text: self.copy_to_clipboard(t)
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 为复制按钮添加悬停提示
        self.create_tooltip(copy_button, text)
        
        # 创建删除按钮
        delete_button = ttk.Button(
            pair_frame, 
            text="删除", 
            command=lambda pf=pair_frame, t=text: self.delete_button_pair(pf, t)
        )
        delete_button.pack(side=tk.LEFT)
        
        # 保存按钮对信息
        self.button_pairs.append({
            "frame": pair_frame,
            "text": text,
            "copy_button": copy_button,
            "delete_button": delete_button
        })
    
    def create_tooltip(self, widget, text):
        """为控件创建悬停提示"""
        tooltip = None
        
        def on_enter(event):
            nonlocal tooltip
            # 创建提示窗口
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            
            # 创建顶层窗口
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           font=("Arial", 10), wraplength=300)
            label.pack(ipadx=1)
        
        def on_leave(event):
            if tooltip:
                tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def copy_to_clipboard(self, text):
        # 将文本复制到剪切板
        pyperclip.copy(text)
        
        # 更新状态
        self.update_status(f"已复制: {text}")
    
    def delete_button_pair(self, pair_frame, text):
        # 从容器中移除框架
        pair_frame.destroy()
        
        # 从列表中移除
        self.button_pairs = [pair for pair in self.button_pairs if pair["text"] != text]
        
        # 更新状态
        self.update_status(f"已删除: {text}")
        
        # 立即保存到文件
        self.save_strings()
    
    def update_status(self, message):
        # 更新状态标签
        self.status_label.config(text=message)
    
    def load_saved_strings(self):
        """从文件加载保存的字符串"""
        try:
            print(f"尝试从 {self.save_file} 加载数据")
            
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    saved_strings = json.load(f)
                
                print(f"从文件加载了 {len(saved_strings)} 个字符串: {saved_strings}")
                
                for text in saved_strings:
                    self.create_button_pair(text)
                
                self.update_status(f"已加载 {len(saved_strings)} 个保存的字符串")
            else:
                print("保存文件不存在，将创建新文件")
                self.update_status("没有找到保存的字符串")
        except Exception as e:
            print(f"加载保存的字符串时出错: {str(e)}")
            self.update_status(f"加载保存的字符串时出错: {str(e)}")
    
    def save_strings(self):
        """保存所有字符串到文件"""
        try:
            # 提取所有文本
            all_texts = [pair["text"] for pair in self.button_pairs]
            
            print(f"保存 {len(all_texts)} 个字符串到 {self.save_file}: {all_texts}")
            
            # 保存到文件
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(all_texts, f, ensure_ascii=False, indent=2)
                
            print("保存成功")
        except Exception as e:
            print(f"保存字符串时出错: {str(e)}")
            self.update_status(f"保存字符串时出错: {str(e)}")
    
    def on_closing(self):
        """窗口关闭时保存数据"""
        print("程序关闭，保存数据")
        self.save_strings()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingWindow()
    app.run()