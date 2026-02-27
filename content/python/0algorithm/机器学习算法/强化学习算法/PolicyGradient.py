#策略梯度
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# 定义策略梯度类
class PolicyGradient:
    def __init__(self, state_size, action_size, learning_rate):
        # 初始化状态大小和动作大小
        self.state_size = state_size
        self.action_size = action_size
        # 存储学习率作为属性
        self.learning_rate = learning_rate
        # 构建模型
        self.model = self._build_model()
        # 设置折扣率
        self.gamma = 0.95
        # 设置探索率
        self.epsilon = 1.0
        # 设置最小探索率和探索率衰减系数
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def _build_model(self):
        # 创建一个序贯模型
        model = Sequential()
        # 添加一个全连接层，使用ReLU激活函数
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        # 添加第二个全连接层，使用ReLU激活函数
        model.add(Dense(24, activation='relu'))
        # 添加输出层，使用softmax激活函数输出概率分布
        model.add(Dense(self.action_size, activation='softmax'))
        # 编译模型，使用交叉熵损失函数和Adam优化器
        model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def act(self, state):
        # 如果随机数小于探索率，则随机选择一个动作
        if np.random.rand() <= self.epsilon:
            return np.random.randint(self.action_size)
        else:
            # 否则，根据模型预测的概率分布选择动作
            probs = self.model.predict(state)
            return np.argmax(probs[0])

    def train(self, state, action, reward, next_state, done):
        # 设置目标回报
        target = reward
        # 如果不是终止状态，则计算包含折扣的期望回报
        if not done:
            target = reward + self.gamma * np.max(self.model.predict(next_state)[0])
        # 更新模型，使用目标函数计算损失
        target_f = self.model.predict(state)
        target_f[0][action] = target
        self.model.fit(state, target_f, epochs=1, verbose=0)
        # 如果探索率大于最小探索率，则更新探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# 设置状态大小和动作大小
state_size = 8
action_size = 4

# 初始化策略梯度模型，传入状态大小、动作大小和学习率
pg = PolicyGradient(state_size, action_size, learning_rate=0.001)

# 创建一个随机状态
state = np.random.rand(1, state_size)

# 让模型选择一个动作
action = pg.act(state)

# 创建下一个随机状态和奖励
next_state = np.random.rand(1, state_size)
reward = 0.5

# 训练模型，传入当前状态、动作、奖励、下一个状态和是否完成标志
pg.train(state, action, reward, next_state, False)
