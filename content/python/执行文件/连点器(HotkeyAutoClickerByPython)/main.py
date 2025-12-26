import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import ctypes

# 隐藏终端窗口（仅Windows）
if sys.platform == "win32":
    import win32gui
    import win32console
    # 隐藏控制台窗口
    win32gui.ShowWindow(win32console.GetConsoleWindow(), 0)

try:
    import keyboard
except ImportError:
    # 静默安装，不显示输出
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "keyboard"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import keyboard

try:
    from pynput import mouse
    from pynput.mouse import Button, Controller
except ImportError:
    # 静默安装，不显示输出
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "pynput"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from pynput import mouse
    from pynput.mouse import Button, Controller

# 检查管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class HotkeyRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("热键连点器")
        self.root.geometry("190x35")
        self.root.resizable(False, False)
        
        # 设置窗口始终置顶
        self.root.attributes('-topmost', True)
        
        # 热键相关变量
        self.hotkey = "f1"
        self.recording = False
        
        # 鼠标连点相关变量
        self.click_interval = 1.0
        self.click_thread = None
        self.stop_clicking = True
        self.clicking_active = False
        
        # 窗口隐藏状态
        self.window_hidden = False
        
        # 检查管理员权限
        self.check_admin_permission()
        
        self.setup_ui()
        self.make_draggable()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # 自动注册默认热键
        self.register_hotkey()
        
    def check_admin_permission(self):
        """检查管理员权限"""
        if not is_admin():
            # 静默提示，不弹窗（以免干扰）
            pass
        
    def make_draggable(self):
        """使窗口可拖动"""
        def start_drag(event):
            self.root.x = event.x_root
            self.root.y = event.y_root
            
        def do_drag(event):
            deltax = event.x_root - self.root.x
            deltay = event.y_root - self.root.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
            self.root.x = event.x_root
            self.root.y = event.y_root
            
        self.root.bind("<ButtonPress-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
        
    def setup_ui(self):
        """设置用户界面"""
        small_font = ("Arial", 8)
        
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)
        
        # 热键按钮
        self.hotkey_button = ttk.Button(
            top_frame, 
            text="热键:F1 未激活", 
            command=self.start_recording,
            width=12
        )
        self.hotkey_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 间隔时间设置
        interval_frame = ttk.Frame(top_frame)
        interval_frame.pack(side=tk.LEFT)
        
        ttk.Label(interval_frame, text="间隔:", font=small_font).pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="1.0")
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=4, font=small_font)
        self.interval_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(interval_frame, text="秒", font=small_font).pack(side=tk.LEFT)
            
    def start_recording(self):
        """开始录制热键"""
        if self.recording:
            return
            
        self.recording = True
        self.hotkey_button.config(text="按下热键...")
        
        threading.Thread(target=self.record_hotkey, daemon=True).start()
        
    def record_hotkey(self):
        """录制热键的线程函数"""
        try:
            keyboard.unhook_all()
            
            event = keyboard.read_event(suppress=False)
            
            if event.event_type == keyboard.KEY_DOWN:
                key_name = event.name
                self.hotkey = key_name
                
                self.root.after(0, self.update_hotkey_display)
                self.register_hotkey()
                
        except Exception:
            pass  # 静默失败
        finally:
            self.recording = False
            
    def update_hotkey_display(self):
        """更新热键显示"""
        if self.hotkey:
            status = "已激活" if self.clicking_active else "未激活"
            self.hotkey_button.config(text=f"热键:{self.hotkey} {status}")
            
    def register_hotkey(self):
        """注册热键监听"""
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            self.update_hotkey_display()
            
        except Exception:
            # 静默失败，尝试备选方法
            self.try_alternative_hotkey_registration()
            
    def try_alternative_hotkey_registration(self):
        """尝试使用备选方法注册热键"""
        try:
            def on_key_event(e):
                if e.event_type == keyboard.KEY_DOWN and e.name == self.hotkey:
                    self.root.after(0, self.toggle_clicking)
            
            keyboard.hook_key(self.hotkey, on_key_event)
            
        except Exception:
            pass
            
    def toggle_clicking(self):
        """切换连点状态"""
        if not self.clicking_active:
            self.start_auto_click()
        else:
            self.stop_auto_click()
                
    def start_auto_click(self):
        """开始自动点击"""
        if not self.stop_clicking:
            return
            
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                interval = 1.0
        except:
            interval = 1.0
            
        self.click_interval = interval
        
        self.stop_clicking = False
        self.clicking_active = True
        
        self.update_hotkey_display()
        
        # 隐藏窗口
        if not self.window_hidden:
            self.hide_window()
        
        self.click_thread = threading.Thread(target=self.auto_click_loop, daemon=True)
        self.click_thread.start()
        
    def stop_auto_click(self):
        """停止自动点击"""
        self.stop_clicking = True
        self.clicking_active = False
        
        self.update_hotkey_display()
        
        # 显示窗口
        if self.window_hidden:
            self.show_window()
        
    def auto_click_loop(self):
        """自动点击循环"""
        mouse_controller = Controller()
        
        while not self.stop_clicking:
            try:
                mouse_controller.click(Button.left)
                time.sleep(self.click_interval)
            except Exception:
                break
    
    def hide_window(self):
        """隐藏窗口"""
        self.window_hidden = True
        self.root.withdraw()
        
    def show_window(self):
        """显示窗口"""
        self.window_hidden = False
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        
    def quit_app(self):
        """退出应用程序"""
        self.stop_auto_click()
        keyboard.unhook_all()
        self.root.quit()
        self.root.destroy()

def main():
    try:
        root = tk.Tk()
        app = HotkeyRecorder(root)
        root.mainloop()
    except Exception:
        pass

if __name__ == "__main__":
    main()