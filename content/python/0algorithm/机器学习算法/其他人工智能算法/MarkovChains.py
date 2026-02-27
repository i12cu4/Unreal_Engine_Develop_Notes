#马尔科夫链
import numpy as np
import matplotlib.pyplot as plt

# 定义状态转移概率矩阵（这里假设有3个状态）
transition_matrix = np.array([
    [0.4, 0.3, 0.3],
    [0.2, 0.4, 0.4],
    [0.1, 0.2, 0.7]
])

# 定义初始状态分布
initial_state = np.array([0.3, 0.4, 0.3])

# 进行状态转移
num_steps = 1000
state_history = [np.random.choice([0, 1, 2], p=initial_state)]

for _ in range(num_steps - 1):
    current_state = state_history[-1]
    next_state = np.random.choice([0, 1, 2], p=transition_matrix[current_state])
    state_history.append(next_state)

# 绘制状态转移过程
plt.figure(figsize=(8, 6))
plt.plot(state_history)
plt.xlabel('Time Step')
plt.ylabel('State')
plt.title('Markov Chain State Transitions')
plt.show()
