```
from tqdm import tqdm
import time

# 模拟一个耗时任务
for i in tqdm(range(100), desc="Processing"):
    # 每次循环执行任务（例如处理数据、下载等）
    time.sleep(0.05)  # 模拟耗时操作
```