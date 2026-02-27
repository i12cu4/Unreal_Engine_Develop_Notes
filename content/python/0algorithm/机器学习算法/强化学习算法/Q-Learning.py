#q学习
import numpy as np
import matplotlib.pyplot as plt

# 定义环境参数
num_states = 6  # 状态数量
num_actions = 2  # 动作数量
q_table = np.zeros((num_states, num_actions))  # 初始化Q表

# 定义学习参数
learning_rate = 0.1  # 学习率
discount_factor = 0.9  # 折扣因子
exploration_prob = 0.2  # 探索概率
num_episodes = 1000  # 学习的剧集数量

# 定义环境动力学
def take_action(state):
    # 以一定概率随机选择动作
    if np.random.rand() < exploration_prob:
        return np.random.choice(num_actions)
    else:
        # 否则选择Q值最大的动作
        return np.argmax(q_table[state, :])

# Q-Learning算法
rewards = []  # 用于存储每集的学习奖励
for episode in range(num_episodes):
    state = 0  # 初始状态
    total_reward = 0  # 总奖励

    while state != num_states - 1:  # 只要未达到终止状态
        action = take_action(state)  # 选择一个动作
        next_state = min(state + action + np.random.randint(-1, 2), num_states - 1)  # 加入随机性
        reward = -1 if next_state != num_states - 1 else 0  # 终止状态的奖励为0
        total_reward += reward  # 累加奖励

        # 更新Q值
        q_table[state, action] = (1 - learning_rate) * q_table[state, action] + \
                                 learning_rate * (reward + discount_factor * np.max(q_table[next_state, :]))

        state = next_state  # 移动到下一个状态

    rewards.append(total_reward)  # 添加总奖励到奖励列表

    if episode % 100 == 0:  # 每百集打印一次
        print(f"Episode {episode}, Total Reward: {total_reward}")

# 绘制学习曲线
plt.plot(range(num_episodes), rewards)
plt.xlabel('Episodes')
plt.ylabel('Total Reward')
plt.title('Q-Learning Learning Curve')
plt.show()
