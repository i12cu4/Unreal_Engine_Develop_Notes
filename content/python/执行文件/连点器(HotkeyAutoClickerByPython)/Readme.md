# Hotkey Auto Clicker

## 描述 / Description

一个简洁的全局热键连点器，通过热键控制鼠标自动点击。  
A compact global hotkey auto-clicker for automated mouse clicking.

## 功能特性 / Features

- ⌨️ **全局热键** - 默认F1键，可自定义
- 🖱️ **自动点击** - 模拟鼠标左键点击
- ⏱️ **可调间隔** - 自定义点击频率
- 🪟 **迷你窗口** - 小巧置顶，不占空间
- 🎯 **拖拽移动** - 可随意拖动窗口位置

## 使用方法 / Usage

### 启动程序
```bash
python main.py
```

### 基本操作
1. **设置热键**：点击"热键"按钮，按下新按键
2. **设置间隔**：输入点击间隔时间（秒）
3. **开始/停止**：按热键切换连点状态
4. **移动窗口**：拖动窗口任意位置

### 默认设置
- **热键**：F1
- **间隔**：1.0秒
- **点击**：鼠标左键

## 技术需求 / Requirements

- Python 3.6+
- 自动安装依赖：
  - `keyboard` - 全局热键监听
  - `pynput` - 鼠标控制

## 注意事项 / Notes

- 可能需要管理员权限
- 热键全局生效，即使窗口不在焦点
- 关闭程序自动停止连点

---

**提示**：适用于游戏、测试等需要重复点击的场景。  
**Tip**: Suitable for gaming, testing, and other scenarios requiring repeated clicks.