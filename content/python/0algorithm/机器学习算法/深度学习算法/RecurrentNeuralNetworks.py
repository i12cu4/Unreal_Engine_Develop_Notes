import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt

# 生成随机数据
def generate_data(length=100, n_samples=100):
    data = np.zeros((n_samples, length, 1))
    targets = np.zeros((n_samples, length, 1))
    for i in range(n_samples):
        for t in range(length):
            data[i, t, 0] = np.sin(0.1 * t) + np.random.normal(0, 0.1)
            # 目标值是输入值的下一个时间步
            if t < length - 1:
                targets[i, t, 0] = data[i, t + 1, 0]
            else:
                # 对于序列的最后一个时间步，我们可以使用输入值作为目标值
                targets[i, t, 0] = data[i, t, 0]
    return data, targets

# 定义RNN模型
def create_rnn_model(input_shape):
    model = Sequential([
        LSTM(50, activation='relu', input_shape=input_shape),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# 训练模型
def train_rnn(model, data, epochs=100):
    history = model.fit(data[0], data[1], epochs=epochs, batch_size=1)
    return history

# 绘制结果
def plot_rnn_results(history):
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('MSE')
    plt.legend()
    plt.show()

# 主函数
def main():
    data, targets = generate_data()
    model = create_rnn_model((None, 1))
    history = train_rnn(model, (data, targets))
    plot_rnn_results(history)

if __name__ == '__main__':
    main()
