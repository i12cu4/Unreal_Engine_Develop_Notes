import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

try:
    import keyboard
except ImportError:
    print("正在安装 keyboard 库...")
    os.system("pip install keyboard")
    import keyboard

try:
    from pynput import mouse
    from pynput.mouse import Button, Listener as MouseListener
except ImportError:
    print("正在安装 pynput 库...")
    os.system("pip install pynput")
    from pynput import mouse
    from pynput.mouse import Button, Listener as MouseListener

class HotkeyRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("热键连点器")
        self.root.geometry("190x35")  # 进一步减小窗口尺寸
        self.root.resizable(False, False)
        
        # 设置窗口始终置顶
        self.root.attributes('-topmost', True)
        
        # 热键相关变量 - 默认设置为F1
        self.hotkey = "f1"
        self.recording = False
        
        # 鼠标连点相关变量
        self.click_interval = 1.0  # 默认1秒
        self.click_thread = None
        self.stop_clicking = True
        self.clicking_active = False
        
        self.setup_ui()
        self.make_draggable()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # 自动注册默认热键
        self.register_hotkey()
        
    def make_draggable(self):
        """使窗口可拖动 - 绑定到整个窗口"""
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
            
        # 绑定整个窗口
        self.root.bind("<ButtonPress-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建小字体
        small_font = ("Arial", 8)
        
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 第一行：热键按钮和间隔设置
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)
        
        # 热键按钮 - 整合设置和状态显示
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
        self.interval_var = tk.StringVar(value="1.0")  # 默认1秒
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=4, font=small_font)
        self.interval_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(interval_frame, text="秒", font=small_font).pack(side=tk.LEFT)
            
    def start_recording(self):
        """开始录制热键"""
        if self.recording:
            return
            
        self.recording = True
        self.hotkey_button.config(text="按下热键...")
        
        # 在新线程中录制热键
        threading.Thread(target=self.record_hotkey, daemon=True).start()
        
    def record_hotkey(self):
        """录制热键的线程函数"""
        try:
            # 清除之前的按键缓冲区
            keyboard.unhook_all()
            
            # 等待按键
            print("等待按键...")
            event = keyboard.read_event(suppress=False)
            
            if event.event_type == keyboard.KEY_DOWN:
                # 获取按键名称
                key_name = event.name
                self.hotkey = key_name
                
                # 更新UI
                self.root.after(0, self.update_hotkey_display)
                
                # 注册热键
                self.register_hotkey()
                
        except Exception as e:
            print(f"录制热键时出错: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"录制热键时出错: {e}"))
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
            # 先移除之前的热键
            keyboard.unhook_all()
            
            # 注册新热键
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            print(f"已注册全局热键: {self.hotkey}")
            
            # 更新按钮显示
            self.update_hotkey_display()
            
        except Exception as e:
            print(f"注册热键失败: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"注册热键失败: {e}"))
            
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
            
        # 获取间隔时间
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                interval = 1.0
        except:
            interval = 1.0
            
        self.click_interval = interval
        
        self.stop_clicking = False
        self.clicking_active = True
        
        # 更新按钮显示
        self.update_hotkey_display()
        
        self.click_thread = threading.Thread(target=self.auto_click_loop, daemon=True)
        self.click_thread.start()
        
        print("开始自动点击")
        
    def stop_auto_click(self):
        """停止自动点击"""
        self.stop_clicking = True
        self.clicking_active = False
        
        # 更新按钮显示
        self.update_hotkey_display()
        
        print("停止自动点击")
        
    def auto_click_loop(self):
        """自动点击循环 - 只点击左键"""
        mouse_controller = mouse.Controller()
        
        while not self.stop_clicking:
            try:
                # 只点击鼠标左键
                mouse_controller.click(Button.left)
                time.sleep(self.click_interval)
                
            except Exception as e:
                print(f"自动点击错误: {e}")
                break
                
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
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()x