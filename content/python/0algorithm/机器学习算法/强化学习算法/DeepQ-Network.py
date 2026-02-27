#深度Q网络
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from collections import deque
import random  # 确保导入random
# 创建一个简单的深度Q网络模型
class DQN:
    def __init__(self, state_size, action_size):
        self.state_size = state_size  # 状态的大小
        self.action_size = action_size  # 动作的数量
        self.memory = deque(maxlen=2000)  # 经验回放记忆，最大容量为2000
        self.gamma = 0.95    # 折扣率，用于计算未来奖励的现值
        self.epsilon = 1.0  # 探索率，用于平衡探索和利用
        self.epsilon_min = 0.01  # 探索率的最小值
        self.epsilon_decay = 0.995  # 探索率的衰减率
        self.learning_rate = 0.001  # 学习率
        self.model = self._build_model()  # 构建模型

    def _build_model(self):
        model = Sequential()  # 初始化一个序贯模型
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))  # 添加一个有24个神经元的全连接层，使用ReLU激活函数
        model.add(Dense(24, activation='relu'))  # 添加第二个有24个神经元的全连接层，使用ReLU激活函数
        model.add(Dense(self.action_size, activation='linear'))  # 添加输出层，神经元数量等于动作数量，使用线性激活函数
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))  # 编译模型，使用均方误差损失函数和Adam优化器
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # 将经历添加到记忆中

    def act(self, state):
        if np.random.rand() <= self.epsilon:  # 如果随机数小于等于探索率，则随机选择一个动作
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)  # 否则，根据模型预测的动作值选择动作
        return np.argmax(act_values[0])  # 返回预测值最大的动作索引

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)  # 从记忆中随机抽取一个小批量
        for state, action, reward, next_state, done in minibatch:
            target = reward  # 初始目标值为即时奖励
            if not done:  # 如果经历不是终端状态
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))  # 计算目标值，包括即时奖励和未来奖励的最大值
            target_f = self.model.predict(state)  # 预测状态的目标值
            target_f[0][action] = target  # 更新目标值
            self.model.fit(state, target_f, epochs=1, verbose=0)  # 使用目标值训练模型
        if self.epsilon > self.epsilon_min:  # 如果当前探索率大于最小探索率
            self.epsilon *= self.epsilon_decay  # 更新探索率

# 假设我们有一个环境，状态大小为8，动作大小为4
state_size = 8
action_size = 4

# 初始化DQN
dqn = DQN(state_size, action_size)

# 假设我们有一个状态
state = np.random.rand(1, state_size)  # 确保状态是二维的，添加一个批处理维度

# 让模型选择一个动作
action = dqn.act(state)

# 假设我们得到了下一个状态和奖励
next_state = np.random.rand(1, state_size)  # 确保下一个状态也是二维的
reward = 0.5

# 记住这个经历
dqn.remember(state, action, reward, next_state, False)

# 进行经验回放
dqn.replay(1)

