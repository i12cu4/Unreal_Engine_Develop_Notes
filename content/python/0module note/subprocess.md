# 模块定位

subprocess 是 Python 标准库中用于 创建和管理子进程 的核心模块，提供对操作系统进程的直接控制能力。

它取代了旧版 os.system 和 os.popen 等函数，是跨平台进程交互的标准化解决方案。

---

# 核心方法

模块通过以下关键方法实现进程管理：

## subprocess.run()

功能：执行命令并等待完成（同步操作）

参数：
```python
subprocess.run(args, *, 
              stdin=None, input=None, 
              stdout=None, stderr=None, 
              capture_output=False, 
              shell=False, 
              cwd=None, 
              timeout=None, 
              check=False, 
              encoding=None, 
              errors=None)
```
返回值：返回 CompletedProcess 对象，包含：

returncode：进程退出码

stdout：标准输出内容

stderr：标准错误内容

---

## subprocess.Popen()

功能：创建异步进程对象（底层控制）

参数：与 run() 类似，但提供更细粒度的控制

返回值：Popen 对象，支持：

poll()：检查进程状态

wait()：等待进程结束

communicate()：交互式输入输出

terminate()：发送终止信号

---

# 参数解析

| 参数     | 类型      | 作用域   | 功能说明                                                          |
| -------- | --------- | -------- | ----------------------------------------------------------------- |
| args     | list/str  | 必选     | 命令参数（推荐使用列表形式避免注入风险）                          |
| stdin    | file/pipe | 输入控制 | 指定标准输入源（默认继承父进程）                                  |
| stdout   | file/pipe | 输出控制 | 重定向标准输出（可用 subprocess.PIPE 捕获）                       |
| stderr   | file/pipe | 错误控制 | 重定向标准错误（可合并到 stdout 使用 STDOUT）                     |
| shell    | bool      | 执行模式 | 是否通过系统 shell 执行命令（默认 False，存在安全风险需谨慎使用） |
| cwd      | str       | 工作目录 | 指定子进程的工作目录                                              |
| timeout  | int/float | 超时控制 | 设置命令执行超时时间（秒）                                        |
| check    | bool      | 异常处理 | 若为 True，返回码非零时抛出 CalledProcessError                    |
| encoding | str       | 编解码   | 指定输入输出的字符编码（如 'utf-8'）                              |

---

# 工作原理

## 进程创建：

通过系统调用（如 Unix 的 fork() + execvp()，Windows 的 CreateProcess()）创建子进程

维护父子进程间的文件描述符映射

## 通信机制：

使用管道（pipe）实现标准输入/输出/错误流的重定向

支持同步/异步操作模式

提供内存缓冲区管理（预防死锁）

## 状态管理：

跟踪进程 PID

监控退出状态码

处理信号中断（如 Ctrl+C）